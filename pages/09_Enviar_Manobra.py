import uuid, mimetypes
import streamlit as st
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme

st.set_page_config(page_title="Enviar Vídeo • Skate Performance", page_icon="🎥", layout="wide")
apply_ui_theme(); user, profile = require_login(); sb = get_supabase()
role = profile.get("role")
STAFF = {"admin","tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica"}
ALLOWED = STAFF | {"skatista"}

st.title("🎥 Enviar vídeo para análise")
st.caption("Envie uma tentativa isolada ou uma sessão completa com várias manobras. Os vídeos ficam no Storage externo; o portal guarda o vínculo com o atleta e a análise.")
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

video = st.file_uploader("Vídeo do treino", type=["mp4","mov","webm","m4v"],
                         help="Limite configurado no portal: até 2 GB por arquivo. Para arquivos muito grandes, prefira Wi‑Fi estável.")
caption = st.text_area("Observação", placeholder="Contexto do treino, objetivo, observações para a comissão técnica…", height=90)

if video:
    size_mb = video.size / 1024 / 1024
    st.caption(f"Arquivo selecionado: {video.name} • {size_mb:.1f} MB")
    if video.size > 2 * 1024 * 1024 * 1024:
        st.error("O arquivo ultrapassa 2 GB. Comprima o vídeo ou divida a sessão em duas partes.")

ready = bool(video and video.size <= 2*1024*1024*1024 and (mode == "Sessão completa" or trick_id))
if st.button("Enviar para análise", type="primary", width="stretch", disabled=not ready):
    ext = video.name.rsplit(".",1)[-1].lower() if "." in video.name else "mp4"
    path = f"{target_id}/{uuid.uuid4().hex}.{ext}"
    ct = video.type or mimetypes.guess_type(video.name)[0] or "video/mp4"
    try:
        with st.spinner("Enviando vídeo… mantenha esta página aberta até concluir."):
            sb.storage.from_("trick-videos").upload(path, video.getvalue(), {"content-type":ct,"upsert":"false"})
            payload = {
                "athlete_id": target_id,
                "trick_id": trick_id,
                "video_path": path,
                "caption": caption.strip() or None,
                "upload_kind": "session" if mode == "Sessão completa" else "single",
                "session_title": title.strip() or ("Sessão de treino" if mode == "Sessão completa" else None),
            }
            sb.table("athlete_posts").insert(payload).execute()
        st.success("Vídeo enviado. A sessão já está no feed e pronta para codificação técnica.")
        st.session_state["selected_athlete_id"] = target_id
        st.switch_page("pages/07_Perfil_do_Atleta.py")
    except Exception as e:
        st.error(f"Não foi possível enviar o vídeo. Detalhes: {e}")

st.info("💡 O vídeo não fica salvo no servidor do Streamlit. Ele é enviado ao Storage do projeto e o feed carrega o arquivo sob demanda. Para sessões muito grandes/frequentes, podemos migrar o mesmo fluxo para Cloudflare R2 ou Google Cloud Storage sem mudar a experiência do atleta.")
