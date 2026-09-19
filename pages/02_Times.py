import streamlit as st
from auth_utils import require_login, get_supabase

st.set_page_config(page_title="Times • Skate Performance", page_icon="🛹", layout="wide")

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
</style>""", unsafe_allow_html=True)
st.markdown("""<style>
[data-testid="stHeader"],header[data-testid="stHeader"],[data-testid="stToolbar"]{display:none!important}
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}
[data-testid="stSidebar"]{background:#081827!important}[data-testid="stSidebar"] *{color:#d9eafa!important}
.block-container{padding-top:1.2rem!important} h1,h2,h3,p,label{color:#eef8ff!important}
[data-testid="stTextInput"] input,[data-testid="stSelectbox"]>div>div,[data-testid="stMultiSelect"]>div>div{
 background:#0b1d2d!important;color:#eef8ff!important;border-color:#24445d!important
}
div[data-testid="stButton"] button{border-radius:10px!important}
</style>""", unsafe_allow_html=True)

user, profile = require_login()
sb = get_supabase()
is_admin = profile.get("role") == "admin"

st.title("🛹 Times")
st.caption("Monte as equipes e vincule skatistas e técnicos cadastrados.")


def fetch_data():
    try:
        # Para não-admin, parte primeiro dos vínculos do próprio usuário. Isso evita
        # que uma listagem ampla seja esvaziada pelo RLS e pareça que ele não tem time.
        if is_admin:
            members = sb.table("team_members").select("team_id,profile_id").execute().data or []
            teams = sb.table("teams").select("*").order("name").execute().data or []
        else:
            mine = sb.table("team_members").select("team_id,profile_id").eq("profile_id", user.id).execute().data or []
            tids = [m["team_id"] for m in mine]
            teams=[]; members=[]
            for tid in tids:
                t=sb.table("teams").select("*").eq("id",tid).maybe_single().execute()
                if t and t.data: teams.append(t.data)
                members += sb.table("team_members").select("team_id,profile_id").eq("team_id",tid).execute().data or []
        profiles = sb.table("profiles").select("id,full_name,email,role,status,modality,photo_url").eq("status", "ativo").order("full_name").execute().data or []
        return teams, profiles, members
    except Exception as exc:
        st.error(f"Não foi possível carregar os times: {exc}")
        return [], [], []


def label_person(p):
    role = {"skatista": "Skatista", "tecnico": "Técnico", "admin": "Admin"}.get(p.get("role"), p.get("role", ""))
    return f"{p.get('full_name') or p.get('email') or 'Sem nome'} • {role}"


if is_admin:
    with st.expander("➕ Criar novo time", expanded=False):
        with st.form("new_team", clear_on_submit=True):
            c1, c2 = st.columns([2, 1])
            name = c1.text_input("Nome do time", placeholder="Ex.: Seleção Brasileira Street")
            modality = c2.selectbox("Modalidade", ["Street", "Park", "Vert", "Misto"])
            create = st.form_submit_button("Criar time", use_container_width=True)
        if create:
            if not name.strip():
                st.warning("Digite o nome do time.")
            else:
                try:
                    sb.table("teams").insert({"name": name.strip(), "modality": modality}).execute()
                    st.success("Time criado.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Não foi possível criar o time: {exc}")

teams, profiles, memberships = fetch_data()
profiles_by_id = {p["id"]: p for p in profiles}

if not teams:
    st.info("Nenhum time cadastrado ainda.")
    st.stop()

for team in teams:
    team_id = team["id"]
    member_ids = [m["profile_id"] for m in memberships if m["team_id"] == team_id]
    team_people = [profiles_by_id[x] for x in member_ids if x in profiles_by_id]
    athletes = [p for p in team_people if p.get("role") == "skatista"]
    staff = [p for p in team_people if p.get("role") in ("tecnico", "admin")]

    with st.container(border=True):
        h1, h2, h3 = st.columns([4, 1.4, 1.4])
        h1.markdown(f"### {team.get('name', 'Time')}")
        h1.caption(f"Modalidade: {team.get('modality') or '—'}")
        h2.metric("Skatistas", len(athletes))
        h3.metric("Técnicos", len(staff))

        if team_people:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Skatistas**")
                if athletes:
                    for p in athletes:
                        st.write(f"🛹 {p.get('full_name') or 'Sem nome'}")
                else:
                    st.caption("Nenhum skatista neste time.")
            with c2:
                st.markdown("**Técnicos / staff**")
                if staff:
                    for p in staff:
                        st.write(f"🎯 {p.get('full_name') or 'Sem nome'}")
                else:
                    st.caption("Nenhum técnico neste time.")
        else:
            st.caption("Este time ainda não possui membros.")

        if is_admin:
            with st.expander("⚙️ Gerenciar time"):
                with st.form(f"edit_team_{team_id}"):
                    e1, e2 = st.columns([2, 1])
                    new_name = e1.text_input("Nome", value=team.get("name") or "", key=f"name_{team_id}")
                    mods = ["Street", "Park", "Vert", "Misto"]
                    current_mod = team.get("modality") if team.get("modality") in mods else "Misto"
                    new_modality = e2.selectbox("Modalidade", mods, index=mods.index(current_mod), key=f"mod_{team_id}")
                    save_team = st.form_submit_button("💾 Salvar dados do time", use_container_width=True)
                if save_team:
                    try:
                        sb.table("teams").update({"name": new_name.strip() or team.get("name"), "modality": new_modality}).eq("id", team_id).execute()
                        st.success("Time atualizado.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Não foi possível atualizar: {exc}")

                eligible = [p for p in profiles if p.get("role") in ("skatista", "tecnico", "admin")]
                option_map = {label_person(p): p["id"] for p in eligible}
                current_labels = [label_person(p) for p in team_people if label_person(p) in option_map]
                with st.form(f"members_{team_id}"):
                    selected_labels = st.multiselect(
                        "Membros do time",
                        options=list(option_map.keys()),
                        default=current_labels,
                        help="Selecione skatistas e técnicos ativos que pertencem a este time.",
                    )
                    save_members = st.form_submit_button("👥 Salvar membros", use_container_width=True)
                if save_members:
                    try:
                        selected_ids = {option_map[x] for x in selected_labels}
                        old_ids = set(member_ids)
                        for pid in old_ids - selected_ids:
                            sb.table("team_members").delete().eq("team_id", team_id).eq("profile_id", pid).execute()
                        rows = [{"team_id": team_id, "profile_id": pid} for pid in selected_ids - old_ids]
                        if rows:
                            sb.table("team_members").insert(rows).execute()
                        st.success("Membros atualizados.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Não foi possível atualizar os membros: {exc}")

                st.divider()
                confirm = st.checkbox(
                    f"Confirmo que quero excluir {team.get('name', 'este time')}",
                    key=f"confirm_delete_{team_id}",
                )
                if st.button("🗑️ Excluir time", key=f"delete_{team_id}", disabled=not confirm, use_container_width=True):
                    try:
                        sb.table("teams").delete().eq("id", team_id).execute()
                        st.success("Time excluído.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Não foi possível excluir o time: {exc}")
