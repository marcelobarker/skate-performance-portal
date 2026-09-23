
import streamlit as st
import streamlit.components.v1 as components
from streamlit_elements import elements, mui
from auth_utils import (
    sign_in, sign_up, sign_out, current_user, current_profile, load_profile,
    get_supabase, _navigation, request_password_reset, start_password_recovery,
    update_password,
)

from ui_theme import apply_ui_theme

st.set_page_config(initial_sidebar_state="collapsed", page_title="Seleção Brasileira de Skateboarding", page_icon="🛹", layout="wide")
apply_ui_theme()

def _is_mobile_request():
    try:
        ua = str(st.context.headers.get("User-Agent", "")).lower()
    except Exception:
        ua = ""
    return any(x in ua for x in ("iphone", "ipad", "ipod", "android", "mobile"))

IS_MOBILE = _is_mobile_request()

st.markdown("""<style>
/* V2.0 — controles globais escuros */
[data-testid="stButton"] button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stDownloadButton"] button {
  background:#0b1d31!important;color:#eef8ff!important;border:1px solid #245274!important;border-radius:10px!important;
}
[data-testid="stButton"] button:hover,[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover{
  background:#102b46!important;color:#fff!important;border-color:#1398ff!important;
}
[data-testid="stButton"] button:disabled,[data-testid="stFormSubmitButton"] button:disabled{
  background:#0a1725!important;color:#668097!important;border-color:#18354d!important;opacity:.8!important;
}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input,[data-testid="stTimeInput"] input,
[data-testid="stSelectbox"] [role="combobox"],[data-testid="stMultiSelect"] [role="combobox"],textarea{
  background:#0b1d2d!important;color:#eef8ff!important;border-color:#245274!important;
}
[data-testid="stDateInput"] button,[data-testid="stTimeInput"] button{background:#0b1d2d!important;color:#eef8ff!important;}
[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{background:#0b1d2d!important;color:#eef8ff!important;}
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"],[data-baseweb="calendar"]{background:#081827!important;color:#eef8ff!important;}
[data-baseweb="menu"] li,[role="option"],[data-baseweb="calendar"] button{background:#081827!important;color:#eef8ff!important;}
[data-baseweb="menu"] li:hover,[role="option"]:hover{background:#12304b!important;}

/* V4.24 — navbar encostada no topo */
[data-testid="stMainBlockContainer"]{
  padding-top:0!important;
  margin-top:0!important;
}
.main .block-container,.block-container{
  padding-top:0!important;
  margin-top:0!important;
}
</style>""", unsafe_allow_html=True)

st.markdown("""
<style>
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}
[data-testid="stSidebar"]{background:#081827!important}
[data-testid="stSidebar"] *{color:#d9eafa!important}
[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important}
.block-container{max-width:none!important;width:calc(100vw - 32px)!important;padding-left:16px!important;padding-right:16px!important;padding-top:1.2rem!important}
.hero{background:#0b1d31;border:1px solid #173b5a;border-radius:18px;padding:24px 28px;margin-bottom:22px}
.brand{font-size:31px;font-weight:900;font-style:italic;letter-spacing:-1px}
.brand .blue{color:#1398ff}.brand .time{font-size:15px;font-style:normal;margin-left:8px}
.sub{color:#6bc1f7;font-size:11px;letter-spacing:.7px}
.card{background:#0b1d31;border:1px solid #173b5a;border-radius:16px;padding:20px;height:155px}
.card h3{margin:0 0 8px;color:#f5f8ff}.muted{color:#9bb2c8}
[data-testid="stMetric"]{background:#0b1d31;border:1px solid #173b5a;padding:14px;border-radius:14px}
[data-testid="stMetricLabel"] p,[data-testid="stMetricValue"],[data-testid="stMetricValue"] div{color:#eef8ff!important}
[data-testid="stCaptionContainer"] p{color:#9bb2c8!important}
h1,h2,h3,p,label{color:#eef8ff}
/* Login/cadastro: remove os blocos brancos do tema padrão */
[data-testid="stTextInput"] input{background:#0b1d31!important;color:#eef8ff!important;border:1px solid #245274!important;border-radius:10px!important}
[data-testid="stTextInput"] input:focus{border-color:#1398ff!important;box-shadow:0 0 0 1px #1398ff!important}
[data-testid="stTextInput"] input::placeholder{color:#7893aa!important}
[data-testid="stTextInput"] button{background:transparent!important;color:#9fc7e5!important}
[data-testid="stFormSubmitButton"] button{background:#1398ff!important;color:#fff!important;border:1px solid #1398ff!important;border-radius:10px!important;font-weight:800!important}
[data-testid="stFormSubmitButton"] button:hover{background:#087fd8!important;border-color:#34aaff!important;color:#fff!important}
[data-testid="stForm"]{border-color:#173b5a!important;background:#081827!important}
/* V4.81 — botões de autenticação compactos, sem esticar pela tela */
[data-testid="stFormSubmitButton"]{width:auto!important;display:flex!important;}
[data-testid="stFormSubmitButton"] button{width:auto!important;min-width:170px!important;padding-left:28px!important;padding-right:28px!important;}
.sp-auth-link [data-testid="stButton"] button{width:auto!important;min-width:0!important;padding:.35rem .15rem!important;border:0!important;background:transparent!important;color:#6bc1f7!important;box-shadow:none!important;}
.sp-auth-link [data-testid="stButton"] button:hover{color:#fff!important;background:transparent!important;border:0!important;}
</style>
""", unsafe_allow_html=True)

