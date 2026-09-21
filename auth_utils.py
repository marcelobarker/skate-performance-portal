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
            if keep_connected and getattr(res.session, "refresh_token", None):
                from datetime import datetime, timedelta
                cm.set(COOKIE_NAME, res.session.refresh_token, expires_at=datetime.now() + timedelta(days=30), key="sp_keep_cookie")
                # O componente grava o cookie no navegador de forma assíncrona.
                # Um pequeno intervalo evita que o rerun interrompa a gravação.
                time.sleep(0.65)
            else:
                cm.delete(COOKIE_NAME, key="sp_clear_cookie")
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
    """Menu lateral controlado pelo portal. Aceita profile dict ou Supabase User."""
    role = None
    if isinstance(me, dict):
        role = me.get("role")
    elif me is not None:
        # As páginas existentes chamam _navigation(user). Buscamos o profile real
        # sem assumir que o objeto Supabase User possui .get().
        try:
            sb = get_supabase()
            uid = getattr(me, "id", None)
            if uid:
                rows = sb.table("profiles").select("role").eq("id", uid).limit(1).execute().data or []
                if rows:
                    role = rows[0].get("role")
        except Exception:
            role = None
    st.sidebar.page_link("Home.py", label="Home")
    st.sidebar.page_link("pages/02_Times.py", label="Times")
    st.sidebar.page_link("pages/11_Feed.py", label="Feed")
    st.sidebar.page_link("pages/06_Calendario.py", label="Calendário")
    st.sidebar.page_link("pages/05_Meu_Perfil.py", label="Meu Perfil")

    if role in ("skatista","admin","tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica"):
        st.sidebar.page_link("pages/09_Enviar_Manobra.py", label="Enviar Vídeo")

    if role not in ("skatista","familiar"):
        st.sidebar.page_link("pages/12_Central_do_Treinador.py", label="Central de Performance")

    # Cadastros permanece somente na Administração, no final da barra.
    if role == "admin":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Administração")
        st.sidebar.page_link("pages/01_Cadastros.py", label="Cargos e cadastros")
        st.sidebar.page_link("pages/04_Gerenciar_Times.py", label="Gerenciar times")


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
