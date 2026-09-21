import uuid, json
import streamlit as st
import streamlit.components.v1 as components
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme
from drive_utils import get_drive_access_token, get_drive_folder_id

st.set_page_config(page_title="Enviar Vídeo • Skate Performance", page_icon="🎥", layout="wide")
apply_ui_theme(); user, profile = require_login(); sb = get_supabase()
role = profile.get("role")
STAFF = {"admin","tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica"}
ALLOWED = STAFF | {"skatista"}
MAX_GB = 10

st.title("🎥 Enviar vídeo para análise")
st.caption("Escolha o vídeo do treino. O envio começa automaticamente e, ao terminar, ele fica disponível no feed e na análise.")
if role not in ALLOWED:
    st.info("Envio disponível para atletas e equipe técnica."); st.stop()

target_id = user.id
target_name = profile.get('full_name') or 'Atleta'
if role in STAFF:
    athletes = sb.table("profiles").select("id,full_name,status").eq("role","skatista").eq("status","ativo").order("full_name").execute().data or []
    amap = {a["full_name"]: a["id"] for a in athletes}
    if not amap: st.warning("Não há atletas ativos cadastrados."); st.stop()
    target_name = st.selectbox("Atleta do vídeo", list(amap)); target_id = amap[target_name]

mode = st.radio("Tipo de vídeo", ["Sessão completa", "Tentativa isolada"], horizontal=True,
                help="Sessão completa = um treino com várias tentativas e manobras.")
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
    title = st.text_input("Nome da sessão", placeholder="Ex.: Treino Street • tarde • 21/09")
caption = st.text_area("Observação", placeholder="Contexto do treino, objetivo, observações para a comissão técnica…", height=80)
if mode == "Tentativa isolada" and not trick_id:
    st.warning("Escolha uma manobra para liberar o envio."); st.stop()

try:
    drive_token = get_drive_access_token()
    folder_id = get_drive_folder_id()
except Exception as e:
    st.error("Google Drive ainda não está configurado para o portal. Confira os Secrets do Streamlit.")
    st.caption(str(e)); st.stop()

try:
    auth_session = sb.auth.get_session()
    access_token = getattr(auth_session, "access_token", None)
    if not access_token: raise RuntimeError("sessão sem token")
except Exception:
    st.error("Sua sessão expirou. Saia e entre novamente para enviar o vídeo."); st.stop()

supabase_url = st.secrets.get("SUPABASE_URL", "").rstrip('/')
publishable_key = st.secrets.get("SUPABASE_KEY", "")
payload = {
    "athlete_id": target_id, "trick_id": trick_id, "caption": caption.strip() or None,
    "upload_kind": "session" if mode == "Sessão completa" else "single",
    "session_title": title.strip() or ("Sessão de treino" if mode == "Sessão completa" else None),
}
cfg = {"driveToken":drive_token,"folder":folder_id,"rest":supabase_url+"/rest/v1/athlete_posts",
       "sbToken":access_token,"apikey":publishable_key,"payload":payload,"athlete":target_name,
       "max":MAX_GB*1024*1024*1024}

