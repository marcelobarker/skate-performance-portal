import streamlit as st
from auth_utils import require_login, get_supabase

st.set_page_config(page_title="Histórico • Skate Performance", page_icon="📚", layout="wide")
st.markdown("""<style>
[data-testid="stHeader"],header[data-testid="stHeader"],[data-testid="stToolbar"]{display:none!important}
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}
[data-testid="stSidebar"]{background:#081827!important}[data-testid="stSidebar"] *{color:#d9eafa!important}
.block-container{padding-top:1.2rem!important} h1,h2,h3,p,label{color:#eef8ff!important}
[data-testid="stSelectbox"]>div>div{background:#0b1d2d!important;color:#eef8ff!important;border-color:#24445d!important}
</style>""", unsafe_allow_html=True)

user, profile = require_login()
sb = get_supabase()
role = profile.get("role")
is_admin = role == "admin"
is_technician = role == "tecnico"

st.title("📚 Histórico de Treinos")
st.caption("Sessões salvas permanentemente e vinculadas a cada skatista.")

try:
    if is_admin or is_technician:
        athletes = (sb.table("profiles")
                    .select("id,full_name,modality,status,role")
                    .eq("role", "skatista").eq("status", "ativo")
                    .order("full_name").execute().data or [])
        if not athletes:
            msg = "Ainda não há skatistas cadastrados para consultar." if is_admin else "Nenhum skatista do seu time está disponível para consulta."
            st.info(msg)
            st.stop()
        amap = {f"{a.get('full_name') or 'Sem nome'}" + (f" • {a.get('modality')}" if a.get('modality') else ""): a for a in athletes}
        label = st.selectbox("Skatista", list(amap.keys()))
        athlete = amap[label]
        athlete_id = athlete["id"]
    else:
        athlete_id = user.id
        athlete = profile

    rows = (sb.table("training_sessions")
            .select("id,athlete_id,training_date,title,csv_path,created_at")
            .eq("athlete_id", athlete_id)
            .order("training_date", desc=True)
            .order("created_at", desc=True)
            .execute().data or [])
except Exception as exc:
    st.error(f"Não foi possível carregar o histórico: {exc}")
    st.stop()

st.markdown(f"### {athlete.get('full_name') or 'Skatista'}")
if not rows:
    st.info("Nenhum treino salvo para este skatista ainda.")
    st.stop()

st.metric("Treinos salvos", len(rows))

for row in rows:
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"#### {row.get('title') or 'Treino'}")
        c1.caption(f"Data do treino: {row.get('training_date') or '—'}")
        c2.caption("CSV armazenado")

        if row.get("csv_path"):
            try:
                data = sb.storage.from_("training-csvs").download(row["csv_path"])
                st.download_button(
                    "⬇ Baixar CSV",
                    data=data,
                    file_name=f"{(row.get('title') or 'treino').replace('/', '-')}.csv",
                    mime="text/csv",
                    key=f"download_{row['id']}",
                )
            except Exception as exc:
                st.caption(f"Arquivo indisponível: {exc}")

        if is_admin:
            confirm = st.checkbox("Confirmar exclusão", key=f"confirm_{row['id']}")
            if st.button("🗑️ Excluir do histórico", key=f"delete_{row['id']}", disabled=not confirm):
                try:
                    if row.get("csv_path"):
                        sb.storage.from_("training-csvs").remove([row["csv_path"]])
                    sb.table("training_sessions").delete().eq("id", row["id"]).execute()
                    st.success("Treino excluído.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Não foi possível excluir: {exc}")
