import re
from datetime import date, timedelta
import streamlit as st
from auth_utils import require_login, get_supabase

st.set_page_config(page_title="Histórico • Skate Performance", page_icon="📚", layout="wide")

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
[data-testid="stSelectbox"]>div>div{background:#0b1d2d!important;color:#eef8ff!important;border-color:#24445d!important}
</style>""", unsafe_allow_html=True)

user, profile = require_login()
sb = get_supabase()
role = profile.get("role")
is_admin = role == "admin"
is_technician = role == "tecnico"

st.title("📚 Histórico de Treinos")
st.caption("Sessões, CSVs e relatórios vinculados a cada skatista.")

try:
    if is_admin or is_technician:
        athletes = (sb.table("profiles")
                    .select("id,full_name,modality,status,role")
                    .eq("role", "skatista").eq("status", "ativo")
                    .order("full_name").execute().data or [])
        if not athletes:
            msg = "Ainda não há skatistas cadastrados para consultar." if is_admin else "Nenhum skatista do seu time está disponível para consulta."
            st.info(msg); st.stop()
        amap = {f"{a.get('full_name') or 'Sem nome'}" + (f" • {a.get('modality')}" if a.get('modality') else ""): a for a in athletes}
        label = st.selectbox("Skatista", list(amap.keys()))
        athlete = amap[label]; athlete_id = athlete["id"]
    else:
        athlete_id = user.id; athlete = profile

    period = st.selectbox("Período", ["Todos", "Últimos 30 dias", "Últimos 90 dias", "Este ano", "Personalizado"])
    query = (sb.table("training_sessions")
             .select("id,athlete_id,training_date,title,csv_path,report_pdf_path,visual_pdf_path,created_at")
             .eq("athlete_id", athlete_id))
    today = date.today()
    if period == "Últimos 30 dias": query = query.gte("training_date", (today-timedelta(days=30)).isoformat())
    elif period == "Últimos 90 dias": query = query.gte("training_date", (today-timedelta(days=90)).isoformat())
    elif period == "Este ano": query = query.gte("training_date", date(today.year,1,1).isoformat())
    elif period == "Personalizado":
        c1,c2=st.columns(2)
        start=c1.date_input("De", value=today-timedelta(days=30), key="history_start")
        end=c2.date_input("Até", value=today, key="history_end")
        if start>end: st.warning("A data inicial precisa ser anterior à data final."); st.stop()
        query=query.gte("training_date",start.isoformat()).lte("training_date",end.isoformat())
    rows = query.order("training_date", desc=True).order("created_at", desc=True).execute().data or []
except Exception as exc:
    st.error(f"Não foi possível carregar o histórico: {exc}"); st.stop()

st.markdown(f"### {athlete.get('full_name') or 'Skatista'}")
if not rows:
    st.info("Nenhum treino salvo para este skatista neste período."); st.stop()

st.metric("Treinos salvos", len(rows))
for row in rows:
    with st.container(border=True):
        c1,c2=st.columns([4,1]); c1.markdown(f"#### {row.get('title') or 'Treino'}")
        c1.caption(f"Data do treino: {row.get('training_date') or '—'}"); c2.caption("ARQUIVOS DA SESSÃO")
        safe=re.sub(r"[^A-Za-z0-9_-]+","_",row.get('title') or 'treino')
        b1,b2,b3=st.columns(3)
        if row.get("csv_path"):
            try:
                data=sb.storage.from_("training-csvs").download(row["csv_path"])
                b1.download_button("⬇ CSV",data=data,file_name=f"{safe}.csv",mime="text/csv",key=f"csv_{row['id']}",use_container_width=True)
            except Exception as exc: b1.caption(f"CSV indisponível: {exc}")
        if row.get("report_pdf_path"):
            try:
                data=sb.storage.from_("training-reports").download(row["report_pdf_path"])
                b2.download_button("⬇ RELATÓRIO PDF",data=data,file_name=f"{safe}_relatorio.pdf",mime="application/pdf",key=f"report_{row['id']}",use_container_width=True)
            except Exception as exc: b2.caption(f"Relatório indisponível: {exc}")
        else: b2.caption("PDF não arquivado (sessão anterior à V1.9)")
        if row.get("visual_pdf_path"):
            try:
                data=sb.storage.from_("training-reports").download(row["visual_pdf_path"])
                b3.download_button("⬇ DASHBOARD VISUAL",data=data,file_name=f"{safe}_dashboard_visual.pdf",mime="application/pdf",key=f"visual_{row['id']}",use_container_width=True)
            except Exception as exc: b3.caption(f"Dashboard indisponível: {exc}")
        else: b3.caption("PDF visual não arquivado (sessão anterior à V1.9)")

        if is_admin:
            confirm=st.checkbox("Confirmar exclusão",key=f"confirm_{row['id']}")
            if st.button("🗑️ Excluir do histórico",key=f"delete_{row['id']}",disabled=not confirm):
                try:
                    if row.get("csv_path"): sb.storage.from_("training-csvs").remove([row["csv_path"]])
                    report_paths=[p for p in [row.get("report_pdf_path"),row.get("visual_pdf_path")] if p]
                    if report_paths: sb.storage.from_("training-reports").remove(report_paths)
                    sb.table("training_sessions").delete().eq("id",row["id"]).execute()
                    st.success("Treino e arquivos associados excluídos."); st.rerun()
                except Exception as exc: st.error(f"Não foi possível excluir: {exc}")
