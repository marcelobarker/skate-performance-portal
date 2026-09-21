import uuid, html, json
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
st.caption("Upload direto e retomável: o vídeo vai do seu aparelho para o Storage, sem passar pelo servidor do Streamlit.")
if role not in ALLOWED:
    st.info("Envio disponível para atletas e equipe técnica."); st.stop()

target_id = user.id
if role in STAFF:
    athletes = sb.table("profiles").select("id,full_name,status").eq("role","skatista").eq("status","ativo").order("full_name").execute().data or []
    amap = {a["full_name"]: a["id"] for a in athletes}
    if not amap: st.warning("Não há atletas ativos cadastrados."); st.stop()
    target_name = st.selectbox("Atleta do vídeo", list(amap)); target_id = amap[target_name]

mode = st.radio("Tipo de envio", ["Sessão completa", "Tentativa isolada"], horizontal=True,
                help="Sessão completa é ideal para vídeos longos de treino com várias tentativas/manobras.")
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

# Signed token is created server-side. The browser then uploads directly with TUS.
meta_sig = (target_id, mode, trick_id, title, caption)
if st.session_state.get("direct_upload_meta") != meta_sig:
    for k in ("direct_upload_path","direct_upload_token","direct_upload_meta"):
        st.session_state.pop(k, None)

if st.button("Preparar upload grande", type="primary", width="stretch"):
    if mode == "Tentativa isolada" and not trick_id:
        st.warning("Escolha uma manobra primeiro.")
    else:
        path = f"{target_id}/{uuid.uuid4().hex}.mp4"
        try:
            signed = sb.storage.from_("trick-videos").create_signed_upload_url(path)
            if hasattr(signed, "model_dump"): signed = signed.model_dump()
            if hasattr(signed, "dict"): signed = signed.dict()
            token = None
            if isinstance(signed, dict):
                token = signed.get("token") or signed.get("signedURL") or signed.get("signed_url")
                if isinstance(token, str) and "token=" in token:
                    token = token.split("token=",1)[1].split("&",1)[0]
            if not token:
                raise RuntimeError(f"Token de upload não retornado pelo Storage: {signed}")
            st.session_state["direct_upload_path"] = path
            st.session_state["direct_upload_token"] = token
            st.session_state["direct_upload_meta"] = meta_sig
            st.rerun()
        except Exception as e:
            st.error(f"Não foi possível preparar o upload direto. Detalhes: {e}")

