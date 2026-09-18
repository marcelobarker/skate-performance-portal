
import streamlit as st
from auth_utils import sign_in, sign_up, sign_out, current_user, current_profile, load_profile

st.set_page_config(page_title="Skate Performance • Portal", page_icon="🛹", layout="wide")

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
            submit = st.form_submit_button("Entrar", use_container_width=True)
        if submit:
            try:
                sign_in(email, password)
                st.success("Login realizado.")
                st.rerun()
            except Exception:
                st.error("Não foi possível entrar. Confira e-mail, senha e se o e-mail já foi confirmado.")

    with signup_tab:
        with st.form("signup_form"):
            full_name = st.text_input("Nome completo")
            email2 = st.text_input("E-mail")
            password2 = st.text_input("Senha", type="password", help="Use pelo menos 6 caracteres.")
            role_label = st.selectbox("Quero me cadastrar como", ["Skatista", "Técnico"])
            modality = st.selectbox("Modalidade principal", ["Street","Park","Vert","Outro"])
            accept = st.checkbox("Confirmo que os dados acima estão corretos.")
            create = st.form_submit_button("Solicitar cadastro", use_container_width=True)
        if create:
            if not full_name.strip() or not email2.strip() or len(password2) < 6 or not accept:
                st.error("Preencha os campos, use uma senha com pelo menos 6 caracteres e confirme os dados.")
            else:
                try:
                    role = "skatista" if role_label == "Skatista" else "tecnico"
                    res = sign_up(full_name, email2, password2, role, modality)
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

st.header("Central da equipe")
c1,c2,c3,c4=st.columns(4)
c1.metric("Atletas","—"); c2.metric("Técnicos","—"); c3.metric("Times","—"); c4.metric("Pendentes","—")

a,b,c=st.columns(3)
with a: st.markdown('<div class="card"><h3>👤 Atletas</h3><div class="muted">Perfis, modalidade, stance, categoria e histórico.</div></div>',unsafe_allow_html=True)
with b: st.markdown('<div class="card"><h3>🧑‍🏫 Técnicos</h3><div class="muted">Acesso aos atletas e times autorizados.</div></div>',unsafe_allow_html=True)
with c: st.markdown('<div class="card"><h3>🛹 Times</h3><div class="muted">Organização dos grupos Street, Park, Vert ou mistos.</div></div>',unsafe_allow_html=True)

if role == "admin":
    st.success("🛡️ Você está conectado como ADMINISTRADOR. Use Cadastros para aprovar usuários.")
elif role == "tecnico":
    st.info("🎯 Perfil TÉCNICO: você acessa somente os times e skatistas vinculados a você.")
else:
    st.info("🛹 Perfil SKATISTA: seu acesso é limitado ao seu próprio perfil, análises e histórico.")
