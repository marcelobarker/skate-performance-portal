import re
import io, zipfile
from datetime import date, timedelta
import streamlit as st
import plotly.graph_objects as go
from streamlit_elements import elements, mui
from auth_utils import require_login, get_supabase
from report_engine import read_csv, is_aggregate, parse_raw, parse_aggregate, merge_sessions, make_pdf, make_visual_pdf

from ui_theme import apply_ui_theme

st.set_page_config(initial_sidebar_state="collapsed", page_title="Histórico • Seleção Brasileira de Skateboarding", page_icon="📚", layout="wide")
apply_ui_theme()

st.markdown(r"""<style>
/* HISTÓRICO V4 — fullscreen, centralizado e dark/neon */
[data-testid="stToolbar"], [data-testid="stHeader"],
section[data-testid="stSidebar"], aside[data-testid="stSidebar"], div[data-testid="stSidebar"],
[data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="stSidebarContent"],
[data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"],
button[aria-label="Open sidebar"], button[aria-label="Close sidebar"], button[kind="headerNoPadding"]{
display:none!important;width:0!important;min-width:0!important;max-width:0!important;visibility:hidden!important;}
[data-testid="stAppViewContainer"], .stApp {background:linear-gradient(180deg,#03111e 0%,#020b14 55%,#04101c 100%)!important;color:#f5f8fc!important;}
[data-testid="stAppViewContainer"]>.main,[data-testid="stAppViewContainer"]>section.main,section.main,
[data-testid="stMain"],[data-testid="stMainBlockContainer"]{margin-left:0!important;width:100%!important;max-width:100%!important;}
[data-testid="stAppViewContainer"]>section>div {margin-left:0!important;width:100%!important;}
[data-testid="stCustomComponentV1"]{background:transparent!important;border:0!important;outline:0!important;box-shadow:none!important;padding:0!important;}
[data-testid="stCustomComponentV1"] iframe{background:transparent!important;border:0!important;outline:0!important;box-shadow:none!important;}
iframe[title="streamlit_elements.core.frame"]{border:0!important;outline:0!important;background:#03111e!important;}
.block-container{width:100%!important;max-width:1480px!important;padding:0 26px 56px!important;margin:0 auto!important;}
html,body,[class*="css"],.stApp{font-family:"Segoe UI Variable",Inter,Manrope,Arial,sans-serif!important;}
h1,h2,h3,h4,p,label,[data-testid="stMarkdownContainer"]{color:#eef8ff!important;}
[data-testid="stCaptionContainer"],small{color:#91a9bd!important;}
/* controles */
[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button{background:linear-gradient(145deg,#0b2035,#081827)!important;color:#eef8ff!important;border:1px solid #20577b!important;border-radius:11px!important;min-height:43px!important;font-weight:800!important;box-shadow:inset 0 0 16px rgba(0,126,255,.05)!important;}
[data-testid="stButton"] button:hover,[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover{border-color:#20e6ff!important;color:#fff!important;box-shadow:0 0 18px rgba(0,217,255,.20)!important;}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input,[data-testid="stTimeInput"] input,[data-baseweb="select"]>div,[data-baseweb="input"],textarea{background:#081b2d!important;color:#eef8ff!important;border-color:#1b668d!important;border-radius:10px!important;-webkit-text-fill-color:#eef8ff!important;}
[data-baseweb="select"] span,[data-baseweb="select"] svg{color:#eaf7ff!important;fill:#eaf7ff!important;}
[data-baseweb="popover"] ul,[role="listbox"]{background:#081b2d!important;color:#f5f8fc!important;} [role="option"]{color:#eaf7ff!important;background:#081b2d!important;} [role="option"]:hover{background:#0d2b45!important;}
/* cards das sessões */
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:16px!important;border:1px solid rgba(41,168,255,.25)!important;background:linear-gradient(145deg,rgba(8,27,45,.98),rgba(5,18,31,.98))!important;box-shadow:0 12px 30px rgba(0,0,0,.22),inset 0 1px rgba(255,255,255,.02)!important;}
[data-testid="stVerticalBlockBorderWrapper"]:hover{border-color:rgba(32,230,255,.42)!important;box-shadow:0 12px 34px rgba(0,0,0,.28),0 0 22px rgba(0,217,255,.06)!important;}
[data-testid="stMetric"]{background:linear-gradient(145deg,#071b2d,#061421)!important;border:1px solid #16476a!important;border-radius:14px!important;padding:14px 16px!important;box-shadow:0 0 22px rgba(8,124,255,.06)!important;}
[data-testid="stMetricLabel"]{color:#8fa9bf!important;font-weight:800!important;text-transform:uppercase!important;letter-spacing:.6px!important;}
[data-testid="stMetricValue"]{color:#f7fbff!important;font-weight:950!important;}
/* cabeçalhos visuais */
.hist-hero{margin:20px 0 18px;padding:26px 28px;border:1px solid #16476a;border-radius:18px;background:radial-gradient(circle at 88% 20%,rgba(0,217,255,.10),transparent 25%),linear-gradient(120deg,#071a2c,#061421 62%,#071b2d);box-shadow:0 16px 38px rgba(0,0,0,.20);}
.hist-kicker{color:#20e6ff;font-size:11px;font-weight:900;letter-spacing:2.2px;text-transform:uppercase;margin-bottom:7px}.hist-title{font-size:30px;font-weight:950;letter-spacing:-.7px;color:#f5f8fc;line-height:1.08}.hist-sub{color:#9bb0c3;font-size:13px;margin-top:7px}.section-label{font-size:11px;font-weight:950;letter-spacing:1.8px;color:#20e6ff;text-transform:uppercase;margin:22px 0 8px;}
/* tabela */
[data-testid="stDataFrame"]{border:1px solid #16476a!important;border-radius:12px!important;overflow:hidden!important;}
@media(max-width:768px){.block-container{padding:0 12px 40px!important}.hist-title{font-size:24px}[data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:8px!important}[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{min-width:100%!important;width:100%!important;flex:1 1 100%!important}}

/* V4.19 — acabamento do histórico */
[data-testid="stVerticalBlockBorderWrapper"] > div{padding-top:4px!important;padding-bottom:4px!important;}
[data-testid="stCheckbox"] label{font-size:12px!important;color:#91a9bd!important;}
[data-testid="stCheckbox"]{margin-top:2px!important;margin-bottom:-4px!important;}
[data-testid="stButton"] button:disabled{opacity:.42!important;box-shadow:none!important;}

/* V4.20 — KPIs de análise em vídeo */
.hist-kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:8px 0 18px}.hist-kpi{background:linear-gradient(145deg,#0a2137,#07192a);border:1px solid #1a608a;border-radius:14px;padding:14px;display:grid;grid-template-columns:42px 1fr;gap:11px;align-items:center;box-shadow:0 8px 22px rgba(0,0,0,.16)}.hist-kpi-icon{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#20e6ff;background:rgba(0,217,255,.08);border:1px solid rgba(32,230,255,.28)}.hist-kpi-icon svg{width:21px;height:21px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.hist-kpi-label{font-size:10px;color:#a9c7dc;font-weight:850;letter-spacing:.08em}.hist-kpi-value{font-size:28px;color:#f6fbff;font-weight:950;line-height:1.05;margin-top:3px}.hist-kpi.error{border-color:#703044}.hist-kpi.error .hist-kpi-icon,.hist-kpi.error .hist-kpi-value{color:#ff5260}@media(max-width:900px){.hist-kpi-grid{grid-template-columns:repeat(2,1fr)}}

/* V4.23 unified redesigned-page frame */
[data-testid="stMainBlockContainer"]{
  border-left:8px solid #f5f8fc!important;
  border-right:8px solid #f5f8fc!important;
  box-sizing:border-box!important;
}
[data-testid="stMainBlockContainer"]::before{
  content:"";display:block;height:8px;background:#f5f8fc;margin:0 -0px 0;
}


/* V4.24 — navbar encostada no topo */
[data-testid="stMainBlockContainer"]{
  padding-top:0!important;
  margin-top:0!important;
}
.main .block-container,.block-container{
  padding-top:0!important;
  margin-top:0!important;
}
</style>""", unsafe_allow_html=True)