path = st.session_state.get("direct_upload_path")
token = st.session_state.get("direct_upload_token")
if path and token:
    supabase_url = st.secrets.get("SUPABASE_URL", "")
    project_id = urlparse(supabase_url).hostname.split(".")[0]
    endpoint = f"https://{project_id}.storage.supabase.co/storage/v1/upload/resumable"
    safe_path = json.dumps(path)
    safe_token = json.dumps(token)
    safe_endpoint = json.dumps(endpoint)
    uploader = f'''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/tus-js-client@4.3.1/dist/tus.min.js"></script>
<style>body{{margin:0;background:#061727;color:#f5f8fc;font-family:Inter,Arial,sans-serif}}.box{{border:1px solid #163b59;border-radius:12px;padding:18px;background:#081b2d}}input{{width:100%;box-sizing:border-box;padding:13px;border:1px dashed #29a8ff;border-radius:9px;background:#061727;color:#c4d1df}}button{{margin-top:12px;width:100%;padding:13px;border:0;border-radius:9px;background:#087cff;color:white;font-weight:800;cursor:pointer}}button:disabled{{opacity:.45}}.track{{height:12px;background:#10263b;border-radius:99px;overflow:hidden;margin-top:14px}}.bar{{height:100%;width:0;background:linear-gradient(90deg,#087cff,#00d9ff);transition:width .2s}}#status{{margin-top:10px;color:#c4d1df;font-size:14px}}</style></head><body><div class="box">
<input id="file" type="file" accept="video/mp4,video/quicktime,video/webm,video/x-m4v"><button id="go">ENVIAR VÍDEO DIRETO</button><div class="track"><div class="bar" id="bar"></div></div><div id="status">Escolha um vídeo. Limite do portal: {MAX_GB} GB.</div></div>
<script>
const PATH={safe_path}, TOKEN={safe_token}, ENDPOINT={safe_endpoint}, MAX={MAX_GB}*1024*1024*1024;
const fileEl=document.getElementById('file'), btn=document.getElementById('go'), bar=document.getElementById('bar'), status=document.getElementById('status');
btn.onclick=async()=>{{ const file=fileEl.files[0]; if(!file){{status.textContent='Escolha um vídeo primeiro.';return}} if(file.size>MAX){{status.textContent='Arquivo acima de {MAX_GB} GB.';return}} btn.disabled=true; status.textContent='Preparando '+file.name+' ('+(file.size/1024/1024).toFixed(1)+' MB)…';
 const upload=new tus.Upload(file,{{endpoint:ENDPOINT,retryDelays:[0,3000,5000,10000,20000],headers:{{'x-signature':TOKEN}},uploadDataDuringCreation:true,removeFingerprintOnSuccess:true,chunkSize:6*1024*1024,metadata:{{bucketName:'trick-videos',objectName:PATH,contentType:file.type||'video/mp4',cacheControl:'3600'}},onError:(e)=>{{status.textContent='Erro no upload: '+e;btn.disabled=false}},onProgress:(u,t)=>{{const p=(u/t*100).toFixed(1);bar.style.width=p+'%';status.textContent='Enviando… '+p+'% • '+(u/1024/1024).toFixed(0)+' / '+(t/1024/1024).toFixed(0)+' MB'}},onSuccess:()=>{{bar.style.width='100%';status.innerHTML='<b>Upload concluído ✓</b> Agora clique em FINALIZAR ENVIO abaixo.';btn.textContent='CONCLUÍDO ✓'}}}});
 const prev=await upload.findPreviousUploads(); if(prev.length) upload.resumeFromPreviousUpload(prev[0]); upload.start(); }};
</script></body></html>'''
    components.html(uploader, height=190)
    st.caption("O upload é enviado em blocos de 6 MB e pode retomar após uma interrupção. Mantenha esta página aberta até chegar a 100%.")

    if st.button("FINALIZAR ENVIO", width="stretch"):
        try:
            folder, filename = path.rsplit("/",1)
            objs = sb.storage.from_("trick-videos").list(folder, {"search": filename, "limit": 10})
            found = any((o.get("name") if isinstance(o,dict) else getattr(o,"name",None)) == filename for o in (objs or []))
            if not found:
                st.warning("O arquivo ainda não apareceu no Storage. Espere o upload chegar a 100% e tente FINALIZAR novamente.")
            else:
                payload={"athlete_id":target_id,"trick_id":trick_id,"video_path":path,"caption":caption.strip() or None,"upload_kind":"session" if mode=="Sessão completa" else "single","session_title":title.strip() or ("Sessão de treino" if mode=="Sessão completa" else None)}
                sb.table("athlete_posts").insert(payload).execute()
                for k in ("direct_upload_path","direct_upload_token","direct_upload_meta"): st.session_state.pop(k,None)
                st.success("Vídeo enviado e vinculado ao atleta. Já está pronto para o feed e para codificação.")
                st.session_state["selected_athlete_id"] = target_id
                st.switch_page("pages/07_Perfil_do_Atleta.py")
        except Exception as e:
            st.error(f"Não foi possível finalizar o envio. Detalhes: {e}")

st.info("Upload grande usa TUS resumível e vai direto do navegador para o Supabase Storage. Isso evita o limite de 200 MB do file_uploader do Streamlit. O limite final ainda depende do plano/limite global configurado no seu projeto Supabase.")