uploader = r'''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{box-sizing:border-box}body{margin:0;background:transparent;color:#10263b;font-family:Inter,Arial,sans-serif}.box{border:1px solid #d9e7f2;border-radius:16px;padding:18px;background:#ffffff;box-shadow:0 10px 28px rgba(31,78,116,.07)}.pick{display:flex;align-items:center;justify-content:center;width:100%;min-height:56px;border:1px solid #159bff;border-radius:10px;background:linear-gradient(180deg,#087cff,#006fe8);color:#fff;font-weight:900;cursor:pointer;box-shadow:0 0 18px rgba(0,124,255,.18)}#file{display:none}.name{margin-top:10px;color:#71879b;font-size:13px;text-align:center}.track{height:10px;background:#eaf2f8;border-radius:99px;overflow:hidden;margin-top:14px;display:none}.bar{height:100%;width:0;background:linear-gradient(90deg,#087cff,#00d9ff);transition:width .15s}.status{margin-top:10px;color:#526b80;font-size:14px;text-align:center;min-height:22px}.ok{color:#00e4a4;font-weight:800}.err{color:#ff6b6b;font-weight:700}
</style></head><body><div class="box"><label class="pick" for="file">＋ ANEXAR VÍDEO</label><input id="file" type="file" accept="video/*"><div class="name" id="name">Selecione o vídeo do treino</div><div class="track" id="track"><div class="bar" id="bar"></div></div><div class="status" id="status"></div></div><script>
const C=__CFG__, f=document.getElementById('file'), nm=document.getElementById('name'), tr=document.getElementById('track'), bar=document.getElementById('bar'), stt=document.getElementById('status'), pick=document.querySelector('.pick');
function fail(m){stt.className='status err';stt.textContent=m;pick.style.pointerEvents='auto';pick.style.opacity='1'}
async function start(file){
 if(file.size>C.max){fail('Este vídeo ultrapassa o limite configurado no portal.');return}
 nm.textContent=file.name+' • '+(file.size/1024/1024).toFixed(1)+' MB'; tr.style.display='block'; pick.style.pointerEvents='none';pick.style.opacity='.55';stt.textContent='Preparando envio…';
 const meta={name:file.name,parents:[C.folder],description:'Skate Performance • '+C.athlete};
 let init=await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true',{method:'POST',headers:{Authorization:'Bearer '+C.driveToken,'Content-Type':'application/json; charset=UTF-8','X-Upload-Content-Type':file.type||'video/mp4','X-Upload-Content-Length':String(file.size)},body:JSON.stringify(meta)});
 if(!init.ok)throw new Error('Drive '+init.status+': '+await init.text());
 const loc=init.headers.get('Location'); if(!loc)throw new Error('O Google Drive não retornou a sessão de upload.');
 const chunk=8*1024*1024; let pos=0, fileId=null;
 while(pos<file.size){let end=Math.min(pos+chunk,file.size);let blob=file.slice(pos,end);let r=await fetch(loc,{method:'PUT',headers:{'Content-Length':String(end-pos),'Content-Range':'bytes '+pos+'-'+(end-1)+'/'+file.size},body:blob});
   if(!(r.status===308||r.ok))throw new Error('Drive '+r.status+': '+await r.text()); pos=end;let p=(pos/file.size*100);bar.style.width=p.toFixed(1)+'%';stt.textContent='Enviando… '+p.toFixed(1)+'% • '+(pos/1024/1024).toFixed(0)+' / '+(file.size/1024/1024).toFixed(0)+' MB';
   if(r.ok){let d=await r.json();fileId=d.id;}
 }
 if(!fileId)throw new Error('Upload terminou sem retornar o ID do vídeo.');
 // O feed usa player HTML5. Publicamos somente este arquivo como "qualquer pessoa com o link";
 // o Drive inteiro continua privado e o ID não é listado publicamente.
 let perm=await fetch('https://www.googleapis.com/drive/v3/files/'+fileId+'/permissions?supportsAllDrives=true',{method:'POST',headers:{Authorization:'Bearer '+C.driveToken,'Content-Type':'application/json'},body:JSON.stringify({role:'reader',type:'anyone',allowFileDiscovery:false})});
 if(!perm.ok)throw new Error('Vídeo enviado, mas o Drive não permitiu liberar a reprodução no feed: '+perm.status+' '+await perm.text());
 stt.textContent='Salvando vídeo no perfil…'; let pay=Object.assign({},C.payload,{video_path:'gdrive:'+fileId});
 let sr=await fetch(C.rest,{method:'POST',headers:{apikey:C.apikey,authorization:'Bearer '+C.sbToken,'Content-Type':'application/json',Prefer:'return=minimal'},body:JSON.stringify(pay)});
 if(!sr.ok)throw new Error('Vídeo enviado, mas não foi possível vinculá-lo ao perfil: '+sr.status+' '+await sr.text());
 bar.style.width='100%';stt.className='status ok';stt.textContent='✓ Vídeo enviado com sucesso. Já está disponível no feed e na análise.';pick.textContent='✓ ENVIO CONCLUÍDO';
}
f.addEventListener('change',()=>{let file=f.files[0];if(file)start(file).catch(e=>fail('Não foi possível enviar o vídeo. '+(e.message||e)))})
</script></body></html>'''.replace('__CFG__',json.dumps(cfg))
components.html(uploader,height=205)
st.caption("Sessões completas podem ser codificadas em Análise → Codificação de Vídeo.")
