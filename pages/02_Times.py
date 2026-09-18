
import streamlit as st
from auth_utils import require_login, get_supabase
st.set_page_config(page_title="Times • Skate Performance",page_icon="🛹",layout="wide")
st.markdown("""<style>
[data-testid="stHeader"],header[data-testid="stHeader"],[data-testid="stToolbar"]{display:none!important}
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}
[data-testid="stSidebar"]{background:#081827!important}[data-testid="stSidebar"] *{color:#d9eafa!important}
.block-container{padding-top:1.2rem!important} h1,h2,h3,p,label{color:#eef8ff}
</style>""",unsafe_allow_html=True)
user, profile = require_login()
sb=get_supabase()
st.title("🛹 Times")
st.caption("Times cadastrados no Skate Performance.")

try:
    teams=sb.table("teams").select("*").order("name").execute().data or []
except Exception:
    teams=[]

if profile.get("role")=="admin":
    with st.form("new_team"):
        a,b=st.columns(2)
        name=a.text_input("Nome do time",placeholder="Ex.: Seleção Street")
        modality=b.selectbox("Modalidade",["Street","Park","Vert","Misto"])
        create=st.form_submit_button("Criar time")
    if create and name.strip():
        sb.table("teams").insert({"name":name.strip(),"modality":modality}).execute()
        st.success("Time criado."); st.rerun()

if teams:
    st.dataframe([{"Time":x["name"],"Modalidade":x.get("modality","")} for x in teams],use_container_width=True,hide_index=True)
else:
    st.info("Nenhum time cadastrado ainda.")
