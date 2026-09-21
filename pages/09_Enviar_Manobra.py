import uuid, json, time
from urllib.parse import urlparse
import streamlit as st
import streamlit.components.v1 as components
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme

st.set_page_config(page_title="Enviar Vídeo • Skate Performance", page_icon="🎥", layout="wide")
apply_ui_theme(); user, profile = require_login(); sb = get_supabase()
role = profile.get("role")
STAFF = {"admin","tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica"}
ALLOWED = STAFF | {"skatista"}
MAX_GB = 2

st.title("🎥 Enviar vídeo para análise")
st.caption("Envie o vídeo do treino. Quando terminar, ele ficará disponível no feed e na análise do atleta.")
if role not in ALLOWED:
    st.info("Envio disponível para atletas e equipe técnica."); st.stop()

target_id = user.id
if role in STAFF:
    athletes = sb.table("profiles").select("id,full_name,status").eq("role","skatista").eq("status","ativo").order("full_name").execute().data or []
    amap = {a["full_name"]: a["id"] for a in athletes}
    if not amap: st.warning("Não há atletas ativos cadastrados."); st.stop()
    target_name = st.selectbox("Atleta do vídeo", list(amap)); target_id = amap[target_name]

mode = st.radio("Tipo de vídeo", ["Sessão completa", "Tentativa isolada"], horizontal=True,
                help="Use Sessão completa para um treino com várias tentativas/manobras.")
try:
    cats = sb.table("trick_categories").select("*").order("sort_order").execute().data or []
    tricks = sb.table("tricks").select("*").eq("active",True).order("name").execute().data or []
except Exception as e:
    st.error(f"Livro de Manobras indisponível. Detalhes: {e}"); st.stop()

trick_id = None
if mode == "Tentativa isolada":
    if not tricks: st.warning("O Livro de Manobras ainda está vazio."); st.stop()
    cmap = {c["name"]: c["id"] for c in cats}; cat = st.selectbox("Categoria", list(cmap))
    available = [t for t in tricks if t.get("category_id") == cmap[cat]]
    tmap = {t["name"]: t["id"] for t in available}
    trick = st.selectbox("Manobra", list(tmap)) if tmap else None
    trick_id = tmap.get(trick) if trick else None
    title = st.text_input("Título", placeholder="Ex.: Flip Crooked no corrimão")
else:
    title = st.text_input("Nome da sessão", placeholder="Ex.: Treino Street • tarde • 20/09")
caption = st.text_area("Observação", placeholder="Contexto do treino, objetivo, observações para a comissão técnica…", height=80)

if mode == "Tentativa isolada" and not trick_id:
    st.warning("Escolha uma manobra para liberar o envio."); st.stop()

# O navegador precisa do JWT REAL da sessão autenticada. A publishable key sozinha
# não representa o usuário e não deve ser usada como Bearer para o TUS.
try:
    auth_session = sb.auth.get_session()
    if not auth_session or not getattr(auth_session, "access_token", None):
        auth_session = st.session_state.get("sp_session")
    access_token = getattr(auth_session, "access_token", None)
    if not access_token:
        raise RuntimeError("sessão sem access token")
except Exception:
    st.error("Sua sessão expirou. Saia e entre novamente para enviar o vídeo.")
    st.stop()

supabase_url = st.secrets.get("SUPABASE_URL", "")
publishable_key = st.secrets.get("SUPABASE_KEY", "")
project_id = urlparse(supabase_url).hostname.split(".")[0]
endpoint = f"https://{project_id}.storage.supabase.co/storage/v1/upload/resumable"
path = f"{target_id}/{uuid.uuid4().hex}.mp4"

payload = {
    "athlete_id": target_id,
    "trick_id": trick_id,
    "video_path": path,
    "caption": caption.strip() or None,
    "upload_kind": "session" if mode == "Sessão completa" else "single",
    "session_title": title.strip() or ("Sessão de treino" if mode == "Sessão completa" else None),
}

cfg = {
    "endpoint": endpoint,
    "rest": supabase_url.rstrip("/") + "/rest/v1/athlete_posts",
    "access": access_token,
    "apikey": publishable_key,
    "path": path,
    "payload": payload,
    "max": MAX_GB * 1024 * 1024 * 1024,
}