# V4.74 — correção mobile real baseada no User-Agent.
# Não depende apenas de @media, pois alguns WebViews do iPhone reportam um viewport CSS maior.
if IS_MOBILE:
    st.markdown("""<style>
    html,body,#root,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"]{
      width:100%!important;max-width:100%!important;min-height:100vh!important;min-height:100dvh!important;
      overflow-x:hidden!important;background:#03111E!important;
    }
    [data-testid="stMain"],section.main,.main,[data-testid="stAppViewContainer"]>.main{
      width:100%!important;max-width:100%!important;margin:0!important;overflow-x:hidden!important;
    }
    [data-testid="stMainBlockContainer"],.main .block-container,.block-container{
      box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;
      margin:0!important;padding:0 10px 28px!important;overflow-x:hidden!important;
    }
    [data-testid="stElementContainer"],[data-testid="stCustomComponentV1"]{width:100%!important;max-width:100%!important;min-width:0!important;overflow:hidden!important;}
    iframe[title="streamlit_elements.core.frame"]{display:block!important;width:100%!important;max-width:100%!important;min-width:0!important;border:0!important;background:#03111E!important;}
    h1{font-size:2.05rem!important;line-height:1.08!important;letter-spacing:-.03em!important;margin-top:1rem!important;}
    [data-testid="stCaptionContainer"] p{font-size:.95rem!important;line-height:1.4!important;}
    [data-testid="stTabs"] [role="tablist"]{overflow-x:auto!important;white-space:nowrap!important;}
    [data-testid="stForm"]{padding:16px!important;}
    </style>""", unsafe_allow_html=True)

# V4.01: a Home e o login não usam a sidebar antiga.
st.markdown("""<style>
section[data-testid="stSidebar"],[data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"],[data-testid="stSidebarCollapsedControl"],button[aria-label="Open sidebar"],button[aria-label="Close sidebar"]{display:none!important;visibility:hidden!important}
[data-testid="stAppViewContainer"]>.main{margin-left:0!important;width:100%!important}
</style>""", unsafe_allow_html=True)

# V4.81 — recuperação de senha. O Supabase devolve os tokens no fragmento (#).\n# Como fragmentos não chegam ao Python, um pequeno bridge os move uma única vez\n# para query params; o servidor consome os tokens e limpa a URL imediatamente.\ncomponents.html("""<script>\n(function(){\n  try{\n    const w = window.parent;\n    const h = w.location.hash || '';\n    if(h && h.indexOf('type=recovery') !== -1){\n      const hp = new URLSearchParams(h.substring(1));\n      const at = hp.get('access_token');\n      const rt = hp.get('refresh_token');\n      if(at && rt){\n        const u = new URL(w.location.href);\n        u.hash = '';\n        u.searchParams.set('sp_recovery_access', at);\n        u.searchParams.set('sp_recovery_refresh', rt);\n        w.location.replace(u.toString());\n      }\n    }\n  }catch(e){}\n})();\n</script>""", height=0)\n\n_recovery_access = st.query_params.get("sp_recovery_access")\n_recovery_refresh = st.query_params.get("sp_recovery_refresh")\nif _recovery_access and _recovery_refresh:\n    try:\n        start_password_recovery(_recovery_access, _recovery_refresh)\n        st.query_params.clear()\n        st.rerun()\n    except Exception:\n        st.query_params.clear()\n        st.session_state["sp_recovery_error"] = "O link de recuperação expirou ou já foi utilizado. Solicite um novo e-mail."\n        st.rerun()\n\nif st.session_state.get("sp_password_recovery"):\n    st.title("Criar nova senha")\n    st.caption("Digite uma nova senha para sua conta.")\n    with st.form("password_recovery_form"):\n        new_password = st.text_input("Nova senha", type="password", help="Use pelo menos 6 caracteres.")\n        new_password_confirm = st.text_input("Confirmar nova senha", type="password")\n        change_password = st.form_submit_button("Salvar nova senha", use_container_width=False)\n    if change_password:\n        if len(new_password) < 6:\n            st.error("A nova senha precisa ter pelo menos 6 caracteres.")\n        elif new_password != new_password_confirm:\n            st.error("As duas senhas não são iguais.")\n        else:\n            try:\n                update_password(new_password)\n                sign_out()\n                st.session_state.pop("sp_password_recovery", None)\n                st.success("Senha alterada com sucesso. Agora entre com sua nova senha.")\n                st.rerun()\n            except Exception:\n                st.error("Não foi possível alterar a senha. Solicite um novo link de recuperação e tente novamente.")\n    st.stop()\n\nuser = current_user()\nprofile = current_profile()
if user and not profile:
    profile = load_profile(user.id)

