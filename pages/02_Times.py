
import streamlit as st
st.set_page_config(page_title="Times • Skate Performance",page_icon="🛹",layout="wide")
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
