import mimetypes, uuid
from datetime import date
import streamlit as st
from auth_utils import require_login, get_supabase, load_profile

from ui_theme import apply_ui_theme

st.set_page_config(initial_sidebar_state="expanded", page_title="Meu Perfil • Skate Performance", page_icon="👤", layout="wide")
apply_ui_theme()
st.markdown("""<style>
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}
[data-testid="stSidebar"]{background:#081827!important}[data-testid="stSidebar"] *{color:#d9eafa!important}
[data-testid="stHeader"],[data-testid="stToolbar"]{display:none!important}.block-container{padding-top:1.2rem!important}
h1,h2,h3,p,label{color:#eef8ff!important}
[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button{background:#0b1d31!important;color:#eef8ff!important;border:1px solid #245274!important;border-radius:10px!important}
[data-testid="stTextInput"] input,[data-testid="stDateInput"] input,[data-testid="stSelectbox"]>div>div,[data-testid="stFileUploader"] section{background:#0b1d2d!important;color:#eef8ff!important;border-color:#24445d!important}
[data-testid="stDateInput"] button{background:#0b1d2d!important;color:#eef8ff!important}
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"],[data-baseweb="calendar"]{background:#081827!important;color:#eef8ff!important}[role="option"]{background:#081827!important;color:#eef8ff!important}
</style>""", unsafe_allow_html=True)
user, profile=require_login(); sb=get_supabase()
st.title("👤 Meu Perfil")
st.caption("Atualize seus dados pessoais, esportivos e sua foto. Perfil de acesso e status são controlados pelo administrador.")
if profile.get("photo_url"): st.image(profile["photo_url"], width=150)
st.markdown(f"### {profile.get('full_name') or 'Usuário'}")
role_label = 'ADMINISTRADOR • MEMBRO DO STAFF' if profile.get('role') == 'admin' else (profile.get('role') or '').upper()
st.caption(f"{profile.get('email') or ''} • {role_label}")

def upload_photo(uploaded):
    ext=(uploaded.name.rsplit('.',1)[-1] if '.' in uploaded.name else 'jpg').lower()
    if ext not in ('jpg','jpeg','png','webp'): ext='jpg'
    path=f"{user.id}/{uuid.uuid4().hex}.{ext}"
    ctype=uploaded.type or mimetypes.guess_type(uploaded.name)[0] or 'image/jpeg'
    sb.storage.from_("profile-photos").upload(path, uploaded.getvalue(), {"content-type":ctype,"upsert":"false"})
    return sb.storage.from_("profile-photos").get_public_url(path)

def parse_birth(v):
    try: return date.fromisoformat(v) if v else date(2000,1,1)
    except Exception: return date(2000,1,1)

with st.form("my_profile"):
    name=st.text_input("Nome completo", value=profile.get("full_name") or "")
    c1,c2=st.columns(2)
    mods=["Street","Park","Vert","Outro"]; mv=profile.get("modality") if profile.get("modality") in mods else "Street"
    modality=c1.selectbox("Modalidade",mods,index=mods.index(mv))
    stances=["Regular","Goofy","Não informado"]; sv=profile.get("stance") if profile.get("stance") in stances else "Não informado"
    stance=c2.selectbox("Base",stances,index=stances.index(sv))
    c3,c4,c5=st.columns([1.3,2,1])
    bv=parse_birth(profile.get("birth_date")) if profile.get("birth_date") else None
    birth_text=c3.text_input("Data de nascimento",value=bv.strftime("%d/%m/%Y") if bv else "",placeholder="DD/MM/AAAA")
    city=c4.text_input("Cidade",value=profile.get("city") or "")
    states=["","AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO","EXTERIOR"]
    state_now=(profile.get("state") or "").upper(); state=c5.selectbox("Estado/UF",states,index=states.index(state_now) if state_now in states else 0)
    photo=st.file_uploader("Foto do perfil",type=["jpg","jpeg","png","webp"])
    save=st.form_submit_button("💾 Salvar meu perfil",use_container_width=True)
if save:
    try:
        payload={"full_name":name.strip() or profile.get("full_name") or "Sem nome","modality":modality,"stance":None if stance=="Não informado" else stance,"birth_date":(date(int(birth_text[6:10]),int(birth_text[3:5]),int(birth_text[0:2])).isoformat() if birth_text.strip() else None),"city":city.strip() or None,"state":state or None}
        if photo is not None: payload["photo_url"]=upload_photo(photo)
        sb.table("profiles").update(payload).eq("id",user.id).execute(); load_profile(user.id)
        st.success("Perfil atualizado."); st.rerun()
    except Exception as exc: st.error(f"Não foi possível atualizar seu perfil: {exc}")
