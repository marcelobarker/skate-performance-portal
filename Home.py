
import streamlit as st
from auth_utils import sign_in, sign_up, sign_out, current_user, current_profile, load_profile

from ui_theme import apply_ui_theme

st.set_page_config(page_title="Skate Performance • Portal", page_icon="🛹", layout="wide")
apply_ui_theme()

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
</style>""", unsafe_allow_html=True)

st.markdown("""
<style>
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}
[data-testid="stSidebar"]{background:#081827!important}
[data-testid="stSidebar"] *{color:#d9eafa!important}
[data-testid="stHeader"],header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important}
.block-container{max-width:1400px;padding-top:1.2rem!important}
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
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><div class="brand">SKATE<span class="blue">PERFORMANCE</span><span class="time">TIME BRASIL</span></div>
<div class="sub">ATHLETE MANAGEMENT • TRAINING INTELLIGENCE</div></div>""", unsafe_allow_html=True)

user = current_user()
profile = current_profile()
if user and not profile:
    profile = load_profile(user.id)

if not user:
    st.title("Bem-vindo ao Skate Performance")
    st.caption("Entre na sua conta ou solicite um novo cadastro.")
    login_tab, signup_tab = st.tabs(["ENTRAR", "CRIAR CONTA"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("E-mail")
            password = st.text_input("Senha", type="password")
            keep_connected = st.checkbox("Me manter conectado neste dispositivo")
            submit = st.form_submit_button("Entrar", use_container_width=True)
        if submit:
            try:
                sign_in(email, password, keep_connected=keep_connected)
                st.success("Login realizado.")
                st.rerun()
            except Exception:
                st.error("Não foi possível entrar. Confira e-mail, senha e se o e-mail já foi confirmado.")

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
            create = st.form_submit_button("Solicitar cadastro", use_container_width=True)
        if create:
            if not full_name.strip() or not email2.strip() or len(password2) < 6 or not accept:
                st.error("Preencha os campos, use uma senha com pelo menos 6 caracteres e confirme os dados.")
            else:
                try:
                    role_map={"Skatista":"skatista","Técnico":"tecnico","Presidente":"presidente","Vice-presidente":"vice_presidente","Chefe de Equipe":"chefe_equipe","Comissão Técnica":"comissao_tecnica","Familiar":"familiar"}
                    role = role_map[role_label]
                    res = sign_up(full_name, email2, password2, role, modality, linked_athlete_id)
                    if getattr(res, "session", None):
                        st.session_state["sp_user"] = res.user
                        st.session_state["sp_session"] = res.session
                        load_profile(res.user.id)
                        st.success("Conta criada. Seu cadastro está aguardando aprovação.")
                        st.rerun()
                    else:
                        st.success("Conta criada. Confira seu e-mail para confirmar o cadastro; depois volte aqui para entrar.")
                except Exception as e:
                    st.error("Não foi possível criar a conta. O e-mail pode já estar cadastrado ou os dados precisam ser revisados.")
    st.stop()

status = (profile or {}).get("status","pendente")
role = (profile or {}).get("role","skatista")
name = (profile or {}).get("full_name", getattr(user,"email","Usuário"))

if role != "admin":
    st.markdown("""<style>[data-testid="stSidebarNav"] a[href*="01_Cadastros"],[data-testid="stSidebarNav"] a[href*="Cadastros"]{display:none!important}</style>""", unsafe_allow_html=True)
if role in ("skatista","familiar"):
    st.markdown("""<style>[data-testid="stSidebarNav"] a[href*="Analise_de_Treino"],[data-testid="stSidebarNav"] a[href*="03_Analise"]{display:none!important}</style>""", unsafe_allow_html=True)

top1, top2 = st.columns([5,1])
with top1:
    st.title(f"Olá, {name}")
    st.caption(f"Perfil: {role.upper()} • Status: {status.upper()}")
with top2:
    if st.button("Sair", use_container_width=True):
        sign_out(); st.rerun()

if status == "bloqueado":
    st.error("⛔ Seu acesso está bloqueado. Procure o administrador.")
    st.stop()
if status != "ativo":
    st.info("⏳ Seu cadastro foi recebido e está aguardando aprovação do administrador.")
    st.write("Assim que for aprovado, as áreas de equipe e análise serão liberadas.")
    st.stop()

st.markdown("""<style>
.sp-home-title{font-size:27px;font-weight:900;margin:10px 0 3px}.sp-home-sub{color:#9bb2c8;margin-bottom:16px}
.sp-kpi{border-radius:18px;padding:20px 18px;min-height:142px;border:1px solid #245274;box-shadow:0 14px 34px #0005;position:relative;overflow:hidden}
.sp-kpi:after{content:'';position:absolute;width:100px;height:100px;border-radius:50%;background:#fff0;box-shadow:0 0 70px #ffffff20;right:-35px;top:-35px}
.sp-blue{background:linear-gradient(145deg,#0b4e92,#0877cf)}.sp-green{background:linear-gradient(145deg,#07573e,#07845c)}.sp-purple{background:linear-gradient(145deg,#44207c,#6e2ca5)}.sp-orange{background:linear-gradient(145deg,#713b00,#a85b00)}.sp-red{background:linear-gradient(145deg,#651c2a,#9a2940)}
.sp-icon{font-size:30px}.sp-num{font-size:38px;font-weight:950;line-height:1;margin:10px 0 3px}.sp-name{font-size:14px;font-weight:800}.sp-hint{font-size:11px;color:#dcecffcc;margin-top:12px}
.sp-section{font-size:19px;font-weight:900;margin:26px 0 10px}.sp-quick{background:#0b1d31;border:1px solid #173b5a;border-radius:16px;padding:17px;text-align:center;min-height:104px}.sp-quick-icon{font-size:27px}.sp-quick-title{font-weight:850;margin-top:5px}.sp-quick-sub{font-size:11px;color:#9bb2c8}
</style>""",unsafe_allow_html=True)
st.markdown("<div class='sp-home-title'>Central da Equipe</div><div class='sp-home-sub'>Visão rápida da estrutura e dos treinos disponíveis para o seu perfil.</div>",unsafe_allow_html=True)
try:
    from auth_utils import get_supabase
    sb = get_supabase()
    visible_profiles = sb.table("profiles").select("id,role,status").execute().data or []
    visible_teams = sb.table("teams").select("id").execute().data or []
    visible_trainings = sb.table("training_sessions").select("id").execute().data or []
    athletes_count = sum(1 for x in visible_profiles if x.get("role") == "skatista" and x.get("status") == "ativo")
    tech_count = sum(1 for x in visible_profiles if x.get("role") in ("tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica") and x.get("status") == "ativo")
    pending_count = sum(1 for x in visible_profiles if x.get("status") == "pendente") if role == "admin" else 0
except Exception as exc:
    athletes_count=tech_count=pending_count=0; visible_teams=[]; visible_trainings=[]
    st.warning(f"Não foi possível atualizar a Central da equipe: {exc}")
items=[("👥",athletes_count,"Atletas","sp-blue"),("🧑‍🏫",tech_count,"Equipe técnica","sp-green"),("🛹",len(visible_teams),"Times","sp-purple"),("📊",len(visible_trainings),"Treinos","sp-orange")]
if role=="admin": items.append(("🔔",pending_count,"Pendentes","sp-red"))
cols=st.columns(len(items))
for col,(ico,num,label,klass) in zip(cols,items):
    col.markdown(f"<div class='sp-kpi {klass}'><div class='sp-icon'>{ico}</div><div class='sp-num'>{num}</div><div class='sp-name'>{label}</div><div class='sp-hint'>Acessar →</div></div>",unsafe_allow_html=True)
st.markdown("<div class='sp-section'>Acesso rápido</div>",unsafe_allow_html=True)
q1,q2,q3,q4=st.columns(4)
with q1:
    st.markdown("<div class='sp-quick'><div class='sp-quick-icon'>🛹</div><div class='sp-quick-title'>Times</div><div class='sp-quick-sub'>Veja sua equipe e os membros</div></div>",unsafe_allow_html=True)
    if st.button("Abrir Times →",key="home_times",use_container_width=True): st.switch_page("pages/02_Times.py")
with q2:
    st.markdown("<div class='sp-quick'><div class='sp-quick-icon'>🗓️</div><div class='sp-quick-title'>Histórico</div><div class='sp-quick-sub'>Treinos e relatórios salvos</div></div>",unsafe_allow_html=True)
    if st.button("Abrir Histórico →",key="home_hist",use_container_width=True): st.switch_page("pages/04_Historico_de_Treinos.py")
with q3:
    if role not in ("skatista","familiar"):
        st.markdown("<div class='sp-quick'><div class='sp-quick-icon'>📈</div><div class='sp-quick-title'>Nova Análise</div><div class='sp-quick-sub'>Analisar um novo CSV</div></div>",unsafe_allow_html=True)
        if st.button("Nova Análise →",key="home_analysis",use_container_width=True): st.switch_page("pages/03_Analise_de_Treino.py")
    else:
        st.markdown("<div class='sp-quick'><div class='sp-quick-icon'>👁️</div><div class='sp-quick-title'>Meus Treinos</div><div class='sp-quick-sub'>Visualize suas análises</div></div>",unsafe_allow_html=True)
        if st.button("Ver Treinos →",key="home_mytrain",use_container_width=True): st.switch_page("pages/04_Historico_de_Treinos.py")
with q4:
    st.markdown("<div class='sp-quick'><div class='sp-quick-icon'>👤</div><div class='sp-quick-title'>Meu Perfil</div><div class='sp-quick-sub'>Foto e informações pessoais</div></div>",unsafe_allow_html=True)
    if st.button("Abrir Perfil →",key="home_profile",use_container_width=True): st.switch_page("pages/05_Meu_Perfil.py")
if role == "admin":
    st.success("🛡️ Você está conectado como ADMINISTRADOR. Use Cadastros para aprovar usuários.")
elif role in ("tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica"):
    st.info("🎯 Perfil TÉCNICO: você acessa somente os times e skatistas vinculados a você.")
else:
    st.info("🛹 Perfil SKATISTA: seu acesso é limitado ao próprio perfil e ao Histórico de Treinos.")