if not user:
    st.title("Bem-vindo à Seleção Brasileira de Skateboarding")
    st.caption("Entre na sua conta ou solicite um novo cadastro.")
    if st.session_state.pop("sp_recovery_error", None):
        st.error("O link de recuperação expirou ou já foi utilizado. Solicite um novo e-mail.")
    login_tab, signup_tab = st.tabs(["ENTRAR", "CRIAR CONTA"])

    with login_tab:
        # Ajuda Chrome/Safari/Edge a reconhecerem os campos como credenciais salvas.
        # Streamlit não expõe autocomplete diretamente no st.text_input, então ajustamos
        # os atributos dos inputs no DOM sem alterar a autenticação Python.
        components.html("""<script>
        (function(){
          function mark(){
            try{
              const d=window.parent.document;
              const inputs=[...d.querySelectorAll('input')];
              const email=inputs.find(i => (i.getAttribute('aria-label')||'').toLowerCase().includes('e-mail'));
              const pass=inputs.find(i => i.type==='password');
              if(email){email.setAttribute('autocomplete','email');email.setAttribute('name','email');email.setAttribute('id','sp-login-email');}
              if(pass){pass.setAttribute('autocomplete','current-password');pass.setAttribute('name','password');pass.setAttribute('id','sp-login-password');}
            }catch(e){}
          }
          mark(); setTimeout(mark,250); setTimeout(mark,900);
        })();
        </script>""", height=0)
        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="seu@email.com")
            password = st.text_input("Senha", type="password")
            keep_connected = st.checkbox("Me manter conectado neste dispositivo")
            submit = st.form_submit_button("Entrar", use_container_width=False)
        if submit:
            try:
                sign_in(email, password, keep_connected=keep_connected)
                st.success("Login realizado.")
                st.rerun()
            except Exception as e:
                # O Supabase bloqueia o login quando a confirmação de e-mail está ativa
                # e o usuário ainda aparece como "Waiting for verification". Antes,
                # essa situação caía na mesma mensagem genérica de senha/e-mail incorretos.
                msg = str(e).lower()
                if (
                    "email not confirmed" in msg
                    or "email_not_confirmed" in msg
                    or "not confirmed" in msg
                    or "not verified" in msg
                    or "unverified" in msg
                ):
                    st.error("Seu e-mail ainda não foi verificado. Abra o e-mail enviado pela plataforma e confirme sua conta antes de entrar.")
                    st.info("Se não encontrar a mensagem, verifique também Spam, Lixo eletrônico e Promoções. Depois de confirmar o e-mail, volte aqui e faça o login normalmente.")
                elif (
                    "invalid login credentials" in msg
                    or "invalid credentials" in msg
                    or "invalid email or password" in msg
                    or "wrong password" in msg
                ):
                    st.error("E-mail ou senha incorretos. Confira os dados e tente novamente.")
                else:
                    st.error("Não foi possível entrar agora. Confira seus dados e tente novamente.")

        st.markdown('<div class="sp-auth-link">', unsafe_allow_html=True)
        forgot = st.button("Esqueci minha senha", key="forgot_password_btn")
        st.markdown('</div>', unsafe_allow_html=True)
        if forgot:
            st.session_state["show_password_reset"] = True

        if st.session_state.get("show_password_reset"):
            st.markdown("#### Recuperar senha")
            st.caption("Informe o e-mail cadastrado. Vamos enviar um link para você criar uma nova senha.")
            with st.form("forgot_password_form"):
                reset_email = st.text_input("E-mail cadastrado", key="reset_email", placeholder="seu@email.com")
                send_reset = st.form_submit_button("Enviar link de recuperação", use_container_width=False)
            if send_reset:
                if not reset_email.strip():
                    st.error("Informe seu e-mail.")
                else:
                    try:
                        request_password_reset(reset_email)
                        st.success("Se esse e-mail estiver cadastrado, o link de recuperação será enviado. Confira também Spam e Lixo eletrônico.")
                    except Exception as e:
                        msg = str(e).lower()
                        if "rate" in msg or "limit" in msg or "too many" in msg:
                            st.error("O limite de envio de e-mails foi atingido. Aguarde um pouco ou configure um SMTP próprio no Supabase.")
                        else:
                            st.error("Não foi possível enviar o e-mail de recuperação agora. Tente novamente em alguns minutos.")

    with signup_tab:
        with st.form("signup_form"):
            full_name = st.text_input("Nome completo")
            email2 = st.text_input("E-mail")
            password2 = st.text_input("Senha", type="password", help="Use pelo menos 6 caracteres.")
            role_label = st.selectbox("Quero me cadastrar como", ["Skatista", "Técnico", "Presidente", "Vice-presidente", "Chefe de Equipe", "Comissão Técnica", "Familiar"])
            linked_athlete_id=None
            if role_label == "Familiar":
                try:
                    avail=get_supabase().rpc("signup_athletes").execute().data or []
                except Exception: avail=[]
                if avail:
                    amap={a.get("full_name") or "Atleta":a["id"] for a in avail}
                    linked_athlete_id=amap[st.selectbox("Atleta que ficará vinculado a esta conta",list(amap))]
                else:
                    st.info("Ainda não há atleta ativo disponível para vínculo.")
            modality = st.selectbox("Modalidade principal", ["Street","Park","Vert","Outro"])
            accept = st.checkbox("Confirmo que os dados acima estão corretos.")
            create = st.form_submit_button("Solicitar cadastro", use_container_width=False)
        if create:
            if not full_name.strip() or not email2.strip() or len(password2) < 6 or not accept:
                st.error("Preencha os campos, use uma senha com pelo menos 6 caracteres e confirme os dados.")
            else:
                role_map={"Skatista":"skatista","Técnico":"tecnico","Presidente":"presidente","Vice-presidente":"vice_presidente","Chefe de Equipe":"chefe_equipe","Comissão Técnica":"comissao_tecnica","Familiar":"familiar"}
                role = role_map[role_label]

                # A criação da conta e o carregamento do perfil são etapas diferentes.
                # Antes, qualquer falha logo após o sign_up (por exemplo, o perfil ainda
                # não estar disponível na primeira leitura) caía no mesmo except e fazia
                # o usuário receber uma falsa mensagem de que a conta não foi criada.
                try:
                    res = sign_up(full_name, email2, password2, role, modality, linked_athlete_id)
                except Exception as e:
                    msg = str(e).lower()
                    if "already" in msg or "registered" in msg or "exists" in msg or "duplicate" in msg:
                        st.error("Este e-mail já possui uma conta cadastrada. Tente entrar ou use outro e-mail.")
                    else:
                        st.error("Não foi possível criar a conta. Revise os dados e tente novamente.")
                else:
                    created_user = getattr(res, "user", None)
                    created_session = getattr(res, "session", None)

                    if created_user:
                        # Se o Supabase abriu a sessão imediatamente, preservamos o login.
                        # O perfil pode levar um instante para aparecer via trigger/RLS, então
                        # uma falha nessa leitura não invalida um cadastro já concluído.
                        if created_session:
                            st.session_state["sp_user"] = created_user
                            st.session_state["sp_session"] = created_session
                            try:
                                load_profile(created_user.id)
                            except Exception:
                                pass

                        st.success("Cadastro realizado com sucesso!")
                        if created_session:
                            st.info("Sua conta foi criada e está aguardando aprovação do administrador.")
                        else:
                            st.info("Agora confirme seu e-mail pelo link enviado pela plataforma. Depois da confirmação, aguarde a aprovação do administrador para acessar o sistema.")
                    else:
                        # Alguns projetos Supabase com confirmação de e-mail podem não
                        # devolver uma sessão imediatamente. Não classificamos isso como erro.
                        st.success("Solicitação de cadastro enviada.")
                        st.info("Confira sua caixa de entrada e confirme o e-mail pelo link enviado pela plataforma. Depois disso, aguarde a aprovação do administrador.")
    st.stop()

