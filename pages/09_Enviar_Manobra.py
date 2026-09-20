import uuid,mimetypes
import streamlit as st
from auth_utils import require_login,get_supabase
from ui_theme import apply_ui_theme
st.set_page_config(page_title="Enviar Manobra • Skate Performance",page_icon="🎥",layout="wide"); apply_ui_theme(); user,profile=require_login(); sb=get_supabase()
role=profile.get("role"); ALLOWED={"skatista","admin","tecnico"}
st.title("🎥 Enviar Manobra"); st.caption("Escolha a manobra, grave ou selecione o vídeo e envie para análise.")
if role not in ALLOWED: st.info("Envio disponível para atletas, técnicos e administradores."); st.stop()
target_id=user.id
if role in {"admin","tecnico"}:
    athletes=sb.table("profiles").select("id,full_name,status").eq("role","skatista").eq("status","ativo").order("full_name").execute().data or []
    amap={a["full_name"]:a["id"] for a in athletes}
    if not amap: st.warning("Não há atletas ativos cadastrados."); st.stop()
    target_name=st.selectbox("Atleta do vídeo",list(amap)); target_id=amap[target_name]
try: cats=sb.table("trick_categories").select("*").order("sort_order").execute().data or []; tricks=sb.table("tricks").select("*").eq("active",True).order("name").execute().data or []
except Exception as e: st.error(f"Execute a migration V3.2 primeiro. Detalhes: {e}"); st.stop()
if not tricks: st.warning("O Livro de Manobras ainda está vazio."); st.stop()
cmap={c["name"]:c["id"] for c in cats}; cat=st.selectbox("Categoria",list(cmap)); available=[t for t in tricks if t.get("category_id")==cmap[cat]]; tmap={t["name"]:t["id"] for t in available}; trick=st.selectbox("Manobra",list(tmap)) if tmap else None
video=st.file_uploader("Vídeo da tentativa",type=["mp4","mov","webm"],help="No celular você pode gravar o vídeo e selecionar aqui. Limite: 150 MB.")
caption=st.text_area("Legenda / observação",placeholder="Ex.: tentando melhorar a saída do corrimão…",height=90)
if st.button("Enviar para análise",type="primary",width="stretch",disabled=not(video and trick)):
    if video.size>150*1024*1024: st.error("O vídeo ultrapassa 150 MB.")
    else:
        ext=video.name.rsplit(".",1)[-1].lower() if "." in video.name else "mp4"; path=f"{target_id}/{uuid.uuid4().hex}.{ext}"; ct=video.type or mimetypes.guess_type(video.name)[0] or "video/mp4"
        try:
            sb.storage.from_("trick-videos").upload(path,video.getvalue(),{"content-type":ct,"upsert":"false"})
            sb.table("athlete_posts").insert({"athlete_id":target_id,"trick_id":tmap[trick],"video_path":path,"caption":caption.strip() or None}).execute(); st.success("Vídeo enviado! Ele já está no feed e aguardando análise."); st.session_state["selected_athlete_id"]=target_id; st.switch_page("pages/07_Perfil_do_Atleta.py")
        except Exception as e: st.error(f"Não foi possível enviar: {e}")