user, profile = require_login()
sb = get_supabase()
role = profile.get("role")
is_admin = True  # V4.42 temporário
is_technician = True  # V4.42 temporário
is_family = role == "familiar"




# Navbar V4.29 visual preservado; links nativos fora de iframe.
nav_name = str((profile or {}).get("full_name") or getattr(user, "email", None) or "Usuário").strip()
nav_role = str((profile or {}).get("role") or "membro").replace("_", " ").title()
nav_photo = (profile or {}).get("photo_url")
from nav_v472 import render_top_nav
render_top_nav(nav_name=nav_name, nav_role=nav_role, nav_photo=nav_photo, active='Histórico', key="nav_pages_04_Historico_de_Treinos.py")

st.markdown("""<div class="hist-hero"><div class="hist-kicker">Performance archive</div><div class="hist-title">Histórico de Treinos</div><div class="hist-sub">Consulte sessões, análises, CSVs e relatórios de cada atleta em um único lugar.</div></div>""",unsafe_allow_html=True)

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
        requested_id = st.session_state.pop("history_athlete_id", None)
        labels=list(amap.keys()); default_index=0
        if requested_id:
            for i,k in enumerate(labels):
                if amap[k].get("id")==requested_id: default_index=i; break
        label = st.selectbox("Skatista", labels, index=default_index)
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

st.markdown('<div class="section-label">Atleta selecionado</div>',unsafe_allow_html=True)
st.markdown(f"## {athlete.get('full_name') or 'Skatista'}")
# Sessões codificadas em vídeo também fazem parte do histórico do atleta.
try:
    video_posts=(sb.table("athlete_posts").select("id,session_title,created_at,analysis_status,upload_kind")
                 .eq("athlete_id",athlete_id).eq("upload_kind","session").order("created_at",desc=True).execute().data or [])
    all_events=sb.table("trick_video_events").select("*").eq("athlete_id",athlete_id).execute().data or []
    tricks=sb.table("tricks").select("id,name").execute().data or []; trick_names={x["id"]:x["name"] for x in tricks}
