
import streamlit as st
st.set_page_config(page_title="Times • Skate Performance",page_icon="🛹",layout="wide")

st.markdown("""
<style>
[data-testid="stHeader"], header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {display:none !important}
.block-container {padding-top:1.2rem !important}
.stApp, [data-testid="stAppViewContainer"] {background:#06111f !important;color:#eef8ff !important}
[data-testid="stSidebar"] {background:#081827 !important}
[data-testid="stSidebar"] * {color:#d9eafa !important}
h1,h2,h3,h4,h5,h6,p,label {color:#eef8ff}
[data-testid="stCaptionContainer"] p {color:#9bb2c8 !important}
</style>
""", unsafe_allow_html=True)
st.title("🛹 Times")
st.caption("Crie grupos e vincule atletas e técnicos.")
st.warning("Banco ainda não conectado.")
a,b=st.columns([1,2])
with a:
    st.text_input("Nome do time",placeholder="Ex.: Seleção Street")
    st.selectbox("Modalidade",["Street","Park","Vert","Misto"])
    st.button("Criar time",disabled=True)
with b:
    st.subheader("Times cadastrados")
    st.dataframe({"Time":[],"Modalidade":[],"Atletas":[],"Técnicos":[]},use_container_width=True)
