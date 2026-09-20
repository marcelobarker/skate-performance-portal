from datetime import date
import streamlit as st
from auth_utils import require_login, get_supabase

st.set_page_config(page_title="Times • Skate Performance", page_icon="🛹", layout="wide")
st.markdown("""<style>
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}[data-testid="stSidebar"]{background:#081827!important}[data-testid="stSidebar"] *{color:#d9eafa!important}[data-testid="stHeader"],[data-testid="stToolbar"]{display:none!important}.block-container{padding-top:1.2rem!important}h1,h2,h3,p,label{color:#eef8ff!important}
[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button{background:#0b1d31!important;color:#eef8ff!important;border:1px solid #245274!important;border-radius:10px!important}
[data-testid="stTextInput"] input,[data-testid="stSelectbox"]>div>div,[data-testid="stMultiSelect"]>div>div{background:#0b1d2d!important;color:#eef8ff!important;border-color:#24445d!important}
.member{border-top:1px solid #173b5a;padding:12px 0}.member:first-child{border-top:0}
</style>""",unsafe_allow_html=True)
user,profile=require_login(); sb=get_supabase(); is_admin=profile.get("role")=="admin"
ROLE_LABELS={"admin":"Admin","skatista":"Atleta","tecnico":"Técnico","presidente":"Presidente","vice_presidente":"Vice-presidente","chefe_equipe":"Chefe de Equipe","comissao_tecnica":"Comissão Técnica","familiar":"Familiar"}
STAFF_ROLES={"admin","tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica"}
@st.dialog("Foto do membro")
def show_photo(name,url):
    st.markdown(f"### {name}")
    st.image(url,use_container_width=True)
st.title("🛹 Times"); st.caption("Equipe, técnicos e skatistas vinculados a cada time.")

def age(v):
    if not v:return None
    try:
        b=date.fromisoformat(v); t=date.today(); return t.year-b.year-((t.month,t.day)<(b.month,b.day))
    except:return None

def fetch_data():
    try:
        if is_admin:
            members=sb.table("team_members").select("team_id,profile_id").execute().data or []; teams=sb.table("teams").select("*").order("name").execute().data or []
        else:
            mine=sb.table("team_members").select("team_id,profile_id").eq("profile_id",user.id).execute().data or []; tids=[m["team_id"] for m in mine]; teams=[]; members=[]
            for tid in tids:
                t=sb.table("teams").select("*").eq("id",tid).maybe_single().execute()
                if t and t.data: teams.append(t.data)
                members += sb.table("team_members").select("team_id,profile_id").eq("team_id",tid).execute().data or []
        profiles=sb.table("profiles").select("id,full_name,email,role,status,modality,stance,photo_url,birth_date,city,state").eq("status","ativo").order("full_name").execute().data or []
        return teams,profiles,members
    except Exception as exc: st.error(f"Não foi possível carregar os times: {exc}"); return [],[],[]

def label_person(p):
    role=ROLE_LABELS.get(p.get("role"),p.get("role", "")); return f"{p.get('full_name') or p.get('email') or 'Sem nome'} • {role}"

if is_admin:
    with st.expander("➕ Criar novo time"):
        with st.form("new_team",clear_on_submit=True):
            c1,c2=st.columns([2,1]); name=c1.text_input("Nome do time"); modality=c2.selectbox("Modalidade",["Street","Park","Vert","Misto"]); create=st.form_submit_button("Criar time",use_container_width=True)
        if create and name.strip(): sb.table("teams").insert({"name":name.strip(),"modality":modality}).execute(); st.rerun()
teams,profiles,memberships=fetch_data(); byid={p["id"]:p for p in profiles}
if not teams: st.info("Nenhum time cadastrado ainda."); st.stop()
for team in teams:
    tid=team["id"]; ids=[m["profile_id"] for m in memberships if m["team_id"]==tid]; people=[byid[x] for x in ids if x in byid]; athletes=[p for p in people if p.get("role")=="skatista"]; staff=[p for p in people if p.get("role") in STAFF_ROLES]
    with st.container(border=True):
        a,b,c=st.columns([4,1.2,1.2]); a.markdown(f"## {team.get('name','Time')}"); a.caption(f"Modalidade: {team.get('modality') or '—'}"); b.metric("Skatistas",len(athletes)); c.metric("Técnicos",len(staff))
        st.markdown("### 👥 Membros do time")
        if not people: st.caption("Este time ainda não possui membros.")
        for p in sorted(people,key=lambda x:(0 if x.get('role') in STAFF_ROLES else 1,(x.get('full_name') or '').lower())):
            pc,ic=st.columns([1,5])
            with pc:
                if p.get("photo_url"):
                    st.image(p["photo_url"],width=95)
                    if st.button("👁",key=f"eye_{tid}_{p['id']}",help="Ampliar foto"):
                        show_photo(p.get("full_name") or "Membro",p["photo_url"])
                else: st.markdown("### 👤")
            with ic:
                role_label=ROLE_LABELS.get(p.get("role"),p.get("role","")).upper()
                st.markdown(f"#### {p.get('full_name') or 'Sem nome'}  ·  {role_label}")
                loc=" / ".join([x for x in [p.get('city'),p.get('state')] if x]) or "—"
                if p.get("role")=="skatista":
                    years=age(p.get("birth_date")); st.write(f"**Idade:** {str(years)+' anos' if years is not None else '—'}   |   **Base:** {p.get('stance') or '—'}   |   **Cidade:** {loc}")
                    st.caption(f"Modalidade: {p.get('modality') or '—'}")
                else:
                    st.write(f"**Função:** {ROLE_LABELS.get(p.get('role'),p.get('role','—'))}   |   **Cidade:** {loc}")
            st.divider()
        if is_admin:
            with st.expander("⚙️ Gerenciar time"):
                with st.form(f"edit_{tid}"):
                    e1,e2=st.columns([2,1]); nn=e1.text_input("Nome",value=team.get("name") or ""); mods=["Street","Park","Vert","Misto"]; cm=team.get("modality") if team.get("modality") in mods else "Misto"; nm=e2.selectbox("Modalidade",mods,index=mods.index(cm)); save=st.form_submit_button("💾 Salvar dados",use_container_width=True)
                if save: sb.table("teams").update({"name":nn.strip() or team.get("name"),"modality":nm}).eq("id",tid).execute(); st.rerun()
                opts={label_person(p):p["id"] for p in profiles}; defaults=[label_person(p) for p in people if label_person(p) in opts]
                with st.form(f"members_{tid}"):
                    sel=st.multiselect("Membros do time",list(opts),default=defaults); sm=st.form_submit_button("👥 Salvar membros",use_container_width=True)
                if sm:
                    new={opts[x] for x in sel}; old=set(ids)
                    for pid in old-new: sb.table("team_members").delete().eq("team_id",tid).eq("profile_id",pid).execute()
                    rows=[{"team_id":tid,"profile_id":pid} for pid in new-old]
                    if rows: sb.table("team_members").insert(rows).execute()
                    st.rerun()
