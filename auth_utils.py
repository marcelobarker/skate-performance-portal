import streamlit as st
from supabase import create_client

# IMPORTANT: never cache the authenticated Supabase client globally.
# Each Streamlit browser session gets its own client via session_state.
def get_supabase():
    if "sp_supabase" not in st.session_state:
        st.session_state["sp_supabase"] = create_client(
            st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
        )
    return st.session_state["sp_supabase"]

def current_user():
    return st.session_state.get("sp_user")

def current_profile():
    return st.session_state.get("sp_profile")

def load_profile(user_id):
    sb = get_supabase()
    res = sb.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
    profile = res.data if res else None
    st.session_state["sp_profile"] = profile
    return profile

def sign_in(email, password):
    sb = get_supabase()
    res = sb.auth.sign_in_with_password({"email": email.strip(), "password": password})
    st.session_state["sp_user"] = res.user
    st.session_state["sp_session"] = res.session
    load_profile(res.user.id)
    return res

def sign_up(full_name, email, password, role, modality):
    sb = get_supabase()
    return sb.auth.sign_up({
        "email": email.strip(),
        "password": password,
        "options": {"data": {"full_name": full_name.strip(), "role": role, "modality": modality}}
    })

def sign_out():
    sb = st.session_state.get("sp_supabase")
    if sb is not None:
        try:
            sb.auth.sign_out()
        except Exception:
            pass
    for k in ("sp_user", "sp_session", "sp_profile", "sp_supabase"):
        st.session_state.pop(k, None)

def require_login(require_active=True, admin=False):
    user = current_user()
    profile = current_profile()
    if not user:
        st.warning("🔒 Faça login pela página Home para acessar esta área.")
        st.stop()
    if profile is None:
        profile = load_profile(user.id)
    if not profile:
        st.error("Seu perfil ainda não foi criado no banco.")
        st.stop()
    if profile.get("status") == "bloqueado":
        st.error("⛔ Seu acesso está bloqueado.")
        st.stop()
    if require_active and profile.get("status") != "ativo":
        st.info("⏳ Seu cadastro está aguardando aprovação do administrador.")
        st.stop()
    if admin and profile.get("role") != "admin":
        st.error("🔐 Área exclusiva do administrador.")
        st.stop()
    return user, profile