status = (profile or {}).get("status","pendente")
role = (profile or {}).get("role","skatista")
name = (profile or {}).get("full_name", getattr(user,"email","Usuário"))

# Dados reais usados na Home. Falhas de rede não derrubam a interface.
home_feed_videos = []
try:
    sb_home = get_supabase()
    _posts = sb_home.table("athlete_posts").select("id,athlete_id,session_title,caption,created_at,video_path").order("created_at", desc=True).limit(3).execute().data or []
    _ids = list({p.get("athlete_id") for p in _posts if p.get("athlete_id")})
    _profiles = sb_home.table("profiles").select("id,full_name").in_("id", _ids).execute().data if _ids else []
    _names = {p.get("id"): p.get("full_name") for p in (_profiles or [])}
    from datetime import datetime
    for _post in _posts:
        _created = _post.get("created_at") or ""
        _when = "Vídeo recente"
        try:
            _dt = datetime.fromisoformat(_created.replace("Z", "+00:00"))
            _when = _dt.strftime("%d/%m/%Y • %H:%M")
        except Exception:
            pass
        home_feed_videos.append((
            _post.get("session_title") or _post.get("caption") or "Vídeo de treino",
            _names.get(_post.get("athlete_id")) or "Atleta",
            _when,
        ))
except Exception:
    home_feed_videos = []

# V4.42 TEMPORÁRIO: acesso liberado a todo usuário autenticado.

st.markdown("""
<style>
:root {
  --sp-bg:#020b14;
  --sp-panel:#071727;
  --sp-panel2:#0a1d30;
  --sp-border:#153a59;
  --sp-blue:#0787ff;
  --sp-cyan:#20e6ff;
  --sp-text:#f5f8fc;
  --sp-muted:#8fa6ba;
}
html, body, [data-testid="stAppViewContainer"], .stApp {
  background:
    radial-gradient(circle at 75% 0%, rgba(0,126,255,.13), transparent 30%),
    linear-gradient(180deg,#020b14 0%,#03111e 100%) !important;
}
[data-testid="stHeader"] {background:transparent !important;}
[data-testid="stToolbar"], [data-testid="stDecoration"] {display:none !important;}
[data-testid="stSidebar"] {display:none !important;}
.block-container {
  width:100% !important;
  max-width:1480px !important;
  padding:0 22px 44px !important;
}
iframe[title="streamlit_elements.core.frame"] {
  width:100% !important;
}
@media (max-width: 900px) {
  .block-container {padding:0 12px 30px !important;}
}
</style>
""", unsafe_allow_html=True)

# V4.74 — largura premium no desktop; no mobile usa 100% do container sem 100vw.
if not IS_MOBILE:
    st.markdown("""<style>
    html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"],.stApp{width:100%!important;background:#06111f!important;}
    [data-testid="stMain"],section.main,.main{width:100%!important;}
    [data-testid="stMainBlockContainer"],.main .block-container,.block-container{
      width:min(1560px, calc(100vw - 48px))!important;max-width:1560px!important;margin:0 auto!important;padding:0 0 40px!important;
    }
    iframe[title="streamlit_elements.core.frame"]{width:100%!important;background:#06111f!important;border:0!important;border-radius:0!important;}
    [data-testid="stElementContainer"]{overflow:visible!important;}
    [data-testid="stElementContainer"]:has(iframe[title="streamlit_elements.core.frame"]){background:#06111f!important;}
    </style>""", unsafe_allow_html=True)

# Cores/estilos reutilizados pelos componentes Material UI.
card = {
    "background": "linear-gradient(145deg,#081b2d,#061523)",
    "border": "1px solid #163b59",
    "borderRadius": "18px",
    "boxShadow": "0 16px 40px rgba(0,0,0,.22)",
}
muted = "#8fa6ba"
white = "#f5f8fc"
cyan = "#20e6ff"
blue = "#0787ff"