uploader = '''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/tus-js-client@4.3.1/dist/tus.min.js"></script>
<style>
*{box-sizing:border-box}body{margin:0;background:transparent;color:#f5f8fc;font-family:Inter,Arial,sans-serif}.box{border:1px solid #163b59;border-radius:14px;padding:18px;background:#081b2d}.pick{display:flex;align-items:center;justify-content:center;width:100%;min-height:54px;border:1px solid #159bff;border-radius:10px;background:linear-gradient(180deg,#087cff,#006fe8);color:#fff;font-weight:800;cursor:pointer;box-shadow:0 0 18px rgba(0,124,255,.18)}.pick:hover{filter:brightness(1.08)}#file{display:none}.name{margin-top:10px;color:#9fb3c8;font-size:13px;text-align:center}.track{height:10px;background:#10263b;border-radius:99px;overflow:hidden;margin-top:14px;display:none}.bar{height:100%;width:0;background:linear-gradient(90deg,#087cff,#00d9ff);transition:width .2s}.status{margin-top:10px;color:#c4d1df;font-size:14px;text-align:center;min-height:22px}.ok{color:#00e4a4;font-weight:800}.err{color:#ff6b6b;font-weight:700}
</style></head><body><div class="box">
<label class="pick" for="file">＋ ANEXAR E ENVIAR VÍDEO</label><input id="file" type="file" accept="video/mp4,video/quicktime,video/webm,video/x-m4v"><div class="name" id="name">Selecione o vídeo do treino</div><div class="track" id="track"><div class="bar" id="bar"></div></div><div class="status" id="status"></div></div>
<script>
const C=__CFG__; const fileEl=document.getElementById('file'), nameEl=document.getElementById('name'), track=document.getElementById('track'), bar=document.getElementById('bar'), status=document.getElementById('status'), pick=document.querySelector('.pick');
function fail(msg){status.className='status err';status.textContent=msg;pick.style.pointerEvents='auto';pick.style.opacity='1'}
fileEl.addEventListener('change', async()=>{const file=fileEl.files[0]; if(!file)return; if(file.size>C.max){fail('Arquivo acima do limite configurado.');return;} nameEl.textContent=file.name+' • '+(file.size/1024/1024).toFixed(1)+' MB';track.style.display='block';pick.style.pointerEvents='none';pick.style.opacity='.55';status.className='status';status.textContent='Preparando envio…';
 const upload=new tus.Upload(file,{endpoint:C.endpoint,retryDelays:[0,3000,5000,10000,20000],headers:{authorization:'Bearer '+C.access,apikey:C.apikey},uploadDataDuringCreation:true,removeFingerprintOnSuccess:true,chunkSize:6*1024*1024,metadata:{bucketName:'trick-videos',objectName:C.path,contentType:file.type||'video/mp4',cacheControl:'3600'},onError:(e)=>fail('Não foi possível enviar o vídeo. '+(e && e.message ? e.message : e)),onProgress:(u,t)=>{const p=(u/t*100).toFixed(1);bar.style.width=p+'%';status.textContent='Enviando… '+p+'% • '+(u/1024/1024).toFixed(0)+' / '+(t/1024/1024).toFixed(0)+' MB'},onSuccess:async()=>{bar.style.width='100%';status.textContent='Salvando vídeo no perfil…';try{const r=await fetch(C.rest,{method:'POST',headers:{apikey:C.apikey,authorization:'Bearer '+C.access,'Content-Type':'application/json',Prefer:'return=minimal'},body:JSON.stringify(C.payload)});if(!r.ok){const tx=await r.text();throw new Error('Upload concluído, mas não foi possível vincular ao perfil: '+r.status+' '+tx)}status.className='status ok';status.textContent='✓ Vídeo enviado com sucesso. Já está disponível no feed e na análise.';nameEl.textContent=file.name;pick.textContent='✓ ENVIO CONCLUÍDO';}catch(e){fail(e.message||String(e))}}});
 try{const prev=await upload.findPreviousUploads();if(prev.length)upload.resumeFromPreviousUpload(prev[0]);upload.start()}catch(e){fail(e.message||String(e))}});
</script></body></html>'''.replace('__CFG__', json.dumps(cfg))
components.html(uploader, height=205)

st.caption("Para vídeos de sessão completa, depois do envio abra Análise → Codificação de Vídeo para marcar as tentativas durante o treino.")
