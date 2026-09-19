import mimetypes, uuid
import streamlit as st
from auth_utils import require_login, get_supabase, load_profile

st.set_page_config(page_title="Meu Perfil • Skate Performance", page_icon="👤", layout="wide")
st.markdown("""<style>
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}
[data-testid="stSidebar"]{background:#081827!important}[data-testid="stSidebar"] *{color:#d9eafa!important}
[data-testid="stHeader"],[data-testid="stToolbar"]{display:none!important}.block-container{padding-top:1.2rem!important}
h1,h2,h3,p,label{color:#eef8ff!important}
[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button{background:#0b1d31!important;color:#eef8ff!important;border:1px solid #245274!important;border-radius:10px!important}
[data-testid="stTextInput"] input,[data-testid="stSelectbox"]>div>div,[data-testid="stFileUploader"] section{background:#0b1d2d!important;color:#eef8ff!important;border-color:#24445d!important}
</style>""", unsafe_allow_html=True)
user, profile=require_login(); sb=get_supabase()
st.title("👤 Meu Perfil")
st.caption("Atualize seus dados esportivos e sua foto. Perfil de acesso e status são controlados pelo administrador.")
if profile.get("photo_url"):
    st.image(profile["photo_url"], width=150)
st.markdown(f"### {profile.get('full_name') or 'Usuário'}")
st.caption(f"{profile.get('email') or ''} • {(profile.get('role') or '').upper()}")

def upload_photo(uploaded):
    ext=(uploaded.name.rsplit('.',1)[-1] if '.' in uploaded.name else 'jpg').lower()
    if ext not in ('jpg','jpeg','png','webp'): ext='jpg'
    path=f"{user.id}/{uuid.uuid4().hex}.{ext}"
    ctype=uploaded.type or mimetypes.guess_type(uploaded.name)[0] or 'image/jpeg'
    sb.storage.from_("profile-photos").upload(path, uploaded.getvalue(), {"content-type":ctype,"upsert":"false"})
    return sb.storage.from_("profile-photos").get_public_url(path)

with st.form("my_profile"):
    name=st.text_input("Nome completo", value=profile.get("full_name") or "")
    c1,c2,c3=st.columns(3)
    mods=["Street","Park","Vert","Outro"]
    mv=profile.get("modality") if profile.get("modality") in mods else "Street"
    modality=c1.selectbox("Modalidade",mods,index=mods.index(mv))
    stances=["Regular","Goofy","Não informado"]
    sv=profile.get("stance") if profile.get("stance") in stances else "Não informado"
    stance=c2.selectbox("Base",stances,index=stances.index(sv))
    category=c3.text_input("Categoria",value=profile.get("category") or "")
    photo=st.file_uploader("Foto do perfil",type=["jpg","jpeg","png","webp"])
    save=st.form_submit_button("💾 Salvar meu perfil",use_container_width=True)
if save:
    try:
        payload={"full_name":name.strip() or profile.get("full_name") or "Sem nome","modality":modality,"stance":None if stance=="Não informado" else stance,"category":category.strip() or None}
        if photo is not None: payload["photo_url"]=upload_photo(photo)
        sb.table("profiles").update(payload).eq("id",user.id).execute(); load_profile(user.id)
        st.success("Perfil atualizado."); st.rerun()
    except Exception as exc: st.error(f"Não foi possível atualizar seu perfil: {exc}")
