
import streamlit as st
st.set_page_config(page_title="Cadastros • Skate Performance", page_icon="👥", layout="wide")
st.title("👥 Cadastros e permissões")
st.caption("Painel reservado para o administrador.")

st.warning("Banco ainda não conectado. Esta tela é a estrutura visual do próximo passo.")

tab1,tab2,tab3=st.tabs(["Pendentes","Pessoas","Novo cadastro"])
with tab1:
    st.subheader("Solicitações pendentes")
    st.info("Quando o Supabase estiver conectado, aparecerão aqui os novos skatistas e técnicos aguardando sua aprovação.")
with tab2:
    st.subheader("Pessoas cadastradas")
    st.dataframe({"Nome":[],"Tipo":[],"Time":[],"Status":[]},use_container_width=True)
with tab3:
    c1,c2=st.columns(2)
    with c1:
        st.text_input("Nome completo")
        st.text_input("E-mail")
        st.selectbox("Perfil",["Skatista","Técnico"])
    with c2:
        st.selectbox("Modalidade",["Street","Park","Vert","Outro"])
        st.text_input("Time")
        st.selectbox("Status",["Pendente","Ativo","Bloqueado"])
    st.button("Salvar cadastro",disabled=True,help="Será habilitado quando o banco estiver conectado.")
