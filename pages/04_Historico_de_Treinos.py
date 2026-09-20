import re
import io, zipfile
from datetime import date, timedelta
import streamlit as st
from auth_utils import require_login, get_supabase
from report_engine import read_csv, is_aggregate, parse_raw, parse_aggregate, merge_sessions, make_pdf, make_visual_pdf

from ui_theme import apply_ui_theme

st.set_page_config(page_title="Histórico • Skate Performance", page_icon="📚", layout="wide")
apply_ui_theme()

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
[data-testid="stToolbar"]{display:none!important}
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}
[data-testid="stSidebar"]{background:#081827!important}[data-testid="stSidebar"] *{color:#d9eafa!important}
.block-container{padding-top:1.2rem!important} h1,h2,h3,p,label{color:#eef8ff!important}
[data-testid="stSelectbox"]>div>div{background:#0b1d2d!important;color:#eef8ff!important;border-color:#24445d!important}
</style>""", unsafe_allow_html=True)

user, profile = require_login()
sb = get_supabase()
role = profile.get("role")
is_admin = role == "admin"
is_technician = role in ("tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica")
is_family = role == "familiar"


st.markdown('''<style>
/* V3.6 histórico: cards mais compactos e ações legíveis */
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px!important;border-color:rgba(41,168,255,.24)!important;background:linear-gradient(145deg,#081b2d,#061727)!important;box-shadow:0 8px 22px rgba(0,0,0,.22)!important}
[data-testid="stVerticalBlockBorderWrapper"] h4{font-size:18px!important;margin-bottom:2px!important}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stButton"] button,
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stDownloadButton"] button{min-height:48px!important;height:auto!important;white-space:normal!important;line-height:1.15!important;font-size:12px!important;padding:8px 10px!important}
@media(max-width:768px){
 [data-testid="stVerticalBlockBorderWrapper"]{padding:4px!important}
 [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:8px!important}
 [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{min-width:100%!important;width:100%!important;flex:1 1 100%!important}
 [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stButton"] button,[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stDownloadButton"] button{font-size:13px!important;min-height:46px!important;width:100%!important}
}
</style>''',unsafe_allow_html=True)

st.title("📚 Histórico de Treinos")
st.caption("Sessões, CSVs e relatórios vinculados a cada skatista.")

try:
    if is_admin or is_technician:
        athletes = (sb.table("profiles")
                    .select("id,full_name,modality,status,role")
                    .eq("role", "skatista").eq("status", "ativo")
                    .order("full_name").execute().data or [])
        if not athletes:
            msg = "Ainda não há skatistas cadastrados para consultar." if is_admin else ("Nenhum atleta está vinculado a este familiar." if is_family else "Nenhum skatista do seu time está disponível para consulta.")
            st.info(msg); st.stop()
        amap = {f"{a.get('full_name') or 'Sem nome'}" + (f" • {a.get('modality')}" if a.get('modality') else ""): a for a in athletes}
        label = st.selectbox("Skatista", list(amap.keys()))
        athlete = amap[label]; athlete_id = athlete["id"]
    else:
        athlete_id = user.id; athlete = profile

    period = st.selectbox("Período", ["Todos", "Últimos 30 dias", "Últimos 90 dias", "Este ano", "Personalizado"])
    query = (sb.table("training_sessions")
             .select("id,athlete_id,training_date,title,csv_path,csv_paths,report_pdf_path,visual_pdf_path,created_at")
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
        # V2.0.2 — abrir o MESMO dashboard interativo da tela de análise usando
        # os CSVs arquivados. Não é apenas um preview do PDF: sessão, filtros e
        # distribuições continuam selecionáveis como no primeiro upload.
        csv_paths = row.get("csv_paths") or ([row.get("csv_path")] if row.get("csv_path") else [])
        view_col, b2, b3 = st.columns(3)
        if csv_paths:
            if view_col.button("◉  VER ANÁLISE", key=f"view_{row['id']}", use_container_width=True):
                try:
                    archived=[]
                    for i,path in enumerate(csv_paths,1):
                        raw=sb.storage.from_("training-csvs").download(path)
                        archived.append({"name": path.rsplit("/",1)[-1] or f"treino_{i}.csv", "data": raw})
                    st.session_state["history_analysis_view"]={
                        "session_id": row["id"], "athlete_id": athlete_id,
                        "title": row.get("title") or "Treino", "training_date": row.get("training_date"),
                        "files": archived
                    }
                    st.switch_page("pages/03_Analise_de_Treino.py")
                except Exception as exc:
                    st.error(f"Não foi possível abrir a análise: {exc}")

            # CSV bruto é material de trabalho: somente Admin pode baixar.
            if is_admin:
                try:
                    if len(csv_paths) == 1:
                        data=sb.storage.from_("training-csvs").download(csv_paths[0])
                        st.download_button("⬇ CSV ORIGINAL (ADMIN)",data=data,file_name=f"{safe}.csv",mime="text/csv",key=f"csv_{row['id']}",use_container_width=True)
                    else:
                        buf=io.BytesIO()
                        with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as zf:
                            for i,path in enumerate(csv_paths,1):
                                data=sb.storage.from_("training-csvs").download(path)
                                name=path.rsplit("/",1)[-1] or f"treino_{i}.csv"
                                zf.writestr(name,data)
                        st.download_button(f"⬇ {len(csv_paths)} CSVs ORIGINAIS (ADMIN)",data=buf.getvalue(),file_name=f"{safe}_CSVs.zip",mime="application/zip",key=f"csv_{row['id']}",use_container_width=True)
                except Exception as exc:
                    st.caption(f"CSV indisponível: {exc}")
        # Relatório é regenerado com o motor atual para usar fontes maiores inclusive em treinos antigos.
        if csv_paths:
            try:
                report_sessions=[]
                for i,path in enumerate(csv_paths,1):
                    raw=sb.storage.from_("training-csvs").download(path)
                    class ReportArchivedFile:
                        def __init__(self,name,data): self.name=name; self._data=data
                        def getvalue(self): return self._data
                    af=ReportArchivedFile(path.rsplit("/",1)[-1] or f"treino_{i}.csv",raw)
                    df=read_csv(af)
                    report_sessions.append(parse_aggregate(df,af.name) if is_aggregate(df) else parse_raw(df,af.name))
                report_merged=merge_sessions(report_sessions)
                report_data=make_pdf(athlete.get("full_name") or "ATLETA",report_merged,report_sessions,"TODOS OS TREINOS")
                b2.download_button("▤  RELATÓRIO PDF",data=report_data,file_name=f"{safe}_relatorio.pdf",mime="application/pdf",key=f"report_{row['id']}",use_container_width=True)
            except Exception as exc: b2.caption(f"Relatório indisponível: {exc}")
        else: b2.caption("CSVs não disponíveis para gerar o relatório")
        # Gera o dashboard com o motor ATUAL a partir dos CSVs arquivados. Assim o
        # download direto do Histórico nunca fica preso ao layout antigo salvo no Storage.
        if csv_paths:
            try:
                sessions=[]
                for i,path in enumerate(csv_paths,1):
                    raw=sb.storage.from_("training-csvs").download(path)
                    class ArchivedFile:
                        def __init__(self,name,data): self.name=name; self._data=data
                        def getvalue(self): return self._data
                    af=ArchivedFile(path.rsplit("/",1)[-1] or f"treino_{i}.csv",raw)
                    df=read_csv(af)
                    sessions.append(parse_aggregate(df,af.name) if is_aggregate(df) else parse_raw(df,af.name))
                merged=merge_sessions(sessions)
                data=make_visual_pdf(athlete.get("full_name") or "ATLETA",merged,sessions,"TODOS OS TREINOS",None)
                b3.download_button("▦  DASHBOARD VISUAL",data=data,file_name=f"{safe}_dashboard_visual.pdf",mime="application/pdf",key=f"visual_{row['id']}",use_container_width=True)
            except Exception as exc: b3.caption(f"Dashboard indisponível: {exc}")
        else: b3.caption("CSVs não disponíveis para gerar o dashboard")

        if is_admin:
            confirm=st.checkbox("Confirmar exclusão",key=f"confirm_{row['id']}")
            if st.button("🗑️ Excluir do histórico",key=f"delete_{row['id']}",disabled=not confirm):
                try:
                    csv_paths = row.get("csv_paths") or ([row.get("csv_path")] if row.get("csv_path") else [])
                    if csv_paths: sb.storage.from_("training-csvs").remove(csv_paths)
                    report_paths=[p for p in [row.get("report_pdf_path"),row.get("visual_pdf_path")] if p]
                    if report_paths: sb.storage.from_("training-reports").remove(report_paths)
                    sb.table("training_sessions").delete().eq("id",row["id"]).execute()
                    st.success("Treino e arquivos associados excluídos."); st.rerun()
                except Exception as exc: st.error(f"Não foi possível excluir: {exc}")
