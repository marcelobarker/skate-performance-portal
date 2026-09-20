import streamlit as st
from supabase import create_client

COOKIE_NAME = "skate_performance_refresh"

def _cookie_manager():
    try:
        import extra_streamlit_components as stx
        if "sp_cookie_manager" not in st.session_state:
            st.session_state["sp_cookie_manager"] = stx.CookieManager(key="sp_auth_cookie_manager")
        return st.session_state["sp_cookie_manager"]
    except Exception:
        return None

def get_supabase():
    if "sp_supabase" not in st.session_state:
        st.session_state["sp_supabase"] = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    return st.session_state["sp_supabase"]

def _restore_session():
    if st.session_state.get("sp_user"):
        return
    cm = _cookie_manager()
    if cm is None:
        return
    try:
        refresh_token = cm.get(COOKIE_NAME)
        if refresh_token:
            res = get_supabase().auth.refresh_session(refresh_token)
            if getattr(res, "user", None) and getattr(res, "session", None):
                st.session_state["sp_user"] = res.user
                st.session_state["sp_session"] = res.session
                load_profile(res.user.id)
    except Exception:
        pass

def current_user():
    _restore_session()
    return st.session_state.get("sp_user")

def current_profile():
    _restore_session()
    return st.session_state.get("sp_profile")

def load_profile(user_id):
    sb = get_supabase()
    res = sb.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
    profile = res.data if res else None
    st.session_state["sp_profile"] = profile
    return profile

def sign_in(email, password, keep_connected=False):
    sb = get_supabase()
    res = sb.auth.sign_in_with_password({"email": email.strip(), "password": password})
    st.session_state["sp_user"] = res.user
    st.session_state["sp_session"] = res.session
    load_profile(res.user.id)
    cm = _cookie_manager()
    if cm is not None:
        try:
            if keep_connected and getattr(res.session, "refresh_token", None):
                from datetime import datetime, timedelta
                cm.set(COOKIE_NAME, res.session.refresh_token, expires_at=datetime.now() + timedelta(days=30), key="sp_keep_cookie")
            else:
                cm.delete(COOKIE_NAME, key="sp_clear_cookie")
        except Exception:
            pass
    return res

def sign_up(full_name, email, password, role, modality, linked_athlete_id=None):
    sb = get_supabase()
    data={"full_name":full_name.strip(),"role":role,"modality":modality}
    if linked_athlete_id: data["linked_athlete_id"]=linked_athlete_id
    return sb.auth.sign_up({"email":email.strip(),"password":password,"options":{"data":data}})

def sign_out():
    sb = st.session_state.get("sp_supabase")
    if sb is not None:
        try: sb.auth.sign_out()
        except Exception: pass
    cm = _cookie_manager()
    if cm is not None:
        try: cm.delete(COOKIE_NAME, key="sp_logout_cookie")
        except Exception: pass
    for k in ("sp_user", "sp_session", "sp_profile", "sp_supabase"):
        st.session_state.pop(k, None)

def _navigation(role):
    # Home rápido no conteúdo e na sidebar; o primeiro continua visível no celular.
    st.page_link("Home.py", label="⌂ Início", icon=None)
    with st.sidebar:
        if st.button("⌂ INÍCIO", use_container_width=True, key="sp_global_home"):
            st.switch_page("Home.py")
    if role != "admin":
        st.markdown("""<style>
        [data-testid="stSidebarNav"] a[href*="01_Cadastros"],
        [data-testid="stSidebarNav"] a[href*="Cadastros"]{display:none!important}
        </style>""", unsafe_allow_html=True)
    if role in ("skatista", "familiar"):
        st.markdown("""<style>
        [data-testid="stSidebarNav"] a[href*="Analise_de_Treino"],
        [data-testid="stSidebarNav"] a[href*="03_Analise"]{display:none!important}
        </style>""", unsafe_allow_html=True)

def require_login(require_active=True, admin=False):
    user = current_user(); profile = current_profile()
    if not user:
        st.warning("🔒 Faça login pela página Home para acessar esta área."); st.stop()
    if profile is None: profile = load_profile(user.id)
    if not profile: st.error("Seu perfil ainda não foi criado no banco."); st.stop()
    if profile.get("status") == "bloqueado": st.error("⛔ Seu acesso está bloqueado."); st.stop()
    if require_active and profile.get("status") != "ativo": st.info("⏳ Seu cadastro está aguardando aprovação do administrador."); st.stop()
    if admin and profile.get("role") != "admin": st.error("🔐 Área exclusiva do administrador."); st.stop()
    _navigation(profile.get("role"))
    return user, profile