except Exception:
    video_posts=[]; all_events=[]; trick_names={}
if not rows and not video_posts:
    st.info("Nenhum treino salvo para este skatista neste período."); st.stop()

if video_posts:
    st.markdown('<div class="section-label">Análise por vídeo</div>',unsafe_allow_html=True)
    st.markdown("## Treinos codificados em vídeo")
    st.caption("Sessões analisadas por tentativa, com a mesma leitura de performance do dashboard.")
    for vp in video_posts:
        ev=[x for x in all_events if x.get("post_id")==vp["id"]]
        with st.container(border=True):
            st.markdown(f"#### {vp.get('session_title') or 'Sessão de vídeo'}")
            st.caption((vp.get('created_at') or '')[:10] + " • " + (vp.get('analysis_status') or 'aguardando').upper())
            if not ev:
                st.caption("Ainda sem tentativas codificadas.")
                continue
            total=len(ev); hits=sum(1 for x in ev if x.get('result')=='Acerto'); errors=total-hits; rate=hits/total*100 if total else 0
            st.markdown(f"""<div class="hist-kpi-grid">
<div class="hist-kpi"><div class="hist-kpi-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v3M22 12h-3"/></svg></div><div><div class="hist-kpi-label">TENTATIVAS</div><div class="hist-kpi-value">{total}</div></div></div>
<div class="hist-kpi"><div class="hist-kpi-icon"><svg viewBox="0 0 24 24"><path d="M5 12l4 4L19 6"/><circle cx="12" cy="12" r="9"/></svg></div><div><div class="hist-kpi-label">ACERTOS</div><div class="hist-kpi-value">{hits}</div></div></div>
<div class="hist-kpi error"><div class="hist-kpi-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/></svg></div><div><div class="hist-kpi-label">ERROS</div><div class="hist-kpi-value">{errors}</div></div></div>
<div class="hist-kpi"><div class="hist-kpi-icon"><svg viewBox="0 0 24 24"><path d="M7 17L17 7"/><circle cx="8" cy="8" r="2"/><circle cx="16" cy="16" r="2"/></svg></div><div><div class="hist-kpi-label">TAXA DE ACERTO</div><div class="hist-kpi-value">{rate:.1f}%</div></div></div>
</div>""",unsafe_allow_html=True)
            def dist(field):
                out={}
                for x in ev:
                    v=x.get(field)
                    if v: out[v]=out.get(v,0)+1
                return out
            def donut(title,data):
                colors={'Excelente':'#16d98b','Bom':'#1398ff','Ruim':'#ff4050','Baixa':'#1398ff','Média':'#16d98b','Alta':'#ff4050','Baixo':'#1398ff','Médio':'#16d98b','Alto':'#ff4050','Lento':'#ff4050','Rápido':'#16d98b'}
                fig=go.Figure(go.Pie(labels=list(data),values=list(data.values()),hole=.63,marker=dict(colors=[colors.get(k,'#29a8ff') for k in data],line=dict(color='#071522',width=1)),textinfo='percent',textfont=dict(size=17,color='#f5f8fc',family='Arial Black')))
                fig.update_layout(title=dict(text=title,x=.04,font=dict(size=14,color='#f5f8fc')),height=314,margin=dict(l=4,r=4,t=38,b=52),paper_bgcolor='rgba(0,0,0,0)',font=dict(color='#9db3c8'),legend=dict(orientation='h',y=-.15,x=0,font=dict(size=9)))
                total_chart=sum(data.values())
                fig.add_annotation(x=.5,y=.5,text=f"<b>{total_chart:.0f}</b><br><span style='font-size:10px;color:#7fa4bd'>TOTAL</span>",showarrow=False,align='center',font=dict(size=24,color='#f5f8fc',family='Arial Black'))
                return fig
            cols=st.columns(4)
            for col,title,field in zip(cols,['AVALIAÇÃO','DIFICULDADE','RISCO','VELOCIDADE'],['evaluation','difficulty','risk','speed']):
                dd=dist(field)
                if dd:
                    with col: st.plotly_chart(donut(title,dd),use_container_width=True,config={'displayModeBar':False})
            counts={}
            for x in ev:
                n=trick_names.get(x.get('trick_id'),'Manobra'); counts.setdefault(n,{'Acertos':0,'Erros':0}); counts[n]['Acertos' if x.get('result')=='Acerto' else 'Erros']+=1
            table=[]
            for n,cnt in counts.items():
                tt=cnt['Acertos']+cnt['Erros']; table.append({'Manobra':n,'Acertos':cnt['Acertos'],'Erros':cnt['Erros'],'Tentativas':tt,'Taxa de acerto':f"{cnt['Acertos']/tt*100:.1f}%"})
            st.dataframe(table,use_container_width=True,hide_index=True)

if rows:
    st.markdown('<div class="section-label">Sportscode / CSV</div>',unsafe_allow_html=True)
    st.markdown("## Treinos salvos")
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
