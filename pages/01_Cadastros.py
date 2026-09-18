
import streamlit as st
from auth_utils import require_login, get_supabase, load_profile
st.set_page_config(page_title="Cadastros • Skate Performance", page_icon="👥", layout="wide")
st.markdown("""<style>
[data-testid="stHeader"],header[data-testid="stHeader"],[data-testid="stToolbar"]{display:none!important}
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}
[data-testid="stSidebar"]{background:#081827!important}[data-testid="stSidebar"] *{color:#d9eafa!important}
.block-container{padding-top:1.2rem!important} h1,h2,h3,p,label{color:#eef8ff}
</style>""",unsafe_allow_html=True)
user, me = require_login(admin=True)
sb = get_supabase()

st.title("👥 Cadastros e permissões")
st.caption("Aprove, bloqueie e gerencie skatistas e técnicos.")

try:
    rows = sb.table("profiles").select("*").order("created_at", desc=True).execute().data or []
except Exception:
    rows = []

pending = [r for r in rows if r.get("status")=="pendente"]
active = [r for r in rows if r.get("status")=="ativo"]
blocked = [r for r in rows if r.get("status")=="bloqueado"]

t1,t2,t3=st.tabs([f"PENDENTES ({len(pending)})",f"ATIVOS ({len(active)})",f"BLOQUEADOS ({len(blocked)})"])

def render_people(items, mode):
    if not items:
        st.info("Nenhum cadastro nesta categoria.")
        return
    for r in items:
        with st.container(border=True):
            a,b,c,d=st.columns([3,2,2,2])
            a.markdown(f"**{r.get('full_name','—')}**")
            a.caption(r.get("email") or "Sem e-mail")
            b.write((r.get("role") or "—").upper())
            b.caption(r.get("modality") or "—")
            if mode=="pending":
                if c.button("✅ Aprovar",key=f"ap_{r['id']}",use_container_width=True):
                    sb.table("profiles").update({"status":"ativo"}).eq("id",r["id"]).execute(); st.rerun()
                if d.button("⛔ Bloquear",key=f"bl_{r['id']}",use_container_width=True):
                    sb.table("profiles").update({"status":"bloqueado"}).eq("id",r["id"]).execute(); st.rerun()
            elif mode=="active":
                if d.button("⛔ Bloquear",key=f"bla_{r['id']}",use_container_width=True):
                    sb.table("profiles").update({"status":"bloqueado"}).eq("id",r["id"]).execute(); st.rerun()
            else:
                if d.button("♻️ Reativar",key=f"re_{r['id']}",use_container_width=True):
                    sb.table("profiles").update({"status":"ativo"}).eq("id",r["id"]).execute(); st.rerun()

with t1: render_people(pending,"pending")
with t2: render_people(active,"active")
with t3: render_people(blocked,"blocked")
