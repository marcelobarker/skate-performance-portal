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

def _navigation(role):
    # Navegação compacta exclusiva do celular. No desktop usamos somente a sidebar.
    st.markdown("""<style>
    .st-key-sp_mobile_nav{display:none!important}
    @media(max-width:768px){
      .st-key-sp_mobile_nav{display:block!important}
      .st-key-sp_mobile_nav [data-testid="stPageLink"] a,
      .st-key-sp_mobile_nav [data-testid="stPopover"] button{
        background:linear-gradient(180deg,#0d2b46,#08233A)!important;
        border:1px solid #159BFF!important;color:#fff!important;border-radius:9px!important;
        min-height:42px!important;box-shadow:0 0 16px rgba(0,124,255,.18)!important
      }
      .st-key-sp_mobile_nav [data-testid="stPageLink"] a:hover,
      .st-key-sp_mobile_nav [data-testid="stPopover"] button:hover{background:#102C46!important;color:#fff!important}
      .st-key-sp_mobile_nav [data-testid="stPopover"] button{font-size:0!important;width:48px!important;min-width:48px!important}
      .st-key-sp_mobile_nav [data-testid="stPopover"] button:before{content:'☰';font-size:24px!important;color:#20E6FF!important}
    }
    </style>""", unsafe_allow_html=True)
    with st.container(key="sp_mobile_nav"):
        n1,n2=st.columns([1.15,6.85],gap="small")
        with n1:
            with st.popover("☰", use_container_width=True):
                st.page_link("Home.py", label="Início", use_container_width=True)
                st.page_link("pages/02_Times.py", label="Times", use_container_width=True)
                st.page_link("pages/06_Calendario.py", label="Calendário", use_container_width=True)
                st.page_link("pages/11_Feed.py", label="Feed", use_container_width=True)
                if role in ("skatista","admin","tecnico"): st.page_link("pages/09_Enviar_Manobra.py", label="Enviar Vídeo", use_container_width=True)
                if role not in ("skatista","familiar"):
                    st.page_link("pages/12_Central_do_Treinador.py", label="Central de Performance", use_container_width=True)
                st.page_link("pages/05_Meu_Perfil.py", label="Meu Perfil", use_container_width=True)
                if role == "admin":
                    st.page_link("pages/01_Cadastros.py", label="Cadastros / Cargos", use_container_width=True)
    with st.sidebar:
        if role == "admin":
            st.caption("ADMINISTRAÇÃO")
            st.page_link("pages/01_Cadastros.py", label="👥 Cargos e cadastros", use_container_width=True)
            st.page_link("pages/02_Times.py", label="🛹 Gerenciar times", use_container_width=True)
            st.page_link("pages/09_Enviar_Manobra.py", label="🎥 Enviar Vídeo", use_container_width=True)

    # Páginas internas: acessadas por cards/botões, não poluem a navegação principal.
    st.markdown("""<style>
    [data-testid="stSidebarNav"] a[href*="03_Analise_de_Treino"],
    [data-testid="stSidebarNav"] a[href*="04_Historico_de_Treinos"],
    [data-testid="stSidebarNav"] a[href*="07_Perfil_do_Atleta"],
    [data-testid="stSidebarNav"] a[href*="08_Livro_de_Manobras"],
    [data-testid="stSidebarNav"] a[href*="10_Codificar_Sessao"]{display:none!important}
    </style>""", unsafe_allow_html=True)
    if role != "admin":
        st.markdown("""<style>[data-testid="stSidebarNav"] a[href*="01_Cadastros"],[data-testid="stSidebarNav"] a[href*="Cadastros"]{display:none!important}</style>""", unsafe_allow_html=True)
    if role in ("skatista", "familiar"):
        st.markdown("""<style>[data-testid="stSidebarNav"] a[href*="Analise_de_Treino"],[data-testid="stSidebarNav"] a[href*="03_Analise"]{display:none!important}</style>""", unsafe_allow_html=True)

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
