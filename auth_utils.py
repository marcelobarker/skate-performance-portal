import streamlit as st
import time
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
        return True
    cm = _cookie_manager()
    if cm is None:
        return False
    try:
        cookies = cm.get_all(key="sp_read_auth_cookies") or {}
        refresh_token = cookies.get(COOKIE_NAME)
        if refresh_token:
            res = get_supabase().auth.refresh_session(refresh_token)
            if getattr(res, "user", None) and getattr(res, "session", None):
                st.session_state["sp_user"] = res.user
                st.session_state["sp_session"] = res.session
                load_profile(res.user.id)
                # Renova o cookie com o refresh token mais recente emitido pelo Supabase.
                new_refresh = getattr(res.session, "refresh_token", None)
                if new_refresh:
                    from datetime import datetime, timedelta
                    cm.set(COOKIE_NAME, new_refresh, expires_at=datetime.now() + timedelta(days=30), key="sp_refresh_cookie")
                return True
    except Exception:
        pass
    # CookieManager é um componente de navegador e pode chegar alguns ms depois do Python.
    # Uma única segunda passagem evita cair na tela de login antes de o cookie ser lido.
    probe = int(st.session_state.get("sp_cookie_probe_count", 0))
    if probe < 3:
        st.session_state["sp_cookie_probe_count"] = probe + 1
        time.sleep(0.45)
        st.rerun()
    return False

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
            refresh_token = getattr(res.session, "refresh_token", None)
            if refresh_token:
                from datetime import datetime, timedelta
                # A navegação MUI entre páginas abre uma nova conexão do Streamlit.
                # Guardamos o refresh token mesmo sem "manter conectado" para que
                # F5 e a troca de páginas preservem a sessão. A opção marcada apenas
                # aumenta a duração do cookie.
                lifetime = timedelta(days=30) if keep_connected else timedelta(hours=12)
                cm.set(COOKIE_NAME, refresh_token, expires_at=datetime.now() + lifetime, key="sp_keep_cookie")
                time.sleep(0.65)
        except Exception:
            pass
    return res

def sign_up(full_name, email, password, role, modality, linked_athlete_id=None):
    sb = get_supabase()
    data={"full_name":full_name.strip(),"role":role,"modality":modality}
    if linked_athlete_id: data["linked_athlete_id"]=linked_athlete_id
    return sb.auth.sign_up({"email":email.strip(),"password":password,"options":{"data":data,"email_redirect_to":"https://skateperformance.streamlit.app/"}})

def sign_out():
    sb = st.session_state.get("sp_supabase")
    if sb is not None:
        try: sb.auth.sign_out()
        except Exception: pass
    cm = _cookie_manager()
    if cm is not None:
        try: cm.delete(COOKIE_NAME, key="sp_logout_cookie")
        except Exception: pass
    for k in ("sp_user", "sp_session", "sp_profile", "sp_supabase", "sp_cookie_probe_count"):
        st.session_state.pop(k, None)

def _navigation(me=None):
    """V4.71: navegação antiga/sidebar desativada. A navbar superior é a navegação principal."""
    return None

def require_login(require_active=True, admin=False):
    user = current_user(); profile = current_profile()
    if not user:
        st.warning("🔒 Faça login pela página Home para acessar esta área."); st.stop()
    if profile is None: profile = load_profile(user.id)
    if not profile: st.error("Seu perfil ainda não foi criado no banco."); st.stop()
    # V4.71: qualquer usuário autenticado pode acessar todas as páginas.
    _navigation(profile)
    return user, profile