# Navbar V4.29 visual preservado; links nativos fora de iframe.
nav_name = str((profile or {}).get("full_name") or getattr(user, "email", None) or "Usuário").strip()
nav_role = str((profile or {}).get("role") or "membro").replace("_", " ").title()
nav_photo = (profile or {}).get("photo_url")
from nav_v472 import render_top_nav
render_top_nav(nav_name=nav_name, nav_role=nav_role, nav_photo=nav_photo, active='Home', key="nav_Home.py")

hero_min_h = 420 if IS_MOBILE else {"xs":430,"sm":390,"md":465}
hero_title_size = 38 if IS_MOBILE else {"xs":34,"sm":46,"md":72}
hero_line_height = .98 if IS_MOBILE else {"xs":.98,"md":.92}
hero_letter_spacing = "-1.4px" if IS_MOBILE else {"xs":"-1.5px","md":"-3px"}
hero_side_shape = {"right":"-28%","top":"12%","width":"70%","height":"76%"} if IS_MOBILE else {}

with elements("skate_performance_home"):
    # O streamlit-elements roda dentro de um iframe. O fundo precisa ser definido
    # aqui dentro também; caso contrário o navegador usa branco nas bordas.
    mui.GlobalStyles(styles={
        "html": {"backgroundColor":"#06111f"},
        "body": {"margin":0,"backgroundColor":"#06111f","overflowX":"hidden"},
        "#root": {"backgroundColor":"#06111f"},
    })
    # Container geral: NÃO é um quadrado central; ocupa 100% da área disponível.
    with mui.Box(sx={
        "width": "100%",
        "maxWidth": "none",
        "margin": "0",
        "backgroundColor": "#06111f",
        "fontFamily": "\"Segoe UI Variable\", Inter, Manrope, Arial, sans-serif",
        "pb": 3,
    }):
        # Navigation bar feita com Material UI (Streamlit Elements).
        # Evita incompatibilidade do streamlit-community-navigation-bar com
        # versões novas do Streamlit (PagesManager.set_pages).
        # HERO
        with mui.Paper(elevation=0, sx={
            **card,
            "position":"relative","overflow":"hidden",
            "minHeight":hero_min_h,
            "mx":{"xs":0,"md":1},
            "background":"radial-gradient(circle at 80% 25%, rgba(0,133,255,.26), transparent 28%), linear-gradient(115deg,#06111d 10%,#09223a 58%,#071827 100%)",
        }):
            # Elementos abstratos dão profundidade sem fingir uma foto.
            mui.Box(sx={
                "position":"absolute","right":hero_side_shape.get("right", {"xs":"-18%","md":"6%"}),"top":hero_side_shape.get("top", "8%"),"width":hero_side_shape.get("width", {"xs":"62%","md":"34%"}),"height":hero_side_shape.get("height", "84%"),
                "border":"1px solid rgba(32,230,255,.16)","borderRadius":"50%",
                "boxShadow":"0 0 90px rgba(0,126,255,.16) inset",
                "transform":"rotate(-12deg)"
            })
            with mui.Box(sx={
                "position":"relative","zIndex":2,"px":{"xs":2.2,"sm":3,"md":7},"py":{"xs":4,"sm":5,"md":7},
                "maxWidth":820
            }):
                mui.Typography("SELEÇÃO BRASILEIRA", sx={
                    "color":white,"fontSize":{"xs":12,"sm":14},"fontWeight":900,"letterSpacing":{"xs":"1px","sm":"1.5px"}
                })
                mui.Typography("DE SKATEBOARDING", sx={
                    "color":cyan,"fontSize":{"xs":9,"sm":11},"fontWeight":900,"letterSpacing":{"xs":"3px","sm":"5px"},"mt":.5
                })
                mui.Typography("PERFORMANCE", sx={
                    "color":white,"fontWeight":950,"fontSize":hero_title_size,
                    "lineHeight":hero_line_height,"letterSpacing":hero_letter_spacing,"mt":3
                })
                mui.Typography("EM EVOLUÇÃO", sx={
                    "color":white,"fontWeight":950,"fontSize":hero_title_size,
                    "lineHeight":hero_line_height,"letterSpacing":hero_letter_spacing
                })
                mui.Typography("ANÁLISE  •  EVOLUÇÃO  •  PERFORMANCE", sx={
                    "color":"#a7bbcc","fontSize":11,"fontWeight":800,"letterSpacing":"1.6px","mt":2.5
                })
                with mui.Box(sx={"display":"flex","gap":1.5,"mt":3,"flexWrap":"wrap"}):
                    mui.Button(
                        mui.icon.CloudUploadOutlined(), " ENVIAR VÍDEO",
                        href="/Enviar_Manobra", target="_top",
                        variant="contained",
                        sx={"bgcolor":blue,"fontWeight":900,"px":2.4,"py":1.15,"borderRadius":"10px"}
                    )
                    mui.Button(
                        mui.icon.History(), " VER HISTÓRICO",
                        href="/Historico_de_Treinos", target="_top",
                        variant="outlined",
                        sx={"color":white,"borderColor":"#31516c","fontWeight":900,"px":2.4,"py":1.15,"borderRadius":"10px"}
                    )

        # KPIs principais — cards neon, tipografia maior e labels mais legíveis
        with mui.Box(sx={
            "display":"grid",
            "gridTemplateColumns":"1fr" if IS_MOBILE else {"xs":"1fr","sm":"repeat(2,1fr)","lg":"repeat(4,1fr)"},
            "gap":1.8,"mx":{"xs":0,"md":1},"mt":2.2
        }):
            kpis = [
                ("TREINOS REALIZADOS","24","+12%", mui.icon.BarChartRounded, "#b85cff"),
                ("TENTATIVAS REGISTRADAS","1.284","+8%", mui.icon.TrackChangesRounded, "#00e4a4"),
                ("MANOBRAS ANALISADAS","58","+3%", mui.icon.SportsRounded, "#29a8ff"),
                ("ATLETAS ATIVOS","10","+1", mui.icon.GroupsRounded, "#20e6ff"),
            ]
            for label, value, delta, Icon, color in kpis:
                with mui.Paper(elevation=0, sx={
                    "position":"relative","overflow":"hidden",
                    "p":2.35,"minHeight":132,
                    "background":"linear-gradient(145deg,#071a2b 0%,#04111d 100%)",
                    "border":f"1px solid {color}70",
                    "borderRadius":"18px",
                    "boxShadow":f"0 0 0 1px {color}12, 0 0 24px {color}18, inset 0 1px 0 rgba(255,255,255,.035)",
                    "transition":"transform .2s ease, box-shadow .2s ease",
                    "&:hover":{
                        "transform":"translateY(-3px)",
                        "boxShadow":f"0 0 0 1px {color}35, 0 0 34px {color}30"
                    }
                }):
                    mui.Box(sx={
                        "position":"absolute","width":110,"height":110,"right":-35,"top":-45,
                        "borderRadius":"50%","backgroundColor":f"{color}10",
                        "boxShadow":f"0 0 45px {color}20"
                    })
                    with mui.Box(sx={"display":"flex","alignItems":"center","justifyContent":"space-between","position":"relative"}):
                        with mui.Box(sx={
                            "width":45,"height":45,"borderRadius":"13px",
                            "display":"flex","alignItems":"center","justifyContent":"center",
                            "background":f"linear-gradient(145deg,{color}25,{color}0D)",
                            "border":f"1px solid {color}80",
                            "boxShadow":f"0 0 18px {color}28"
                        }):
                            Icon(sx={"color":color,"fontSize":25,"filter":f"drop-shadow(0 0 5px {color})"})
                        with mui.Box(sx={
                            "px":1,"py":.45,"borderRadius":"20px",
                            "backgroundColor":"rgba(0,228,164,.08)",
                            "border":"1px solid rgba(0,228,164,.20)"
                        }):
                            mui.Typography(delta, sx={"color":"#25f0b0","fontSize":10,"fontWeight":950})
                    mui.Typography(value, sx={
                        "color":white,"fontSize":29,"fontWeight":950,"mt":1.35,
                        "lineHeight":1,"letterSpacing":"-.7px"
                    })
                    mui.Typography(label, sx={
                        "color":"#b5c9d9","fontSize":10.5,"fontWeight":900,
                        "letterSpacing":"1.15px","mt":.85
                    })

        # NOVA FAIXA CENTRAL: calendário + tarefas + últimos vídeos
        with mui.Box(sx={
            "display":"grid",
            "gridTemplateColumns":{"xs":"1fr","lg":"1.05fr .95fr 1fr"},
            "gap":1.8,"mx":{"xs":0,"md":1},"mt":2
        }):
            # Calendário moderno
            with mui.Paper(elevation=0, sx={**card,"p":2.4,"minHeight":330}):
                with mui.Box(sx={"display":"flex","justifyContent":"space-between","alignItems":"center","mb":2}):
                    with mui.Box(sx={"display":"flex","alignItems":"center","gap":1}):
                        mui.icon.CalendarMonth(sx={"color":cyan})
                        mui.Typography("Calendário", sx={"color":white,"fontSize":20,"fontWeight":950})
                    mui.Typography("SET 2026", sx={"color":cyan,"fontSize":10,"fontWeight":900,"letterSpacing":"1.5px"})
                with mui.Box(sx={"display":"grid","gridTemplateColumns":"repeat(7,1fr)","gap":.65}):
                    for day in ["D","S","T","Q","Q","S","S"]:
                        mui.Typography(day, sx={"textAlign":"center","color":"#66849c","fontSize":9,"fontWeight":900,"pb":.6})
                    for d in range(1,31):
                        active = d in [22,24,28]
                        today = d == 22
                        with mui.Box(sx={
                            "height":32,"display":"flex","alignItems":"center","justifyContent":"center",
                            "borderRadius":"9px",
                            "backgroundColor":"#087cff" if today else ("rgba(32,230,255,.08)" if active else "transparent"),
                            "border":"1px solid #20e6ff" if active and not today else "1px solid transparent",
                        }):
                            mui.Typography(str(d), sx={
                                "color":"#fff" if today else ("#20e6ff" if active else "#b8c7d4"),
                                "fontSize":10,"fontWeight":900 if active else 650
                            })
                with mui.Box(sx={"display":"flex","gap":1.5,"mt":2,"flexWrap":"wrap"}):
                    for label,color in [("Treino","#20e6ff"),("Evento","#b85cff"),("Tarefa","#ffbf3f")]:
                        with mui.Box(sx={"display":"flex","alignItems":"center","gap":.6}):
                            mui.Box(sx={"width":7,"height":7,"borderRadius":"50%","bgcolor":color})
                            mui.Typography(label,sx={"color":muted,"fontSize":10,"fontWeight":750})

            # Tarefas do técnico
            with mui.Paper(elevation=0, sx={**card,"p":2.4,"minHeight":330}):
                with mui.Box(sx={"display":"flex","justifyContent":"space-between","alignItems":"center","mb":2}):
                    with mui.Box(sx={"display":"flex","alignItems":"center","gap":1}):
                        mui.icon.AssignmentTurnedInOutlined(sx={"color":"#ffbf3f"})
                        mui.Typography("Tarefas", sx={"color":white,"fontSize":20,"fontWeight":950})
                    mui.Typography("3 pendentes", sx={"color":"#ffbf3f","fontSize":10,"fontWeight":900})
                tasks = [
                    ("Revisar linha de Park","Wallace Gabriel",72,"#20e6ff"),
                    ("Enviar vídeo do treino","Pedro Quintas",45,"#ffbf3f"),
                    ("Finalizar análise técnica","Fernanda Tonissi",20,"#ff5364"),
                ]
                for title, athlete, pct, color in tasks:
                    with mui.Box(sx={"mb":2.05}):
                        with mui.Box(sx={"display":"flex","justifyContent":"space-between","gap":1,"mb":.55}):
                            with mui.Box:
                                mui.Typography(title,sx={"color":"#e7f0f7","fontSize":11,"fontWeight":850})
                                mui.Typography(athlete,sx={"color":muted,"fontSize":10,"mt":.25})
                            mui.Typography(f"{pct}%",sx={"color":color,"fontSize":10,"fontWeight":950})
                        with mui.Box(sx={"height":6,"bgcolor":"#10283d","borderRadius":20,"overflow":"hidden"}):
                            mui.Box(sx={"height":"100%","width":f"{pct}%","bgcolor":color,"borderRadius":20})

            # Últimos vídeos do feed
            with mui.Paper(elevation=0, sx={**card,"p":2.4,"minHeight":330}):
                with mui.Box(sx={"display":"flex","justifyContent":"space-between","alignItems":"center","mb":2}):
                    with mui.Box(sx={"display":"flex","alignItems":"center","gap":1}):
                        mui.icon.SmartDisplayOutlined(sx={"color":"#b85cff"})
                        mui.Typography("Últimos vídeos", sx={"color":white,"fontSize":20,"fontWeight":950})
                    mui.Button("Ver feed", href="/Feed", target="_top", sx={"color":cyan,"fontSize":9,"fontWeight":900})
                videos = home_feed_videos
                if videos:
                    for title, athlete, when in videos:
                        with mui.Box(sx={"display":"flex","alignItems":"center","gap":1.2,"py":1.15,"borderBottom":"1px solid #122d45"}):
                            with mui.Box(sx={
                                "width":58,"height":48,"borderRadius":"10px","flexShrink":0,
                                "display":"flex","alignItems":"center","justifyContent":"center",
                                "background":"linear-gradient(135deg,#102f4a,#071522)",
                                "border":"1px solid #1b4868"
                            }):
                                mui.icon.PlayCircleOutline(sx={"color":cyan,"fontSize":25})
                            with mui.Box(sx={"minWidth":0,"flex":1}):
                                mui.Typography(title,sx={"color":white,"fontSize":12,"fontWeight":850,"whiteSpace":"nowrap","overflow":"hidden","textOverflow":"ellipsis"})
                                mui.Typography(athlete,sx={"color":"#9eb3c5","fontSize":9,"mt":.25})
                                mui.Typography(when,sx={"color":"#607b91","fontSize":8,"mt":.2})
                else:
                    mui.Typography("Ainda não há vídeos publicados no feed.", sx={"color":muted,"fontSize":11,"py":3})

        # FAIXA INFERIOR: ranking + top manobras + atletas
        with mui.Box(sx={
            "display":"grid",
            "gridTemplateColumns":{"xs":"1fr","lg":"1.08fr .97fr .95fr"},
            "gap":1.8,"mx":{"xs":0,"md":1},"mt":2
        }):
            # Ranking por quantidade de treinos
            with mui.Paper(elevation=0, sx={**card,"p":2.4,"minHeight":390,"display":"flex","flexDirection":"column"}):
                with mui.Box(sx={"display":"flex","justifyContent":"space-between","alignItems":"center","mb":2}):
                    with mui.Box(sx={"display":"flex","alignItems":"center","gap":1}):
                        mui.icon.EmojiEventsOutlined(sx={"color":"#ffbf3f"})
                        mui.Typography("Ranking de treinos", sx={"color":white,"fontSize":20,"fontWeight":950})
                    mui.Box()
                ranking = [
                    ("1","Wallace Gabriel","18 treinos","WG","#ffbf3f"),
                    ("2","Fernanda Tonissi","15 treinos","FT","#c9d5df"),
                    ("3","Pedro Quintas","13 treinos","PQ","#d18a55"),
                    ("4","Fernanda Galdino","11 treinos","FG","#29a8ff"),
                    ("5","Dan Sabino","9 treinos","DS","#29a8ff"),
                ]
                for pos,name,count,initials,color in ranking:
                    with mui.Box(sx={"display":"flex","alignItems":"center","gap":1.2,"py":1.05,"borderBottom":"1px solid #122d45"}):
                        mui.Typography(pos,sx={"width":18,"color":color,"fontSize":13,"fontWeight":950})
                        mui.Avatar(initials,sx={"width":34,"height":34,"bgcolor":"#0c3554","color":cyan,"fontSize":9,"fontWeight":950})
                        with mui.Box(sx={"flex":1}):
                            mui.Typography(name,sx={"color":white,"fontSize":12,"fontWeight":850})
                        mui.Typography(count,sx={"color":"#9eb3c5","fontSize":9.5,"fontWeight":850})
                mui.Button(
                    "VER RANKING COMPLETO",
                    href="/Historico_de_Treinos", target="_top",
                    endIcon=mui.icon.ArrowForwardRounded(),
                    fullWidth=True,
                    variant="outlined",
                    sx={
                        "mt":"auto","color":cyan,"borderColor":"#1b668d",
                        "fontSize":10,"fontWeight":950,"letterSpacing":".7px",
                        "borderRadius":"11px","py":1.05,
                        "boxShadow":"0 0 18px rgba(32,230,255,.08)"
                    }
                )

            # Top manobras
            with mui.Paper(elevation=0, sx={**card,"p":2.4,"minHeight":390,"display":"flex","flexDirection":"column"}):
                with mui.Box(sx={"display":"flex","justifyContent":"space-between","alignItems":"center","mb":2}):
                    mui.Typography("Top manobras", sx={"color":white,"fontSize":20,"fontWeight":950})
                    mui.Box()
                tricks = [
                    ("Noseblunt",95.3,"#00e4a4"),
                    ("Blunt",94.9,"#00e4a4"),
                    ("Flip Lipslide",78.6,"#a9df46"),
                    ("Flip Board",68.4,"#ffbf3f"),
                    ("Flip Crooked",17.1,"#ff5364"),
                ]
                for name, pct, color in tricks:
                    with mui.Box(sx={"mb":1.9}):
                        with mui.Box(sx={"display":"flex","justifyContent":"space-between","mb":.7}):
                            mui.Typography(name, sx={"color":"#dce7f0","fontSize":12,"fontWeight":800})
                            mui.Typography(f"{pct:.1f}%".replace(".",","), sx={"color":color,"fontSize":11,"fontWeight":950})
                        with mui.Box(sx={"height":7,"bgcolor":"#10283d","borderRadius":20,"overflow":"hidden"}):
                            mui.Box(sx={"height":"100%","width":f"{pct}%","bgcolor":color,"borderRadius":20})
                mui.Button(
                    "VER TODAS AS MANOBRAS",
                    href="/Livro_de_Manobras", target="_top",
                    endIcon=mui.icon.ArrowForwardRounded(),
                    fullWidth=True,
                    variant="outlined",
                    sx={
                        "mt":"auto","color":cyan,"borderColor":"#1b668d",
                        "fontSize":10,"fontWeight":950,"letterSpacing":".7px",
                        "borderRadius":"11px","py":1.05,
                        "boxShadow":"0 0 18px rgba(32,230,255,.08)"
                    }
                )

            # Comissão técnica
            with mui.Paper(elevation=0, sx={**card,"p":2.4,"minHeight":390,"display":"flex","flexDirection":"column"}):
                with mui.Box(sx={"display":"flex","justifyContent":"space-between","alignItems":"center","mb":2}):
                    with mui.Box(sx={"display":"flex","alignItems":"center","gap":1}):
                        mui.icon.GroupsOutlined(sx={"color":cyan})
                        mui.Typography("Comissão técnica", sx={"color":white,"fontSize":20,"fontWeight":950})
                    mui.Box()

                # Ordem visual fixa por cargo. Na integração final, os nomes/fotos
                # virão dos perfis reais do Supabase.
                staff = [
                    ("Presidente","Presidência","PR","#ffbf3f"),
                    ("Vice-presidente","Vice-presidência","VP","#b85cff"),
                    ("Chefe de equipe","Chefia de equipe","CE","#20e6ff"),
                    ("Comissão técnica","Staff","CT","#29a8ff"),
                ]
                for name, role, initials, color in staff:
                    with mui.Box(sx={
                        "display":"flex","alignItems":"center","gap":1.25,"py":1.15,
                        "borderBottom":"1px solid #122d45"
                    }):
                        mui.Avatar(initials, sx={
                            "width":40,"height":40,
                            "backgroundColor":f"{color}18",
                            "color":color,
                            "border":f"1px solid {color}55",
                            "fontSize":9,"fontWeight":950
                        })
                        with mui.Box(sx={"flex":1,"minWidth":0}):
                            mui.Typography(name, sx={
                                "color":white,"fontSize":12,"fontWeight":850,
                                "whiteSpace":"nowrap","overflow":"hidden","textOverflow":"ellipsis"
                            })
                            mui.Typography(role, sx={
                                "color":muted,"fontSize":10,"mt":.3
                            })
                        mui.icon.ChevronRight(sx={"color":"#58748a","fontSize":18})

                mui.Button(
                    "VER MAIS DA EQUIPE",
                    href="/Times", target="_top",
                    endIcon=mui.icon.ArrowForward(),
                    fullWidth=True,
                    variant="outlined",
                    sx={
                        "mt":"auto","color":cyan,"borderColor":"#1b5277",
                        "fontSize":9,"fontWeight":950,"letterSpacing":".8px",
                        "borderRadius":"10px","py":1
                    }
                )

# A navegação é propositalmente visual neste teste.
# A integração real com as páginas existentes será feita somente após aprovação do layout.


# Sessão autenticada: controle discreto, fora do layout principal.
with st.container():
    c1, c2 = st.columns([8, 1])
    with c1:
        st.caption(f"Conectado como: {name}")
    with c2:
        if st.button("Sair", key="home_logout", use_container_width=True):
            sign_out()
            st.rerun()
