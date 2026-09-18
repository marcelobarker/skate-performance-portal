
import streamlit as st
from datetime import date

st.set_page_config(page_title="Skate Performance • Portal", page_icon="🛹", layout="wide")

st.markdown("""
<style>
.stApp {background:#06111f;color:#eef8ff}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {color:#eef8ff !important}
[data-testid="stAppViewContainer"] > .main {background:#06111f !important}
[data-testid="stHeader"] {background:transparent !important; height:0 !important}
[data-testid="stToolbar"] {display:none !important}
[data-testid="stDecoration"] {display:none !important}
header[data-testid="stHeader"] {display:none !important}
#MainMenu {visibility:hidden !important}
.block-container {padding-top:1.2rem !important}
h1,h2,h3,h4,h5,h6,p,span,label,div { }
[data-testid="stMetricLabel"] p,
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {color:#eef8ff !important}
[data-testid="stCaptionContainer"] p {color:#9bb2c8 !important}
[data-testid="stSidebar"] * {color:#d9eafa !important}

[data-testid="stSidebar"] {background:#081827}
.block-container {max-width:1400px;padding-top:1.2rem !important}
.hero{background:#0b1d31;border:1px solid #173b5a;border-radius:18px;padding:24px 28px;margin-bottom:18px}
.brand{font-size:31px;font-weight:900;font-style:italic;letter-spacing:-1px}
.brand .blue{color:#1398ff}.brand .time{font-size:15px;font-style:normal;margin-left:8px}
.sub{color:#6bc1f7;font-size:11px;letter-spacing:.7px}
.card{background:#0b1d31;border:1px solid #173b5a;border-radius:16px;padding:20px;height:155px}
.card h3{margin:0 0 8px}.muted{color:#9bb2c8}
div[data-testid="stMetric"]{background:#0b1d31;border:1px solid #173b5a;padding:14px;border-radius:14px}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="brand">SKATE<span class="blue">PERFORMANCE</span><span class="time">TIME BRASIL</span></div>
  <div class="sub">ATHLETE MANAGEMENT • TRAINING INTELLIGENCE</div>
</div>
""", unsafe_allow_html=True)

st.title("Central da equipe")
st.caption("Novo espaço de gestão. O dashboard de análise original foi preservado como uma página separada.")

c1,c2,c3,c4=st.columns(4)
c1.metric("Atletas","—")
c2.metric("Técnicos","—")
c3.metric("Times","—")
c4.metric("Cadastros pendentes","—")

st.info("🔐 O portal está preparado para receber autenticação e banco Supabase. Até conectar o banco, nenhum cadastro real é gravado.")

a,b,c=st.columns(3)
with a:
    st.markdown('<div class="card"><h3>👤 Atletas</h3><div class="muted">Cadastro, foto, modalidade, stance, categoria e histórico de treinos.</div></div>',unsafe_allow_html=True)
with b:
    st.markdown('<div class="card"><h3>🧑‍🏫 Técnicos</h3><div class="muted">Perfis de técnicos e acesso aos atletas/times autorizados.</div></div>',unsafe_allow_html=True)
with c:
    st.markdown('<div class="card"><h3>🛹 Times</h3><div class="muted">Organize Street, Park ou qualquer grupo de trabalho.</div></div>',unsafe_allow_html=True)

st.markdown("### Fluxo planejado")
st.write("Pessoa cria conta → você recebe como **PENDENTE** → aprova como **SKATISTA** ou **TÉCNICO** → vincula ao time → treinos e análises ficam associados ao perfil.")
