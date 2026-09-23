from auth_utils import require_login, get_supabase
import io, re, unicodedata, uuid
from datetime import date
from urllib.request import urlopen
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from streamlit_elements import elements, mui

from ui_theme import apply_ui_theme

st.set_page_config(initial_sidebar_state="collapsed", page_title="Análise de Treino • Seleção Brasileira", page_icon="🛹", layout="wide")

# V4.23 early sidebar kill

st.markdown("""<style>
html,body,[data-testid="stAppViewContainer"]{background:#020b14!important;}
section[data-testid="stSidebar"],aside[data-testid="stSidebar"],div[data-testid="stSidebar"],
[data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="stSidebarContent"],
[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"],
button[aria-label="Open sidebar"],button[aria-label="Close sidebar"]{
display:none!important;width:0!important;min-width:0!important;max-width:0!important;
visibility:hidden!important;opacity:0!important;pointer-events:none!important;}
[data-testid="stAppViewContainer"]>.main,section.main,[data-testid="stMain"]{
margin-left:0!important;width:100%!important;max-width:100%!important;}

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
[data-testid="stDateInput"]>div,[data-testid="stDateInput"] div[data-baseweb="input"]{background:#0b1d2d!important;color:#eef8ff!important;}
[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{background:#0b1d2d!important;color:#eef8ff!important;}

/* V4.20 — KPIs premium + ícones */
.kpi2{display:grid!important;grid-template-columns:42px 1fr!important;grid-template-rows:auto auto auto!important;column-gap:11px!important;align-items:center!important;padding:14px 15px!important;min-height:100px!important}
.kpi2-icon{grid-row:1/4;width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,rgba(0,217,255,.16),rgba(8,124,255,.07));border:1px solid rgba(32,230,255,.30);box-shadow:0 0 18px rgba(0,217,255,.08);color:#20e6ff}
.kpi2-icon svg{width:21px;height:21px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.kpi2-label,.kpi2-value,.kpi2-sub{grid-column:2!important;margin:0!important}.kpi2-value{font-size:30px!important;margin-top:2px!important}.kpi2-error .kpi2-icon{color:#ff5260;border-color:rgba(255,82,96,.34);background:rgba(255,82,96,.07)}
.video-kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:8px 0 18px}.video-kpi{background:linear-gradient(145deg,#0a2137,#07192a);border:1px solid #1a608a;border-radius:14px;padding:14px;display:grid;grid-template-columns:42px 1fr;gap:11px;align-items:center;box-shadow:0 8px 22px rgba(0,0,0,.16)}.video-kpi .vk-icon{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#20e6ff;background:rgba(0,217,255,.08);border:1px solid rgba(32,230,255,.28)}.video-kpi .vk-icon svg{width:21px;height:21px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.video-kpi .vk-label{font-size:10px;color:#a9c7dc;font-weight:850;letter-spacing:.08em}.video-kpi .vk-value{font-size:28px;color:#f6fbff;font-weight:950;line-height:1.05;margin-top:3px}.video-kpi.error{border-color:#703044}.video-kpi.error .vk-icon,.video-kpi.error .vk-value{color:#ff5260}@media(max-width:900px){.video-kpi-grid{grid-template-columns:repeat(2,1fr)}}

/* V4.23 unified redesigned-page frame */
[data-testid="stMainBlockContainer"]{
  border-left:8px solid #f5f8fc!important;
  border-right:8px solid #f5f8fc!important;
  box-sizing:border-box!important;
}
[data-testid="stMainBlockContainer"]::before{
  content:"";display:block;height:8px;background:#f5f8fc;margin:0 -0px 0;
}

</style>""", unsafe_allow_html=True)


user, profile = require_login()
history_view = st.session_state.get("history_analysis_view")
if profile.get("role") in ("skatista","familiar") and not history_view:
    st.info("🛹 Seu perfil de skatista tem acesso ao Histórico de Treinos. As análises e uploads de CSV são realizados pela equipe técnica.")
    st.stop()
st.markdown("""
<style>
:root{--bg:#06111f;--panel:#09192b;--panel2:#0c2035;--line:#173a58;--blue:#1398ff;--cyan:#5bc0ff;--green:#12dc8c;--red:#ff4050;--text:#f5f8ff;--muted:#89a5bf}
.stApp{background:radial-gradient(circle at 75% 0%,#0a1a2b 0,#06111f 42%,#050e1a 100%);color:var(--text)}
.block-container{max-width:1700px;padding-top:1.2rem;padding-bottom:3rem}
[data-testid="stHeader"]{display:none!important}
[data-testid="stToolbar"]{display:none!important}
#MainMenu{visibility:hidden!important}
footer{visibility:hidden!important}
[data-testid="stDecoration"]{display:none!important}


h1,h2,h3{letter-spacing:.02em}
div[data-testid="stMetric"]{background:#09192b;border:1px solid #1b4567;border-radius:12px;padding:14px 16px}
.kpi{height:122px;background:linear-gradient(145deg,#0b1d31,#091827);border:1px solid #1b4567;border-radius:12px;padding:16px}
.klabel{font-size:12px;color:#9bb2c8;letter-spacing:.08em;font-weight:700}
.kvalue{font-size:34px;font-weight:850;margin-top:10px}.ksub{font-size:13px;margin-top:3px;color:#55bfff}
.hero{background:linear-gradient(145deg,#0b1d31,#081725);border:1px solid #1b4567;border-radius:14px;padding:14px}
.section{font-size:21px;font-weight:850;margin:22px 0 8px;letter-spacing:.03em}
.session-pill{display:inline-block;background:#0b2a45;border:1px solid #1b5d8c;color:#67c5ff;border-radius:999px;padding:5px 10px;font-size:12px;margin:2px 3px 2px 0}
.table-wrap{border:1px solid #1a4566;border-radius:12px;overflow:hidden;background:#071522}
.sk-table{width:100%;border-collapse:collapse;font-size:13px}
.sk-table th{background:#0d2237;color:#9cb4ca;text-align:left;padding:12px;border-bottom:1px solid #1b4567}
.sk-table td{padding:11px 12px;border-bottom:1px solid #112d45;color:#e9f3ff}
.sk-table tr:last-child td{border-bottom:none}.sk-table tr:hover td{background:#0a1d30}
.hit{color:#18df91!important;font-weight:800}.err{color:#ff4c5b!important;font-weight:800}.rate{color:#51bdff!important;font-weight:800}
.smallnote{color:#819db6;font-size:12px}
[data-testid="stFileUploaderDropzone"]{background:#09192b!important;border-color:#245071!important}
[data-testid="stFileUploaderDropzone"] *{color:#dcecff!important}
[data-testid="stFileUploaderFile"]{background:#0b1d31!important;color:#dcecff!important}
[data-testid="stFileUploaderFile"] *{color:#dcecff!important}


.stSelectbox div[data-baseweb="select"]>div,.stTextInput input{background:#09192b!important;border-color:#245071!important;color:#eef7ff!important}
div[data-baseweb="popover"],ul[role="listbox"]{background:#09192b!important}
div[role="option"]{color:#eef7ff!important}
.site-header{display:flex;align-items:center;justify-content:space-between;
background:linear-gradient(100deg,#081827,#0a2136);border:1px solid #1b4567;
border-radius:15px;padding:18px 24px;margin:2px 0 22px 0;box-shadow:0 10px 30px rgba(0,0,0,.2)}
.brand{font-size:29px;font-weight:950;font-style:italic;letter-spacing:.04em;color:#fff;line-height:1}
.brand span{color:#43b8ff}.tag{font-size:11px;color:#7fa3c0;letter-spacing:.18em;margin-top:7px}
.header-right{text-align:right}.header-right b{color:#5dc3ff;font-size:12px;letter-spacing:.12em}.header-right div{color:#7795ae;font-size:11px;margin-top:4px}

/* V4.4 - contraste dos controles */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"]{
    background:#0b1d31 !important;
    color:#eaf6ff !important;
    border-color:#245071 !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder{color:#7894ad !important;}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] *{color:#dcecff !important;}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button{
    background:#102c49 !important;color:#f2f8ff !important;border:1px solid #245071 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button *{color:#f2f8ff !important;}
div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"]{
    background:#081827 !important;border:1px solid #245071 !important;
}
div[role="option"]{background:#081827 !important;color:#eaf6ff !important;}
div[role="option"] *{color:#eaf6ff !important;}
div[role="option"]:hover, div[role="option"][aria-selected="true"]{
    background:#0d8df0 !important;color:white !important;
}
div[role="option"]:hover *, div[role="option"][aria-selected="true"] *{color:white !important;}
[data-testid="stDownloadButton"] button{
    background:#0d2a43 !important;color:#eef8ff !important;border:1px solid #1c6b9e !important;
}
[data-testid="stDownloadButton"] button *{color:#eef8ff !important;}


/* V4.5 — correção pontual de contraste dos componentes claros do Streamlit */
[data-testid="stFileUploaderFile"]{
    background:#f1f4f8 !important;
    border:1px solid #d7e0e8 !important;
}
[data-testid="stFileUploaderFile"] *,
[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFile"] small,
[data-testid="stFileUploaderFile"] p{
    color:#173047 !important;
    opacity:1 !important;
}
[data-testid="stFileUploaderFile"] svg{
    color:#173047 !important;
    fill:#173047 !important;
}
[data-testid="stFileUploaderFile"] button,
[data-testid="stFileUploaderFile"] button *{
    color:#173047 !important;
}
[data-testid="stFileUploaderDropzone"] button{
    background:#f4f6f9 !important;
    color:#173047 !important;
    border:1px solid #d8e1e9 !important;
}
[data-testid="stFileUploaderDropzone"] button *{color:#173047 !important}

/* Select fechado e menu aberto: fundo claro = texto escuro */
[data-baseweb="select"] > div{
    background:#f5f6f8 !important;
    color:#15283a !important;
}
[data-baseweb="select"] > div *{color:#15283a !important}
div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"]{
    background:#f5f6f8 !important;
}
div[role="option"], div[role="option"] *{
    color:#15283a !important;
}
div[role="option"]:hover, div[role="option"][aria-selected="true"]{
    background:#dce9f4 !important;
}
div[role="option"]:hover *, div[role="option"][aria-selected="true"] *{
    color:#10283d !important;
}

/* Downloads permanecem dark e legíveis */
[data-testid="stDownloadButton"] button{
    background:#0d2a43 !important;
    border:1px solid #178bd1 !important;
    color:#eef8ff !important;
}
[data-testid="stDownloadButton"] button *{color:#eef8ff !important}


/* Impressão/PDF pelo navegador: preserva o dashboard inteiro como visto */
@media print{
  *{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
  html,body,.stApp{background:#06111f!important}
  [data-testid="stHeader"],[data-testid="stToolbar"],#MainMenu,footer{display:none!important}
  .block-container{max-width:none!important;padding:10mm!important}
  [data-testid="stSidebar"]{position:relative!important;width:280px!important;min-width:280px!important}
  [data-testid="stSidebarCollapseButton"]{display:none!important}
  [data-testid="stDownloadButton"]{display:none!important}
  iframe{display:none!important}
  .element-container,.stPlotlyChart,.table-wrap{break-inside:avoid!important}
}


/* V4.7 — ajustes finais de contraste */
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] > div{
  background:#eef2f6!important;border-color:#d3dde6!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] *,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] p,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] span,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] small,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] div{
  color:#10283d!important;opacity:1!important;-webkit-text-fill-color:#10283d!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] svg{
  color:#10283d!important;fill:#10283d!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] button{
  color:#10283d!important;background:transparent!important;
}

/* Cabeçalho de KPIs */
.kpi-shell{background:linear-gradient(135deg,#081827,#0a1e32);border:1px solid #1b4567;
border-radius:16px;padding:17px 18px 18px;margin-top:2px;box-shadow:0 12px 28px rgba(0,0,0,.18)}
.kpi-title{font-size:25px;font-weight:900;color:#f6fbff;letter-spacing:.02em;margin-bottom:2px}
.kpi-subtitle{font-size:11px;color:#6dbfff;letter-spacing:.13em;margin-bottom:13px}
.kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.kpi2{background:linear-gradient(145deg,#0c2138,#09192b);border:1px solid #205275;border-radius:11px;
padding:12px 13px;min-height:82px}
.kpi2-label{font-size:10px;color:#8baac3;font-weight:800;letter-spacing:.09em}
.kpi2-value{font-size:27px;color:#f6fbff;font-weight:950;margin-top:5px;line-height:1}
.kpi2-sub{font-size:10px;color:#49b9ff;margin-top:6px}
.kpi2-error .kpi2-value,.kpi2-error .kpi2-sub{color:#ff5260}
@media(max-width:1100px){.kpi-grid{grid-template-columns:repeat(3,1fr)}}


/* V4.8 — controles 100% dark */
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] > div,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] section {
    background:#0b1d31 !important;
    border-color:#245071 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] *,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] p,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] span,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] small,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] div {
    color:#eaf6ff !important;
    -webkit-text-fill-color:#eaf6ff !important;
    opacity:1 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] svg {
    color:#8ed1ff !important;
    fill:#8ed1ff !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] button,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] button * {
    background:#102b45 !important;
    color:#eaf6ff !important;
    -webkit-text-fill-color:#eaf6ff !important;
}

/* select fechado */
div[data-baseweb="select"] > div,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background:#0b1d31 !important;
    border-color:#245071 !important;
    color:#eaf6ff !important;
}
div[data-baseweb="select"] > div *,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div * {
    color:#eaf6ff !important;
    -webkit-text-fill-color:#eaf6ff !important;
}

/* menu do select aberto */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"],
div[role="listbox"] {
    background:#081827 !important;
    border-color:#245071 !important;
}
div[role="option"],
div[role="option"] *,
li[role="option"],
li[role="option"] * {
    background:#081827 !important;
    color:#eaf6ff !important;
    -webkit-text-fill-color:#eaf6ff !important;
}
div[role="option"]:hover,
div[role="option"][aria-selected="true"],
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background:#123a5a !important;
}
div[role="option"]:hover *,
div[role="option"][aria-selected="true"] *,
li[role="option"]:hover *,
li[role="option"][aria-selected="true"] * {
    color:#ffffff !important;
    -webkit-text-fill-color:#ffffff !important;
}


/* V4.9 — uploader e select totalmente dark */
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"]{
 background:#0a2034!important;border:1px solid #245071!important;border-radius:9px!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] > div,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] > div > div{
 background:transparent!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] p,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] span,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] small,
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] div{
 color:#e9f6ff!important;-webkit-text-fill-color:#e9f6ff!important;opacity:1!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] button{
 background:#102b45!important;border-color:#3b6d90!important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] svg{
 color:#9bd7ff!important;fill:#9bd7ff!important;
}
[data-testid="stSelectbox"] label,
[data-testid="stSelectbox"] label *,
[data-testid="stSelectbox"] > label p{
 color:#b9d7ec!important;-webkit-text-fill-color:#b9d7ec!important;opacity:1!important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div{
 background:#0a2034!important;border:1px solid #245071!important;color:#f2f9ff!important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div *{
 color:#f2f9ff!important;-webkit-text-fill-color:#f2f9ff!important;
}
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] [role="listbox"],
div[data-baseweb="menu"]{
 background:#081827!important;border:1px solid #245071!important;
}
div[data-baseweb="popover"] [role="option"],
div[data-baseweb="popover"] [role="option"] *{
 background:#081827!important;color:#eaf6ff!important;-webkit-text-fill-color:#eaf6ff!important;
}
div[data-baseweb="popover"] [role="option"]:hover,
div[data-baseweb="popover"] [role="option"][aria-selected="true"]{
 background:#123a5a!important;
}

</style>
""", unsafe_allow_html=True)

def norm(s):
    s=unicodedata.normalize("NFKD",str(s)).encode("ascii","ignore").decode()
    return re.sub(r"\s+"," ",s.strip()).upper()

def read_csv(f):
    raw=f.getvalue()
    for enc in ("utf-8-sig","utf-8","latin1"):
        for sep in (None,",",";","\t"):
            try:
                kw={"encoding":enc}
                if sep is None: kw.update(sep=None,engine="python")
                else: kw["sep"]=sep
                d=pd.read_csv(io.BytesIO(raw),**kw)
                if len(d.columns)>1:return d
            except: pass
    raise ValueError("Formato CSV não reconhecido")

def is_aggregate(d):
    return any(":" in str(c) for c in d.columns)

def empty_session(name):
    return {"name":name,"attempts":0,"hits":0,"errors":0,"maneuvers":{},
            "cats":{k:{} for k in ["AVALIACAO","DIFICULDADE","RISCO","DIRECAO","VELOCIDADE","OBSTACULO","BASE"]}}

def add(dic,key,n=1):
    key=norm(key)
    if key and key not in ("NAN","0","NONE"):
        dic[key]=dic.get(key,0)+float(n)

def parse_raw(d,name):
    d=d.copy(); d.columns=[norm(c) for c in d.columns]
    s=empty_session(name)
    # Sportscode raw export: Row = maneuver, ACERTOS = result
    mcol="ROW" if "ROW" in d.columns else next((c for c in ["MANOBRA","TRICK","CODE"] if c in d.columns),None)
    for _,r in d.iterrows():
        result=norm(r.get("ACERTOS",""))
        valid=result in ("ACERTO","ERRO")
        if valid:
            s["attempts"]+=1
            s["hits"]+=result=="ACERTO"; s["errors"]+=result=="ERRO"
            man=norm(r.get(mcol,"")) if mcol else ""
            if man and man!="NAN":
                if man not in s["maneuvers"]:s["maneuvers"][man]=[0,0]
                s["maneuvers"][man][0 if result=="ACERTO" else 1]+=1
        # categories can exist even on rows without result; count only valid attempts for consistency
        if valid:
            for cat in s["cats"]:
                val=r.get(cat,"")
                if pd.isna(val):continue
                # direction may contain "FRONTSIDE, REVERSE"
                vals=[v.strip() for v in str(val).split(",")]
                for v in vals:add(s["cats"][cat],v)
    return s

def parse_aggregate(d,name):
    d=d.copy(); d.columns=[norm(c) for c in d.columns]
    s=empty_session(name)
    mcol=d.columns[0]
    # first column is maneuver name in pivoted Sportscode CSV
    for _,r in d.iterrows():
        h=float(pd.to_numeric(r.get("ACERTOS:ACERTO",0),errors="coerce") or 0)
        e=float(pd.to_numeric(r.get("ACERTOS:ERRO",0),errors="coerce") or 0)
        man=norm(r.get(mcol,""))
        if h+e>0 and man not in ("","NAN","0"):
            s["maneuvers"][man]=[h,e]
        s["hits"]+=h;s["errors"]+=e
        for cat in s["cats"]:
            pref=cat+":"
            for c in d.columns:
                if c.startswith(pref):
                    v=pd.to_numeric(r.get(c,0),errors="coerce")
                    if pd.notna(v) and float(v)!=0:add(s["cats"][cat],c.split(":",1)[1],float(v))
    s["attempts"]=s["hits"]+s["errors"]
    return s

def merge_sessions(ss):
    out=empty_session("TODOS OS TREINOS")
    for s in ss:
        for k in ("attempts","hits","errors"):out[k]+=s[k]
        for m,(h,e) in s["maneuvers"].items():
            if m not in out["maneuvers"]:out["maneuvers"][m]=[0,0]
            out["maneuvers"][m][0]+=h;out["maneuvers"][m][1]+=e
        for cat in out["cats"]:
            for k,v in s["cats"][cat].items():add(out["cats"][cat],k,v)
    return out

PALETTE=["#0d8df0","#6bc1f7","#ff3f4d","#16d98b","#f4cf43","#a46cff","#ff8b3d"]

SITE_CATEGORY_COLORS = {
    "ACERTO":"#16d98b", "ERRO":"#ff4050",
    "BOM":"#1398ff", "RUIM":"#ff4050", "EXCELENTE":"#16d98b",
    "BAIXA":"#1398ff", "MEDIA":"#16d98b", "MÉDIA":"#16d98b", "ALTA":"#ff4050",
    "BAIXO":"#1398ff", "MEDIO":"#16d98b", "MÉDIO":"#16d98b", "ALTO":"#ff4050",
    "NORMAL":"#1398ff", "LENTO":"#ff4050", "RAPIDO":"#16d98b", "RÁPIDO":"#16d98b",
    "SWITCH":"#1398ff", "NOLLIE":"#16d98b", "FAKIE":"#ff4050",
    "FRONTSIDE":"#16d98b", "BACKSIDE":"#6bc1f7", "REVERSE":"#ff4050",
}

def donut(title,data):
    data={k:v for k,v in data.items() if v>0}
    # Cores semânticas iguais às do Dashboard Visual PDF
    chart_colors=[SITE_CATEGORY_COLORS.get(str(label).strip().upper(), PALETTE[i % len(PALETTE)])
                  for i,label in enumerate(data.keys())]
    fig=go.Figure(go.Pie(labels=list(data),values=list(data.values()),hole=.66,
        marker=dict(colors=chart_colors,line=dict(color="#071522",width=1)),
        textinfo="percent",textfont=dict(size=17,color="#f5f8ff",family="Arial Black"),
        hovertemplate="<b>%{label}</b><br>%{value:.0f} • %{percent}<extra></extra>"))
    if title=="OBSTÁCULO":
        # Muitas categorias: percentuais ficam dentro das fatias para evitar linhas/labels sobrepostos.
        fig.update_traces(textposition="inside", textinfo="percent", insidetextorientation="radial",
                          textfont=dict(size=14,color="#f5f8ff",family="Arial Black"),
                          domain=dict(x=[0.08,0.66],y=[0.08,0.95]))
        fig.update_layout(title=dict(text=title,x=.04,font=dict(size=15,color="#f5f8ff")),
            height=390,margin=dict(l=8,r=8,t=45,b=20),paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#9db3c8"),
            legend=dict(orientation="v",y=.95,x=.70,xanchor="left",yanchor="top",
                        font=dict(size=9,color="#d9e9f7"),itemsizing="constant"))
    else:
        fig.update_layout(title=dict(text=title,x=.04,font=dict(size=15,color="#f5f8ff")),
            height=300,margin=dict(l=8,r=8,t=45,b=75),paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#9db3c8"),
            legend=dict(orientation="h",y=-.18,x=0,font=dict(size=10,color="#d9e9f7")))
    total=sum(data.values())
    fig.add_annotation(x=.37 if title=="OBSTÁCULO" else .5,y=.515 if title=="OBSTÁCULO" else .5,
        text=f"<b>{total:.0f}</b><br><span style='font-size:10px;color:#7fa4bd'>TOTAL</span>",
        showarrow=False,align="center",font=dict(size=24,color="#f5f8ff",family="Arial Black"))
    return fig

def kpi(label,value,sub=""):
    st.markdown(f'<div class="kpi"><div class="klabel">{label}</div><div class="kvalue">{value}</div><div class="ksub">{sub}</div></div>',unsafe_allow_html=True)

def make_pdf(athlete, cur, sessions, choice):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.units import mm

    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=landscape(A4),rightMargin=12*mm,leftMargin=12*mm,topMargin=12*mm,bottomMargin=12*mm)
    styles=getSampleStyleSheet()
    title=ParagraphStyle("T",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=32,textColor=colors.HexColor("#0D4E7A"),alignment=TA_LEFT,spaceAfter=5)
    h=ParagraphStyle("H",parent=styles["Heading2"],fontName="Helvetica-Bold",fontSize=20,textColor=colors.HexColor("#0D4E7A"),spaceBefore=8,spaceAfter=6)
    body=ParagraphStyle("B",parent=styles["BodyText"],fontSize=13,textColor=colors.HexColor("#263746"))
    story=[Paragraph("SKATE PERFORMANCE",title),
           Paragraph(f"{athlete or 'ATLETA'} - {choice}",body),Spacer(1,6)]
    rate=cur["hits"]/cur["attempts"]*100 if cur["attempts"] else 0
    kdata=[["TENTATIVAS","ACERTOS","ERROS","TAXA DE ACERTO","TREINOS"],
           [f'{cur["attempts"]:.0f}',f'{cur["hits"]:.0f}',f'{cur["errors"]:.0f}',f'{rate:.1f}%',str(len(sessions))]]
    kt=Table(kdata,colWidths=[50*mm]*5,rowHeights=[8*mm,13*mm])
    kt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0D4E7A")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BACKGROUND",(0,1),(-1,1),colors.HexColor("#EDF5FA")),("TEXTCOLOR",(0,1),(-1,1),colors.HexColor("#102536")),
        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),10),("FONTSIZE",(0,1),(-1,1),20),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#A9C7DA"))
    ]))
    story += [kt,Spacer(1,8),Paragraph("MANOBRAS",h)]
    rows=[["MANOBRA","ACERTOS","ERROS","TOTAL","TAXA"]]
    for m,(hh,ee) in sorted(cur["maneuvers"].items(),key=lambda x:sum(x[1]),reverse=True):
        tt=hh+ee; rr=hh/tt*100 if tt else 0
        rows.append([m,f"{hh:.0f}",f"{ee:.0f}",f"{tt:.0f}",f"{rr:.1f}%"])
    if len(rows)==1: rows.append(["Sem dados","0","0","0","0.0%"])
    mt=Table(rows,colWidths=[110*mm,32*mm,32*mm,32*mm,35*mm],repeatRows=1)
    mt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#102C43")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F4F8FB")]),
        ("TEXTCOLOR",(0,1),(-1,-1),colors.HexColor("#1D2D3A")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),10),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#C9D9E4")),
        ("ALIGN",(1,1),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE")
    ]))
    story.append(mt)
    if len(sessions)>1:
        story += [PageBreak(),Paragraph("EVOLUCAO ENTRE TREINOS",title)]
        ev=[["TREINO","TENTATIVAS","ACERTOS","ERROS","TAXA","DIFICULDADE ALTA"]]
        for s in sessions:
            rr=s["hits"]/s["attempts"]*100 if s["attempts"] else 0
            alta=s["cats"]["DIFICULDADE"].get("ALTA",0)
            ev.append([s["name"],f'{s["attempts"]:.0f}',f'{s["hits"]:.0f}',f'{s["errors"]:.0f}',f"{rr:.1f}%",f"{alta:.0f}"])
        et=Table(ev,colWidths=[105*mm,30*mm,30*mm,30*mm,30*mm,40*mm],repeatRows=1)
        et.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#102C43")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F4F8FB")]),
            ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#C9D9E4")),("FONTSIZE",(0,0),(-1,-1),10),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("ALIGN",(1,1),(-1,-1),"CENTER")
        ]))
        story.append(et)
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

def make_visual_pdf(athlete, cur, sessions, choice, photo_file=None):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    import math

    buf=io.BytesIO(); W,H=landscape(A3)
    bg=colors.HexColor("#06111f"); panel=colors.HexColor("#0b1d31")
    panel2=colors.HexColor("#0d243b"); white=colors.HexColor("#f5f8ff")
    muted=colors.HexColor("#9bb2c8"); blue=colors.HexColor("#1398ff")
    lightblue=colors.HexColor("#6bc1f7"); red=colors.HexColor("#ff4050")
    green=colors.HexColor("#16d98b"); yellow=colors.HexColor("#f4cf43")
    purple=colors.HexColor("#a46cff"); orange=colors.HexColor("#ff8b3d")
    palette=[blue,lightblue,red,green,yellow,purple,orange]
    c=canvas.Canvas(buf,pagesize=(W,H))

    def page_bg():
        c.setFillColor(bg); c.rect(0,0,W,H,fill=1,stroke=0)

    def header(sub="PERFORMANCE ANALYSIS • TRAINING INTELLIGENCE"):
        c.setFillColor(panel); c.roundRect(10*mm,H-31*mm,W-20*mm,20*mm,4*mm,fill=1,stroke=0)
        # Cabeçalho com posições calculadas para nunca sobrepor PERFORMANCE / TIME BRASIL
        hx=17*mm
        c.setFillColor(white); c.setFont("Helvetica-BoldOblique",23)
        c.drawString(hx,H-22*mm,"SKATE")
        skate_w=c.stringWidth("SKATE","Helvetica-BoldOblique",23)

        perf_x=hx+skate_w+2.0*mm
        c.setFillColor(blue); c.setFont("Helvetica-BoldOblique",23)
        c.drawString(perf_x,H-22*mm,"PERFORMANCE")
        perf_w=c.stringWidth("PERFORMANCE","Helvetica-BoldOblique",23)

        time_x=perf_x+perf_w+5.5*mm
        c.setStrokeColor(colors.HexColor("#6f8da5")); c.setLineWidth(.6)
        c.line(time_x-2.8*mm,H-26*mm,time_x-2.8*mm,H-16.5*mm)
        c.setFillColor(white); c.setFont("Helvetica-Bold",11.5)
        c.drawString(time_x,H-22*mm,"TIME BRASIL")
        c.setFillColor(lightblue); c.setFont("Helvetica",8.5); c.drawString(17*mm,H-27*mm,sub)
        c.setFillColor(blue); c.setFont("Helvetica-Bold",9.5); c.drawRightString(W-17*mm,H-21*mm,"SPORTSCODE ANALYTICS")
        c.setFillColor(muted); c.setFont("Helvetica",8); c.drawRightString(W-17*mm,H-26*mm,"TRAINING DATA DASHBOARD")

    def section(title,y):
        c.setFillColor(white); c.setFont("Helvetica-Bold",17); c.drawString(12*mm,y,title)

    def card(x,y,w,h,label,value,sub="",value_color=None):
        c.setFillColor(panel2); c.roundRect(x,y,w,h,3*mm,fill=1,stroke=0)
        c.setStrokeColor(colors.HexColor("#245071")); c.roundRect(x,y,w,h,3*mm,fill=0,stroke=1)
        c.setFillColor(muted); c.setFont("Helvetica-Bold",12.5); c.drawString(x+4*mm,y+h-7*mm,label)
        c.setFillColor(value_color or white); c.setFont("Helvetica-Bold",30); c.drawString(x+4*mm,y+8*mm,str(value))
        if sub:
            c.setFillColor(lightblue if value_color is None else value_color); c.setFont("Helvetica",11.5); c.drawString(x+4*mm,y+3.5*mm,sub)

    def donut(x,y,r,title,data,colorset=None):
        vals=[(str(k),float(v)) for k,v in data.items() if float(v)>0]
        total=sum(v for _,v in vals)
        c.setFillColor(white); c.setFont("Helvetica-Bold",15); c.drawCentredString(x,y+r+9*mm,title)
        if not vals or total<=0:
            c.setFillColor(muted); c.setFont("Helvetica",10); c.drawCentredString(x,y,"SEM DADOS"); return

        # Cores fixas por significado. Assim pizza e legenda sempre usam a MESMA cor,
        # independentemente da ordem em que o Sportscode exportar as categorias.
        semantic = {
            "ACERTO": green, "ERRO": red,
            "BOM": blue, "RUIM": red, "EXCELENTE": green,
            "BAIXA": blue, "MEDIA": green, "MÉDIA": green, "ALTA": red,
            "BAIXO": blue, "MEDIO": green, "MÉDIO": green, "ALTO": red,
            "NORMAL": blue, "LENTO": red, "RAPIDO": green, "RÁPIDO": green,
            "SWITCH": blue, "NOLLIE": green, "FAKIE": red,
            "FRONTSIDE": green, "BACKSIDE": lightblue, "REVERSE": red,
        }
        assigned=[]
        for i,(lab,v) in enumerate(vals):
            key=lab.strip().upper()
            if colorset is not None and i < len(colorset):
                assigned.append(colorset[i])
            elif key in semantic:
                assigned.append(semantic[key])
            else:
                assigned.append(palette[i%len(palette)])

        angle=90
        for i,(lab,v) in enumerate(vals):
            extent=360*v/total
            c.setFillColor(assigned[i])
            c.wedge(x-r,y-r,x+r,y+r,angle,extent,fill=1,stroke=0)
            # V2.0 — percentual diretamente na fatia do dashboard visual.
            # Posiciona o texto entre o furo e a borda para permanecer legível.
            import math
            mid = math.radians(angle + extent / 2.0)
            tx = x + math.cos(mid) * r * .79
            ty = y + math.sin(mid) * r * .79
            pct = v / total * 100
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 15.5 if extent >= 24 else 12.0)
            c.drawCentredString(tx, ty-1.5, f"{pct:.0f}%")
            angle+=extent
        c.setFillColor(bg); c.circle(x,y,r*.58,fill=1,stroke=0)

        ly=y-r-7*mm; colw=36*mm
        for i,(lab,v) in enumerate(vals[:8]):
            row=i//2; col=i%2; lx=x-r+col*colw
            c.setFillColor(assigned[i]); c.rect(lx,ly-row*5*mm,2.5*mm,2.5*mm,fill=1,stroke=0)
            c.setFillColor(white); c.setFont("Helvetica-Bold",10.8)
            pct=v/total*100
            c.drawString(lx+4*mm,ly-row*5*mm,f"{lab[:16]}  {pct:.1f}%")

    def line_chart(x,y,w,h,title,values,color=blue,suffix=""):
        c.setFillColor(white); c.setFont("Helvetica-Bold",13); c.drawString(x,y+h+5*mm,title)
        c.setStrokeColor(colors.HexColor("#173047")); c.setLineWidth(.5)
        for j in range(5):
            gy=y+j*h/4; c.line(x,gy,x+w,gy)
        if not values:return
        mx=max(max(values),1); pts=[]
        for i,v in enumerate(values):
            xx=x+w*(i/max(1,len(values)-1)); yy=y+h*(v/mx*.88); pts.append((xx,yy))
        c.setStrokeColor(color); c.setLineWidth(2)
        for a,b in zip(pts,pts[1:]): c.line(a[0],a[1],b[0],b[1])
        for i,(xx,yy) in enumerate(pts):
            c.setFillColor(color); c.circle(xx,yy,1.7*mm,fill=1,stroke=0)
            c.setFillColor(white); c.setFont("Helvetica-Bold",8); c.drawCentredString(xx,yy+3*mm,f"{values[i]:.1f}{suffix}")
            c.setFillColor(muted); c.setFont("Helvetica",7); c.drawCentredString(xx,y-4*mm,sessions[i]["name"][:24])

    # PAGE 1
    page_bg(); header()
    # Athlete/photo block
    px,py,pw,ph=12*mm,H-92*mm,55*mm,54*mm
    c.setFillColor(panel); c.roundRect(px,py,pw,ph,3*mm,fill=1,stroke=0)
    if photo_file is not None:
        try:
            photo_file.seek(0); im=ImageReader(photo_file)
            iw,ih=im.getSize(); scale=min((pw-4*mm)/iw,(ph-4*mm)/ih)
            dw,dh=iw*scale,ih*scale
            c.drawImage(im,px+(pw-dw)/2,py+(ph-dh)/2,dw,dh,preserveAspectRatio=True,mask='auto')
        except Exception: pass
    c.setFillColor(white); c.setFont("Helvetica-Bold",22); c.drawString(12*mm,H-101*mm,(athlete or "ATLETA").upper())
    c.setFillColor(muted); c.setFont("Helvetica",12); c.drawString(12*mm,H-107*mm,f"{len(sessions)} treino(s) • {choice}")

    rate=cur["hits"]/cur["attempts"]*100 if cur["attempts"] else 0
    vals=[("TENTATIVAS",f'{cur["attempts"]:.0f}',"volume total",None),
          ("MANOBRAS",str(len(cur["maneuvers"])),"diferentes",None),
          ("ACERTOS",f'{cur["hits"]:.0f}',f"{rate:.1f}% de acerto",None),
          ("ERROS",f'{cur["errors"]:.0f}',f"{100-rate:.1f}%",red),
          ("TREINOS",str(len(sessions)),"CSVs importados",None)]
    kx=73*mm; ky=H-78*mm; gap=3*mm; kw=(W-kx-12*mm-gap*4)/5
    for i,(lab,val,sub,col) in enumerate(vals): card(kx+i*(kw+gap),ky,kw,28*mm,lab,val,sub,col)

    section("DISTRIBUIÇÕES GERAIS",H-123*mm)
    cy=H-169*mm; rr=25*mm
    ds=[("RESULTADO",{"ACERTO":cur["hits"],"ERRO":cur["errors"]},[green,red]),
        ("DIFICULDADE",cur["cats"]["DIFICULDADE"],None),
        ("RISCO",cur["cats"]["RISCO"],None),
        ("DIREÇÃO",cur["cats"]["DIRECAO"],None)]
    centers=[58*mm,150*mm,242*mm,334*mm]
    for xx,(t,d,cc) in zip(centers,ds): donut(xx,cy,rr,t,d,cc)

    # Maneuver table lower
    section("MANOBRAS",H-221*mm)
    tx=12*mm; ty=H-232*mm; widths=[12*mm,220*mm,38*mm,38*mm,38*mm,44*mm]
    headers=["#","MANOBRA","ACERTOS","ERROS","TOTAL","TAXA"]
    c.setFillColor(colors.HexColor("#0d2237")); c.rect(tx,ty-8*mm,sum(widths),8*mm,fill=1,stroke=0)
    c.setFillColor(muted); c.setFont("Helvetica-Bold",10.5); xx=tx
    for h,w in zip(headers,widths): c.drawString(xx+2*mm,ty-5*mm,h); xx+=w
    yy=ty-15*mm
    all_maneuvers=sorted(cur["maneuvers"].items(),key=lambda z:sum(z[1]),reverse=True)
    for idx,(m,(hh,ee)) in enumerate(all_maneuvers[:8],1):
        tt=hh+ee; rr2=hh/tt*100 if tt else 0
        row=[str(idx),m[:35],f"{hh:.0f}",f"{ee:.0f}",f"{tt:.0f}",f"{rr2:.1f}%"]
        c.setFillColor(panel if idx%2 else panel2); c.rect(tx,yy,sum(widths),6.7*mm,fill=1,stroke=0)
        xx=tx
        for j,(v,w) in enumerate(zip(row,widths)):
            c.setFillColor(red if j==3 else (blue if j in (2,5) else white)); c.setFont("Helvetica-Bold" if j in (1,2,3,5) else "Helvetica",11.5)
            c.drawString(xx+2*mm,yy+2.2*mm,v); xx+=w
        yy-=7.2*mm
    c.showPage()

    # PÁGINAS EXTRAS: todas as manobras restantes, sem cortar a lista.
    remaining=all_maneuvers[8:]
    chunk_size=28
    for chunk_start in range(0,len(remaining),chunk_size):
        page_bg(); header("MANEUVER ANALYSIS • COMPLETE LIST")
        section("MANOBRAS — CONTINUAÇÃO",H-45*mm)
        tx=12*mm; ty=H-57*mm
        widths=[12*mm,220*mm,38*mm,38*mm,38*mm,44*mm]
        headers=["#","MANOBRA","ACERTOS","ERROS","TOTAL","TAXA"]
        c.setFillColor(colors.HexColor("#0d2237")); c.rect(tx,ty-9*mm,sum(widths),9*mm,fill=1,stroke=0)
        c.setFillColor(muted); c.setFont("Helvetica-Bold",10.5); xx=tx
        for h,w in zip(headers,widths):
            c.drawString(xx+2*mm,ty-5.8*mm,h); xx+=w
        yy=ty-17*mm
        chunk=remaining[chunk_start:chunk_start+chunk_size]
        for local_i,(m,(hh,ee)) in enumerate(chunk):
            idx=9+chunk_start+local_i
            tt=hh+ee; rr2=hh/tt*100 if tt else 0
            row=[str(idx),m[:58],f"{hh:.0f}",f"{ee:.0f}",f"{tt:.0f}",f"{rr2:.1f}%"]
            c.setFillColor(panel if idx%2 else panel2); c.rect(tx,yy,sum(widths),7*mm,fill=1,stroke=0)
            xx=tx
            for j,(v,w) in enumerate(zip(row,widths)):
                c.setFillColor(red if j==3 else (blue if j in (2,5) else white))
                c.setFont("Helvetica-Bold" if j in (1,2,3,5) else "Helvetica",11.5)
                c.drawString(xx+2*mm,yy+2.3*mm,v); xx+=w
            yy-=7.6*mm
        c.setFillColor(muted); c.setFont("Helvetica",8)
        c.drawRightString(W-12*mm,10*mm,f"Manobras {9+chunk_start}–{8+chunk_start+len(chunk)} de {len(all_maneuvers)}")
        c.showPage()

    # ÚLTIMA PÁGINA: evolution + details
    page_bg(); header("SESSION EVOLUTION • PERFORMANCE DISTRIBUTION")
    section("EVOLUÇÃO ENTRE TREINOS",H-45*mm)
    rates=[ss["hits"]/ss["attempts"]*100 if ss["attempts"] else 0 for ss in sessions]
    line_chart(18*mm,H-105*mm,W-36*mm,45*mm,"TAXA DE ACERTO",rates,blue,"%")
    section("EVOLUÇÃO DA DIFICULDADE",H-125*mm)
    chartw=(W-42*mm)/3
    for i,(dif,col) in enumerate([("ALTA",red),("MEDIA",blue),("BAIXA",lightblue)]):
        vv=[ss["cats"]["DIFICULDADE"].get(dif,0) for ss in sessions]
        line_chart(14*mm+i*(chartw+7*mm),H-180*mm,chartw,35*mm,dif,vv,col,"")
    section("DETALHES",H-201*mm)
    details=[("AVALIAÇÃO",cur["cats"]["AVALIACAO"]),("VELOCIDADE",cur["cats"]["VELOCIDADE"]),
             ("OBSTÁCULO",cur["cats"]["OBSTACULO"]),("BASE",cur["cats"]["BASE"])]
    for xx,(t,d) in zip(centers,details): donut(xx,H-246*mm,22*mm,t,d,None)
    c.save(); buf.seek(0); return buf.getvalue()

def table_html(mans):
    rows=[]
    items=sorted(mans.items(),key=lambda x:sum(x[1]),reverse=True)
    for i,(m,(h,e)) in enumerate(items,1):
        t=h+e;r=(h/t*100 if t else 0)
        rows.append(f"<tr><td>{i}</td><td><b>{m}</b></td><td class='hit'>{h:.0f}</td><td class='err'>{e:.0f}</td><td>{t:.0f}</td><td class='rate'>{r:.1f}%</td></tr>")
    if not rows: rows=["<tr><td colspan='6'>Nenhuma manobra detectada nesta sessão.</td></tr>"]
    return ('<div class="table-wrap"><table class="sk-table"><thead><tr>'
            '<th>#</th><th>MANOBRA</th><th>ACERTOS</th><th>ERROS</th><th>TOTAL</th><th>TAXA DE ACERTO</th>'
            '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>')


st.markdown("""<style>
@media(max-width:768px){
  [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.65rem!important}
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{flex:1 1 100%!important;width:100%!important;min-width:100%!important}
  [data-testid="stPlotlyChart"]{width:100%!important;max-width:100%!important;overflow:visible!important}
  [data-testid="stPlotlyChart"] > div{width:100%!important}
  .js-plotly-plot,.plot-container,.svg-container{width:100%!important;max-width:100%!important}
  .sk-table{font-size:11px!important;min-width:680px!important}
  .table-wrap{overflow-x:auto!important;-webkit-overflow-scrolling:touch!important}
}
</style>""",unsafe_allow_html=True)
st.markdown("""
<style>
/* V4.15 — Análise em tela cheia: remove definitivamente a navegação lateral antiga */
section[data-testid="stSidebar"],
aside[data-testid="stSidebar"],
div[data-testid="stSidebar"],
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarContent"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"]{display:none!important;width:0!important;min-width:0!important;max-width:0!important;visibility:hidden!important}
[data-testid="stAppViewContainer"] > .main,
[data-testid="stAppViewContainer"] > section.main,
section.main{margin-left:0!important;width:100%!important;max-width:100%!important}
[data-testid="stMain"], [data-testid="stMainBlockContainer"]{margin-left:0!important;width:100%!important;max-width:100%!important}
.block-container{max-width:1480px!important;width:100%!important;margin:0 auto!important;padding:0 26px 52px!important}
.analysis-nav{height:62px;margin:0 -26px 26px;padding:0 26px;display:flex;align-items:center;justify-content:space-between;
 background:linear-gradient(90deg,#061522,#071c2e 58%,#081827);border-bottom:1px solid #123d5c;box-shadow:0 10px 28px rgba(0,0,0,.2)}
.analysis-brand{display:flex;align-items:center;gap:11px}.analysis-mark{width:34px;height:34px;border:1px solid #087cff;border-radius:10px;
 display:grid;place-items:center;color:#20e6ff;box-shadow:0 0 18px rgba(0,217,255,.16);font-size:16px;font-weight:900}
.analysis-brand-main{font-size:12px;font-weight:900;letter-spacing:.11em;color:#f5f8fc}.analysis-brand-sub{font-size:8px;color:#29a8ff;letter-spacing:.13em;margin-top:2px}
.analysis-links{display:flex;gap:25px;font-size:10px;letter-spacing:.08em;color:#9bb0c4;font-weight:800}.analysis-links span.active{color:#f7fbff;border-bottom:2px solid #20e6ff;padding-bottom:18px}
.analysis-eyebrow{font-size:10px;color:#20e6ff;font-weight:900;letter-spacing:.18em;margin-bottom:6px}.analysis-title{font-size:38px;line-height:1.05;font-weight:950;color:#f7fbff;letter-spacing:-.02em;margin:0}
.analysis-lead{font-size:13px;color:#89a5bf;max-width:720px;margin-top:8px}.setup-card{background:linear-gradient(145deg,rgba(8,27,45,.96),rgba(5,19,32,.96));border:1px solid #174c70;border-radius:18px;padding:22px;margin:22px 0 18px;box-shadow:0 18px 45px rgba(0,0,0,.2)}
.setup-title{font-size:17px;font-weight:900;color:#f5f8fc;margin-bottom:2px}.setup-sub{font-size:11px;color:#7895ae;margin-bottom:14px}
.video-card{background:linear-gradient(145deg,#081b2d,#071625);border:1px solid #244a68;border-radius:16px;padding:18px 20px;margin:18px 0}.video-title{font-size:17px;font-weight:900;color:#f5f8fc}.video-kicker{font-size:10px;color:#d45aff;font-weight:900;letter-spacing:.14em;margin-bottom:4px}
[data-testid="stRadio"] label,[data-testid="stRadio"] p{color:#dcecff!important}
[data-testid="stTextInput"] label,[data-testid="stDateInput"] label,[data-testid="stSelectbox"] label,[data-testid="stFileUploader"] label{color:#dcecff!important;font-weight:700!important}
/* V4.15 — todos os campos da configuração permanecem dark, inclusive data e calendário */
[data-testid="stTextInput"] > div > div,
[data-testid="stDateInput"] > div > div,
[data-testid="stDateInput"] div[data-baseweb="input"],
[data-testid="stDateInput"] input,
[data-testid="stDateInput"] button,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stFileUploaderDropzone"]{background:#0a1d30!important;background-color:#0a1d30!important;border-color:#245274!important;color:#eef8ff!important}
[data-testid="stTextInput"] input,[data-testid="stDateInput"] input{color:#eef8ff!important;-webkit-text-fill-color:#eef8ff!important}
[data-testid="stDateInput"] input::placeholder,[data-testid="stTextInput"] input::placeholder{color:#6f8ba4!important;-webkit-text-fill-color:#6f8ba4!important}
[data-baseweb="calendar"], [data-baseweb="calendar"] > div, [role="dialog"] [data-baseweb="calendar"]{background:#081827!important;color:#eef8ff!important}
[data-baseweb="calendar"] button,[data-baseweb="calendar"] div,[data-baseweb="calendar"] span{color:#dcecff!important}
[data-baseweb="input"], [data-baseweb="select"]>div, [data-testid="stFileUploaderDropzone"]{background:#0a1d30!important;border-color:#245274!important;color:#eef8ff!important}
[data-baseweb="input"] input,[data-baseweb="select"] *,[data-testid="stFileUploaderDropzone"] *{color:#eef8ff!important;-webkit-text-fill-color:#eef8ff!important}
[data-testid="stFileUploaderDropzone"] button{background:#0d2a43!important;color:#eef8ff!important;border:1px solid #178bd1!important}
[data-testid="stFileUploaderFile"]{background:#0a1d30!important;border:1px solid #245274!important}[data-testid="stFileUploaderFile"] *{color:#dcecff!important;-webkit-text-fill-color:#dcecff!important}
.analysis-status{display:inline-flex;gap:8px;align-items:center;padding:7px 11px;border-radius:999px;background:#08263a;border:1px solid #15577b;color:#86d8ff;font-size:10px;font-weight:800;margin:4px 6px 4px 0}
@media(max-width:800px){.analysis-links{display:none}.analysis-title{font-size:30px}.block-container{padding-left:15px!important;padding-right:15px!important}.analysis-nav{margin-left:-15px;margin-right:-15px;padding-left:15px;padding-right:15px}}
</style>
""", unsafe_allow_html=True)

# V4.17 — mesma navbar Material UI aprovada na Home/Times.
nav_name = str((profile or {}).get("full_name") or getattr(user, "email", None) or "Usuário").strip()
nav_role = str((profile or {}).get("role") or "membro").replace("_", " ").title()
nav_photo = (profile or {}).get("photo_url")
nav_initials = "".join(part[:1].upper() for part in nav_name.split()[:2]) or "U"

with elements("analysis_top_nav"):
    with mui.Paper(elevation=0, square=True, sx={
        "mb":2,"backgroundColor":"#061523","border":"1px solid #163b59",
        "borderRadius":"0 0 14px 14px","minHeight":62,"display":"flex",
        "alignItems":"center","px":{"xs":1,"md":2},"fontFamily":"\"Segoe UI Variable\", Inter, Manrope, Arial, sans-serif"
    }):
        with mui.Box(sx={"display":"flex","alignItems":"center","gap":{"xs":1,"md":3},"width":"100%","overflowX":"auto"}):
            with mui.Box(sx={"display":"flex","alignItems":"center","gap":1.1,"mr":{"xs":1,"md":3},"flexShrink":0}):
                mui.icon.AutoAwesome(sx={"color":"#20e6ff","fontSize":27})
                with mui.Box:
                    mui.Typography("ANÁLISE • EVOLUÇÃO • PERFORMANCE", sx={"color":"#f5f8fc","fontWeight":950,"fontSize":12,"letterSpacing":".7px","lineHeight":1.2})
                    mui.Typography("SKATEBOARDING PERFORMANCE SYSTEM", sx={"color":"#20e6ff","fontWeight":850,"fontSize":7,"letterSpacing":"2px","mt":.45})
            for label, Icon, active in [
                ("Home",mui.icon.HomeOutlined,False),("Análise",mui.icon.AnalyticsOutlined,True),
                ("Atletas",mui.icon.GroupsOutlined,False),("Times",mui.icon.ShieldOutlined,False),
                ("Histórico",mui.icon.History,False)
            ]:
                with mui.Button(startIcon=Icon(), sx={
                    "height":61,"minWidth":"auto","px":1,"flexShrink":0,"textTransform":"none",
                    "borderRadius":0,"color":"#20e6ff" if active else "#9fb4c7",
                    "borderBottom":"2px solid #20e6ff" if active else "2px solid transparent",
                    "fontSize":12,"fontWeight":850
                }):
                    mui.Typography(label,sx={"fontSize":12,"fontWeight":850})

            with mui.Box(sx={"ml":"auto","display":{"xs":"none","md":"flex"},"alignItems":"center","gap":1.0,"pl":1.5,"flexShrink":0}):
                with mui.Box(sx={"textAlign":"right","lineHeight":1.05}):
                    mui.Typography(nav_name,sx={"color":"#f5f8fc","fontSize":10.5,"fontWeight":900,"maxWidth":145,"whiteSpace":"nowrap","overflow":"hidden","textOverflow":"ellipsis"})
                    mui.Typography(nav_role,sx={"color":"#20e6ff","fontSize":7.5,"fontWeight":800,"letterSpacing":".45px"})
                if nav_photo:
                    mui.Avatar(src=nav_photo,sx={"width":35,"height":35,"border":"1px solid #20e6ff","boxShadow":"0 0 12px rgba(32,230,255,.22)"})
                else:
                    mui.Avatar(nav_initials,sx={"width":35,"height":35,"bgcolor":"#0c3554","color":"#20e6ff","border":"1px solid #20e6ff","fontSize":10,"fontWeight":950})

st.markdown("""
<div class="analysis-eyebrow">SELEÇÃO BRASILEIRA • PERFORMANCE ANALYTICS</div>
<div class="analysis-title">Análise de Treino</div>
<div class="analysis-lead">Centralize os dados do treino, importe os CSVs do Sportscode e acompanhe a evolução técnica do atleta em um único dashboard.</div>
""", unsafe_allow_html=True)

# V4.14 — a análise pode nascer de upload novo ou de uma sessão salva, sem controles na sidebar.
sb = get_supabase()
try:
    athlete_rows = (
        sb.table("profiles")
        .select("id,full_name,email,role,status,modality,stance,photo_url,birth_date,city,state")
        .eq("role", "skatista").eq("status", "ativo").order("full_name").execute().data or []
    )
except Exception as e:
    st.error(f"Não foi possível carregar os skatistas cadastrados: {e}"); st.stop()

analysis_photo = None
if history_view:
    selected_athlete = next((r for r in athlete_rows if r.get("id") == history_view.get("athlete_id")), None)
    if selected_athlete is None:
        st.error("Este treino não está disponível para o seu perfil."); st.stop()
    athlete = selected_athlete.get("full_name") or "ATLETA"
    photo_url = selected_athlete.get("photo_url")
    with st.container(border=True):
        c1,c2=st.columns([5,1])
        with c1:
            st.markdown("#### 👁 Modo histórico")
            st.caption(f"{history_view.get('title','Treino')} • {history_view.get('training_date') or '—'}")
        with c2:
            if st.button("← Histórico", use_container_width=True):
                st.session_state.pop("history_analysis_view", None); st.switch_page("pages/04_Historico_de_Treinos.py")
    class ArchivedUpload(io.BytesIO):
        def __init__(self, data, name): super().__init__(data); self.name=name
        def getvalue(self): return super().getvalue()
    files=[ArchivedUpload(item["data"], item["name"]) for item in history_view.get("files",[])]
    training_date = date.fromisoformat(history_view["training_date"]) if history_view.get("training_date") else date.today()
    training_title = history_view.get("title") or "Treino"
else:
    st.markdown('<div class="setup-card"><div class="setup-title">Configurar nova análise</div><div class="setup-sub">Selecione o atleta, identifique o treino e importe um ou mais arquivos CSV.</div></div>', unsafe_allow_html=True)
    analysis_subject = st.radio("QUEM SERÁ ANALISADO?", ["Atleta cadastrado", "Atleta convidado / sem cadastro"], horizontal=True)
    guest_mode = analysis_subject.startswith("Atleta convidado")
    if guest_mode:
        c1,c2,c3=st.columns([2,1,1])
        with c1: guest_name=st.text_input("NOME DO ATLETA CONVIDADO",placeholder="Ex.: John Doe")
        with c2: guest_modality=st.selectbox("MODALIDADE",["Street","Park","Vert","Outro"])
        with c3: guest_stance=st.selectbox("BASE",["Regular","Goofy","Não informado"])
        selected_athlete={"id":None,"full_name":guest_name.strip() or "ATLETA CONVIDADO","modality":guest_modality,"stance":None if guest_stance=="Não informado" else guest_stance,"photo_url":None}
        athlete=selected_athlete["full_name"]; photo_url=None
        st.caption("Análise temporária: o convidado não é cadastrado nem salvo no Histórico.")
    else:
        if not athlete_rows:
            st.info("Ainda não há skatistas ativos disponíveis para análise."); st.stop()
        athlete_by_label={f"{r.get('full_name') or 'Sem nome'}"+(f" • {r.get('modality')}" if r.get('modality') else ""):r for r in athlete_rows}
        athlete_label=st.selectbox("ATLETA CADASTRADO",list(athlete_by_label.keys()))
        selected_athlete=athlete_by_label[athlete_label]; athlete=selected_athlete.get("full_name") or "ATLETA"; photo_url=selected_athlete.get("photo_url")
    info=" • ".join([x for x in [selected_athlete.get("modality"),selected_athlete.get("stance")] if x])
    if info: st.caption(info)
    c1,c2=st.columns([1,2])
    with c1: training_date=st.date_input("DATA DO TREINO",value=date.today())
    with c2: training_title=st.text_input("TÍTULO DO TREINO",placeholder="Ex.: Treino Street - manhã")
    analysis_photo=st.file_uploader("FOTO PARA A ANÁLISE (OPCIONAL)",type=["jpg","jpeg","png","webp"],accept_multiple_files=False)
    files=st.file_uploader("ARQUIVOS CSV (TREINOS)",type=["csv","txt"],accept_multiple_files=True)

photo=None
if photo_url:
    try: photo=io.BytesIO(urlopen(photo_url,timeout=8).read())
    except Exception: photo=None
if analysis_photo is not None: photo=io.BytesIO(analysis_photo.getvalue())

# Área de vídeo separada visualmente da análise por CSV.
if selected_athlete.get("id") and profile.get("role") == "admin":
    try: video_posts=sb.table("athlete_posts").select("id,session_title,created_at,upload_kind,analysis_status").eq("athlete_id",selected_athlete["id"]).order("created_at",desc=True).execute().data or []
    except Exception: video_posts=[]
    if video_posts:
        with st.expander("🎬 CODIFICAÇÃO DE VÍDEO", expanded=False):
            st.caption("Abra uma sessão de vídeo para marcar tentativas. Esta área fica separada do dashboard de CSV.")
            labels=[f"{vp.get('session_title') or 'Vídeo de treino'} • {(vp.get('created_at') or '')[:10]}" for vp in video_posts]
            pick=st.selectbox("Sessão de vídeo",range(len(video_posts)),format_func=lambda i:labels[i],key="video_session_pick")
            if st.button("ABRIR CODIFICAÇÃO",type="primary",use_container_width=True,key="open_video_coding"):
                st.session_state["selected_video_post_id"]=video_posts[pick]["id"]; st.switch_page("pages/10_Codificar_Sessao.py")

# Resultados de vídeo em painel recolhível para não competir com a análise de CSV.
if selected_athlete.get('id'):
    try: ve=sb.table('trick_video_events').select('*').eq('athlete_id',selected_athlete['id']).order('created_at',desc=True).execute().data or []
    except Exception: ve=[]
    try: legacy=sb.table('trick_video_analyses').select('*').eq('athlete_id',selected_athlete['id']).order('analyzed_at',desc=True).execute().data or []
    except Exception: legacy=[]
    video_attempts=ve if ve else legacy
    if video_attempts:
        with st.expander("🎥 RESULTADOS DE VÍDEO", expanded=False):
            total=len(video_attempts); hits=sum(1 for x in video_attempts if x.get('result')=='Acerto'); errors=total-hits; rate=(hits/total*100) if total else 0
            st.markdown(f"""<div class="video-kpi-grid">
<div class="video-kpi"><div class="vk-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v3M22 12h-3"/></svg></div><div><div class="vk-label">TENTATIVAS</div><div class="vk-value">{total}</div></div></div>
<div class="video-kpi"><div class="vk-icon"><svg viewBox="0 0 24 24"><path d="M5 12l4 4L19 6"/><circle cx="12" cy="12" r="9"/></svg></div><div><div class="vk-label">ACERTOS</div><div class="vk-value">{hits}</div></div></div>
<div class="video-kpi error"><div class="vk-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/></svg></div><div><div class="vk-label">ERROS</div><div class="vk-value">{errors}</div></div></div>
<div class="video-kpi"><div class="vk-icon"><svg viewBox="0 0 24 24"><path d="M7 17L17 7"/><circle cx="8" cy="8" r="2"/><circle cx="16" cy="16" r="2"/></svg></div><div><div class="vk-label">TAXA DE ACERTO</div><div class="vk-value">{rate:.1f}%</div></div></div>
</div>""",unsafe_allow_html=True)
            def dist_video(field):
                out={}
                for x in video_attempts:
                    v=x.get(field)
                    if v: out[v]=out.get(v,0)+1
                return out
            d1,d2,d3,d4=st.columns(4)
            for col,title,field in [(d1,'AVALIAÇÃO','evaluation'),(d2,'DIFICULDADE','difficulty'),(d3,'RISCO','risk'),(d4,'VELOCIDADE','speed')]:
                vals=dist_video(field)
                with col:
                    if vals: st.plotly_chart(donut(title,vals),use_container_width=True,config={"displayModeBar":False})

if not files:
    st.markdown('<div class="video-card"><div class="video-kicker">PRONTO PARA COMEÇAR</div><div class="video-title">Importe os CSVs para gerar o dashboard</div></div>', unsafe_allow_html=True)
    st.info("Envie um ou mais CSVs do Sportscode acima. O dashboard completo aparecerá aqui sem alterar os dados originais.")
    st.stop()

sessions=[]; problems=[]
for f in files:
    try:
        d=read_csv(f); sessions.append(parse_aggregate(d,Path(f.name).stem) if is_aggregate(d) else parse_raw(d,Path(f.name).stem))
    except Exception as e: problems.append(f"{f.name}: {e}")
for p in problems: st.warning(p)

# Um envio com vários CSVs representa um treino consolidado no histórico.
can_save = sessions and not history_view and profile.get("role") in ("admin","tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica") and selected_athlete.get("id")
if can_save:
    if st.button("💾 SALVAR TREINO NO HISTÓRICO",use_container_width=True):
        uploaded_paths=[]; report_path=visual_path=None
        try:
            token=uuid.uuid4().hex; base_path=f"{selected_athlete['id']}/{training_date.isoformat()}/{token}"
            for idx,f in enumerate(files):
                raw=f.getvalue(); ext=Path(f.name).suffix.lower() or ".csv"; safe_stem=re.sub(r"[^A-Za-z0-9_-]+","_",Path(f.name).stem)[:70] or f"treino_{idx+1}"
                object_path=f"{base_path}/{idx+1:02d}_{safe_stem}{ext}"
                sb.storage.from_("training-csvs").upload(object_path,raw,{"content-type":"text/csv","upsert":"false"}); uploaded_paths.append(object_path)
            title=training_title.strip() or (Path(files[0].name).stem if len(files)==1 else f"Treino consolidado • {len(files)} CSVs")
            report_path=f"{base_path}_relatorio.pdf"; visual_path=f"{base_path}_dashboard_visual.pdf"; merged=merge_sessions(sessions)
            report_bytes=make_pdf(athlete,merged,sessions,"TODOS OS TREINOS")
            if photo is not None: photo.seek(0)
            visual_bytes=make_visual_pdf(athlete,merged,sessions,"TODOS OS TREINOS",photo)
            sb.storage.from_("training-reports").upload(report_path,report_bytes,{"content-type":"application/pdf","upsert":"false"})
            sb.storage.from_("training-reports").upload(visual_path,visual_bytes,{"content-type":"application/pdf","upsert":"false"})
            sb.table("training_sessions").insert({"athlete_id":selected_athlete["id"],"training_date":training_date.isoformat(),"title":title,"csv_path":uploaded_paths[0] if uploaded_paths else None,"csv_paths":uploaded_paths,"report_pdf_path":report_path,"visual_pdf_path":visual_path}).execute()
            st.success(f"Treino salvo no histórico com {len(uploaded_paths)} CSV(s) consolidados.")
        except Exception as exc:
            try:
                if uploaded_paths: sb.storage.from_("training-csvs").remove(uploaded_paths)
                cleanup=[x for x in [report_path,visual_path] if x]
                if cleanup: sb.storage.from_("training-reports").remove(cleanup)
            except Exception: pass
            st.error(f"Não foi possível salvar o histórico: {exc}")

names=[s["name"] for s in sessions]
choice=st.selectbox("VISUALIZAR SESSÃO / CSV",["TODOS OS TREINOS"]+names,key="session_main")
cur=merge_sessions(sessions) if choice=="TODOS OS TREINOS" else next(s for s in sessions if s["name"]==choice)
st.markdown("".join([f'<span class="analysis-status">✓ {n}</span>' for n in names]),unsafe_allow_html=True)

head1,head2=st.columns([1.05,4.5])
with head1:
    if analysis_photo is not None:
        st.image(analysis_photo, use_container_width=True)
    elif photo_url:
        st.image(photo_url,use_container_width=True)
    else:
        st.markdown("### 📷 FOTO")
    st.markdown(f"### {athlete or 'ATLETA'}")
    sport_info = " • ".join([x for x in [selected_athlete.get("modality"), selected_athlete.get("stance")] if x])
    if sport_info:
        st.caption(sport_info)
    st.caption(f"{len(sessions)} treino(s) carregado(s)")
with head2:
    rate=cur["hits"]/cur["attempts"]*100 if cur["attempts"] else 0
    st.markdown(f"""
    <div class="kpi-shell">
      <div class="kpi-title">{(athlete.upper() if athlete else "DASHBOARD DE PERFORMANCE")}</div>
      <div class="kpi-subtitle">SKATEBOARDING • ANÁLISE DE PERFORMANCE • {choice}</div>
      <div class="kpi-grid">
        <div class="kpi2"><div class="kpi2-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v3M22 12h-3"/></svg></div><div class="kpi2-label">TENTATIVAS</div><div class="kpi2-value">{cur["attempts"]:.0f}</div><div class="kpi2-sub">volume total</div></div>
        <div class="kpi2"><div class="kpi2-icon"><svg viewBox="0 0 24 24"><path d="M5 16h14M7 16l-2 3M17 16l2 3"/><circle cx="8" cy="20" r="1.5"/><circle cx="16" cy="20" r="1.5"/><path d="M8 12c2-4 6-4 8 0"/></svg></div><div class="kpi2-label">MANOBRAS</div><div class="kpi2-value">{len(cur["maneuvers"])}</div><div class="kpi2-sub">manobras diferentes</div></div>
        <div class="kpi2"><div class="kpi2-icon"><svg viewBox="0 0 24 24"><path d="M5 12l4 4L19 6"/><circle cx="12" cy="12" r="9"/></svg></div><div class="kpi2-label">ACERTOS</div><div class="kpi2-value">{cur["hits"]:.0f}</div><div class="kpi2-sub">{rate:.1f}% de acerto</div></div>
        <div class="kpi2 kpi2-error"><div class="kpi2-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/></svg></div><div class="kpi2-label">ERROS</div><div class="kpi2-value">{cur["errors"]:.0f}</div><div class="kpi2-sub">{100-rate:.1f}%</div></div>
        <div class="kpi2"><div class="kpi2-icon"><svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M8 3v4M16 3v4M4 10h16"/></svg></div><div class="kpi2-label">TREINOS</div><div class="kpi2-value">{len(sessions)}</div><div class="kpi2-sub">CSVs importados</div></div>
      </div>
    </div>
    """,unsafe_allow_html=True)

st.markdown('<div class="section">DISTRIBUIÇÕES GERAIS</div>',unsafe_allow_html=True)
plots=[("RESULTADO",{"ACERTO":cur["hits"],"ERRO":cur["errors"]}),
       ("DIFICULDADE",cur["cats"]["DIFICULDADE"]),("RISCO",cur["cats"]["RISCO"]),("DIREÇÃO",cur["cats"]["DIRECAO"])]
cols=st.columns(4)
for col,(title,data) in zip(cols,plots):
    with col:
        if sum(data.values()):st.plotly_chart(donut(title,data),use_container_width=True,config={"displayModeBar":False})
        else:st.info(f"{title}: sem dados")

st.markdown('<div class="section">MANOBRAS</div>',unsafe_allow_html=True)
st.markdown(table_html(cur["maneuvers"]),unsafe_allow_html=True)

if len(sessions)>1:
    st.markdown('<div class="section">EVOLUÇÃO ENTRE TREINOS</div>',unsafe_allow_html=True)
    x=[s["name"] for s in sessions]
    y=[s["hits"]/s["attempts"]*100 if s["attempts"] else 0 for s in sessions]
    fig=go.Figure(go.Scatter(x=x,y=y,mode="lines+markers+text",
        line=dict(color="#1398ff",width=3),marker=dict(size=9,color="#1398ff"),
        text=[f"{v:.1f}%" for v in y],textposition="top center"))
    fig.update_layout(height=350,yaxis=dict(title="Taxa de acerto (%)",range=[0,max(100,max(y)+10)],
        gridcolor="#173047"),xaxis=dict(title="Sessão",gridcolor="#173047"),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#9db3c8"),
        margin=dict(l=30,r=20,t=30,b=40))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    evrows="".join(f"<tr><td>{s['name']}</td><td>{s['attempts']:.0f}</td><td class='hit'>{s['hits']:.0f}</td><td class='err'>{s['errors']:.0f}</td><td class='rate'>{(s['hits']/s['attempts']*100 if s['attempts'] else 0):.1f}%</td></tr>" for s in sessions)
    st.markdown('<div class="table-wrap"><table class="sk-table"><thead><tr><th>TREINO</th><th>TENTATIVAS</th><th>ACERTOS</th><th>ERROS</th><th>TAXA</th></tr></thead><tbody>' + evrows + '</tbody></table></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">EVOLUÇÃO DA DIFICULDADE</div>',unsafe_allow_html=True)
    difficulty_choice=st.selectbox("Dificuldade para acompanhar",["ALTA","MEDIA","BAIXA"],index=0,key="difficulty_evolution")
    yd=[s["cats"]["DIFICULDADE"].get(difficulty_choice,0) for s in sessions]
    difficulty_colors={"ALTA":"#ff4c5b","MEDIA":"#1398ff","BAIXA":"#6bc1f7"}
    dc=difficulty_colors[difficulty_choice]
    figd=go.Figure(go.Scatter(x=x,y=yd,mode="lines+markers+text",
        line=dict(color=dc,width=3),marker=dict(size=9,color=dc),
        text=[f"{v:.0f}" for v in yd],textposition="top center"))
    figd.update_layout(height=350,yaxis=dict(title=f"Manobras / tentativas de dificuldade {difficulty_choice}",rangemode="tozero",
        gridcolor="#173047"),xaxis=dict(title="Sessão",gridcolor="#173047"),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#d9e9f7"),
        margin=dict(l=30,r=20,t=30,b=40))
    st.plotly_chart(figd,use_container_width=True,config={"displayModeBar":False})

st.markdown('<div class="section">DETALHES</div>',unsafe_allow_html=True)
extra=[("AVALIAÇÃO",cur["cats"]["AVALIACAO"]),("VELOCIDADE",cur["cats"]["VELOCIDADE"]),("OBSTÁCULO",cur["cats"]["OBSTACULO"]),("BASE",cur["cats"]["BASE"])]
cols=st.columns(4)
for col,(title,data) in zip(cols,extra):
    with col:
        if sum(data.values()):st.plotly_chart(donut(title,data),use_container_width=True,config={"displayModeBar":False})
        else:st.info(f"{title}: sem dados")


st.markdown('<div class="section">EXPORTAR</div>',unsafe_allow_html=True)
pdf_bytes=make_pdf(athlete,cur,sessions,choice)
safe_name=re.sub(r"[^A-Za-z0-9_-]+","_",athlete.strip() if athlete else "atleta")
ex1,ex2=st.columns(2)
with ex1:
    st.download_button("⬇ BAIXAR RELATÓRIO EM PDF", data=pdf_bytes,
        file_name=f"skate_performance_relatorio_{safe_name}.pdf", mime="application/pdf", use_container_width=True)
with ex2:
    if photo is not None:
        photo.seek(0)
    visual_pdf=make_visual_pdf(athlete,cur,sessions,choice,photo)
    st.download_button("⬇ BAIXAR DASHBOARD VISUAL EM PDF", data=visual_pdf,
        file_name=f"skate_performance_dashboard_visual_{safe_name}.pdf", mime="application/pdf", use_container_width=True)




st.markdown("""
<style>
/* V4.16 — acabamento premium do dashboard; somente apresentação */
.section{font-size:22px!important;font-weight:950!important;color:#f7fbff!important;letter-spacing:.045em!important;margin:34px 0 14px!important;position:relative;padding-left:14px}
.section:before{content:"";position:absolute;left:0;top:4px;bottom:4px;width:3px;border-radius:5px;background:linear-gradient(180deg,#20e6ff,#087cff);box-shadow:0 0 14px rgba(32,230,255,.5)}
.kpi-shell{background:radial-gradient(circle at 88% 0%,rgba(0,217,255,.08),transparent 28%),linear-gradient(145deg,#081b2d,#061522)!important;border:1px solid #17608a!important;border-radius:18px!important;padding:22px!important;box-shadow:0 18px 45px rgba(0,0,0,.26),inset 0 1px 0 rgba(255,255,255,.025)!important}
.kpi-title{font-size:27px!important;letter-spacing:.015em!important}.kpi-subtitle{color:#50c8ff!important}
.kpi2{position:relative;overflow:hidden;background:linear-gradient(145deg,#0a2137,#07192a)!important;border:1px solid #1a608a!important;border-radius:14px!important;padding:15px!important;min-height:94px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.025),0 8px 22px rgba(0,0,0,.16)}
.kpi2:after{content:"";position:absolute;left:0;right:0;bottom:0;height:2px;background:linear-gradient(90deg,transparent,#16cfff,transparent);opacity:.75}
.kpi2-value{font-size:31px!important}.kpi2-label{color:#a9c7dc!important}.kpi2-sub{color:#52c9ff!important}.kpi2-error{border-color:#703044!important}.kpi2-error:after{background:linear-gradient(90deg,transparent,#ff4050,transparent)}
.analysis-status{background:linear-gradient(145deg,#08263a,#071d2f)!important;border-color:#1678a8!important;box-shadow:0 0 12px rgba(0,217,255,.08)}
/* cada gráfico ganha superfície própria sem alterar o Plotly */
[data-testid="stPlotlyChart"]{background:linear-gradient(145deg,rgba(9,28,46,.82),rgba(5,18,31,.82));border:1px solid #153f5d;border-radius:16px;padding:8px 8px 2px;box-shadow:0 12px 28px rgba(0,0,0,.14);overflow:hidden}
.table-wrap{border:1px solid #1b5378!important;border-radius:15px!important;background:#071522!important;box-shadow:0 14px 30px rgba(0,0,0,.16);max-height:620px;overflow:auto!important}
.sk-table{font-size:13px!important}.sk-table thead th{position:sticky;top:0;z-index:2;background:#0d2942!important;color:#b9d7eb!important;letter-spacing:.045em}.sk-table td{padding:12px 14px!important}.sk-table tbody tr:nth-child(even) td{background:rgba(12,32,53,.28)}
.sk-table tr:hover td{background:#0d2942!important}
/* atleta/foto e cards de conteúdo */
[data-testid="stImage"] img{border-radius:16px!important;border:1px solid #1c638e!important;box-shadow:0 15px 35px rgba(0,0,0,.28)}
[data-testid="stDownloadButton"] button{min-height:48px!important;border-radius:11px!important;background:linear-gradient(135deg,#0b2942,#0a2136)!important;border:1px solid #168ac4!important;color:#eefaff!important;font-weight:850!important;box-shadow:0 0 18px rgba(0,174,255,.08)}
[data-testid="stDownloadButton"] button:hover{border-color:#20e6ff!important;box-shadow:0 0 22px rgba(0,217,255,.18)!important;transform:translateY(-1px)}
[data-testid="stSelectbox"] div[data-baseweb="select"]>div{border-color:#285b7c!important}
@media(max-width:900px){.kpi-grid{grid-template-columns:repeat(2,1fr)!important}.section{font-size:19px!important}.table-wrap{max-height:520px}}
</style>
""",unsafe_allow_html=True)

st.markdown("""
<style>
/* V5.0 — override final dos controles do Streamlit */

/* Arquivos já carregados: card escuro + texto claro */
section[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
[data-testid="stSidebar"] section[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
.stFileUploader [data-testid="stFileUploaderFile"]{
    background:#0b2034 !important;
    border:1px solid #245071 !important;
    border-radius:9px !important;
}
section[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] > div,
section[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] > div > div,
.stFileUploader [data-testid="stFileUploaderFile"] > div,
.stFileUploader [data-testid="stFileUploaderFile"] > div > div{
    background:transparent !important;
}
section[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] *,
.stFileUploader [data-testid="stFileUploaderFile"] *{
    color:#eef8ff !important;
    -webkit-text-fill-color:#eef8ff !important;
    opacity:1 !important;
}
section[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] svg,
.stFileUploader [data-testid="stFileUploaderFile"] svg{
    color:#8fd3ff !important;
    fill:#8fd3ff !important;
}
section[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button,
.stFileUploader [data-testid="stFileUploaderFile"] button{
    background:#102c47 !important;
    border-color:#32698f !important;
}

/* Select fechado — sempre dark */
.stSelectbox div[data-baseweb="select"],
[data-testid="stSelectbox"] div[data-baseweb="select"]{
    background:#0b2034 !important;
}
.stSelectbox div[data-baseweb="select"] > div,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div{
    background-color:#0b2034 !important;
    background:#0b2034 !important;
    border-color:#245071 !important;
    color:#eef8ff !important;
}
.stSelectbox div[data-baseweb="select"] > div *,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div *,
div[data-baseweb="select"] > div *{
    color:#eef8ff !important;
    -webkit-text-fill-color:#eef8ff !important;
}

/* Label "Dificuldade para acompanhar" */
.stSelectbox label,
.stSelectbox label *,
[data-testid="stSelectbox"] label,
[data-testid="stSelectbox"] label *{
    color:#bcd9ee !important;
    -webkit-text-fill-color:#bcd9ee !important;
    opacity:1 !important;
}

/* Select aberto — menu e opções dark */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[role="listbox"],
div[role="listbox"]{
    background:#081827 !important;
    border-color:#245071 !important;
}
div[role="option"], div[role="option"] *,
li[role="option"], li[role="option"] *{
    background:#081827 !important;
    color:#eef8ff !important;
    -webkit-text-fill-color:#eef8ff !important;
}
div[role="option"]:hover,
div[role="option"][aria-selected="true"],
li[role="option"]:hover,
li[role="option"][aria-selected="true"]{
    background:#123a5a !important;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* V5.2 — evolução da dificuldade: caixa fechada e aberta 100% dark */
div[data-testid="stSelectbox"] div[data-baseweb="select"],
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-testid="stSelectbox"] div[role="combobox"],
div[data-testid="stSelectbox"] [role="combobox"],
div[data-testid="stSelectbox"] input {
    background:#0a2034 !important;
    background-color:#0a2034 !important;
    color:#f1f8ff !important;
    -webkit-text-fill-color:#f1f8ff !important;
    border-color:#245071 !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] *,
div[data-testid="stSelectbox"] div[role="combobox"] *,
div[data-testid="stSelectbox"] [role="combobox"] * {
    color:#f1f8ff !important;
    -webkit-text-fill-color:#f1f8ff !important;
}
div[data-testid="stSelectbox"] label,
div[data-testid="stSelectbox"] label *,
div[data-testid="stSelectbox"] label p {
    color:#bcd9ee !important;
    -webkit-text-fill-color:#bcd9ee !important;
    opacity:1 !important;
}

/* Menu aberto do BaseWeb */
body > div[data-baseweb="popover"],
body > div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] [role="listbox"],
div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] {
    background:#081827 !important;
    background-color:#081827 !important;
    border-color:#245071 !important;
}
div[data-baseweb="popover"] [role="option"],
div[data-baseweb="popover"] [role="option"] *,
div[role="listbox"] [role="option"],
div[role="listbox"] [role="option"] * {
    background:#081827 !important;
    background-color:#081827 !important;
    color:#eef8ff !important;
    -webkit-text-fill-color:#eef8ff !important;
}
div[data-baseweb="popover"] [role="option"]:hover,
div[data-baseweb="popover"] [role="option"][aria-selected="true"],
div[role="listbox"] [role="option"]:hover,
div[role="listbox"] [role="option"][aria-selected="true"] {
    background:#123a5a !important;
    background-color:#123a5a !important;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* V5.3 — UPLOADER DEFINITIVO DARK */

/* container principal do arquivo carregado */
[data-testid="stFileUploaderFile"] {
    background: #0a1f33 !important;
    background-color: #0a1f33 !important;
    border: 1px solid #245071 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}

/* wrappers internos que o Streamlit pinta de branco */
[data-testid="stFileUploaderFile"] > div,
[data-testid="stFileUploaderFile"] > div > div,
[data-testid="stFileUploaderFile"] div[data-testid],
[data-testid="stFileUploaderFile"] div[class],
[data-testid="stFileUploaderFile"] section {
    background: #0a1f33 !important;
    background-color: #0a1f33 !important;
}

/* nome e tamanho */
[data-testid="stFileUploaderFile"] p,
[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFile"] small,
[data-testid="stFileUploaderFile"] label {
    color: #eaf7ff !important;
    -webkit-text-fill-color: #eaf7ff !important;
    opacity: 1 !important;
}

/* ícone do tipo de arquivo */
[data-testid="stFileUploaderFile"] svg {
    color: #9bd9ff !important;
    fill: #9bd9ff !important;
}

/* botão X */
[data-testid="stFileUploaderFile"] button,
[data-testid="stFileUploaderFile"] button div,
[data-testid="stFileUploaderFile"] button span {
    background: #0f2b45 !important;
    background-color: #0f2b45 !important;
    color: #eaf7ff !important;
    -webkit-text-fill-color: #eaf7ff !important;
    border-color: #32698f !important;
}

/* área externa dos uploaders na sidebar */
[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
    background: #0b2034 !important;
    background-color: #0b2034 !important;
    border-color: #245071 !important;
}

/* Select de evolução fechado */
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stSelectbox"] [role="combobox"] {
    background: #0a2034 !important;
    background-color: #0a2034 !important;
    border-color: #245071 !important;
    color: #eef8ff !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] *,
[data-testid="stSelectbox"] [role="combobox"] * {
    color: #eef8ff !important;
    -webkit-text-fill-color: #eef8ff !important;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* V5.5 — cards dos arquivos carregados realmente escuros */

/* Linha/card do arquivo */
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] > div,
[data-testid="stFileUploaderFile"] > div > div,
[data-testid="stFileUploaderFile"] > div > div > div,
[data-testid="stFileUploaderFile"] div {
    background-color:#0b2034 !important;
    background:#0b2034 !important;
}

/* O próprio card */
[data-testid="stFileUploaderFile"] {
    border:1px solid #285678 !important;
    border-radius:9px !important;
    box-shadow:none !important;
}

/* Texto do nome e tamanho */
[data-testid="stFileUploaderFile"] p,
[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFile"] small,
[data-testid="stFileUploaderFile"] div {
    color:#e8f5ff !important;
    -webkit-text-fill-color:#e8f5ff !important;
    opacity:1 !important;
}

/* Ícone à esquerda */
[data-testid="stFileUploaderFile"] svg {
    color:#9bd8ff !important;
    fill:#9bd8ff !important;
}

/* Botão X */
[data-testid="stFileUploaderFile"] button,
[data-testid="stFileUploaderFile"] button *,
[data-testid="stFileUploaderFile"] [data-testid="stBaseButton-minimal"],
[data-testid="stFileUploaderFile"] [data-testid="stBaseButton-minimal"] * {
    background:#102c47 !important;
    background-color:#102c47 !important;
    color:#eaf7ff !important;
    -webkit-text-fill-color:#eaf7ff !important;
    border-color:#376c91 !important;
}

/* Alguns releases do Streamlit usam estes wrappers para a lista */
[data-testid="stFileUploader"] ul,
[data-testid="stFileUploader"] li,
[data-testid="stFileUploader"] ul > li,
[data-testid="stFileUploader"] li > div,
[data-testid="stFileUploader"] li > div > div {
    background:#0b2034 !important;
    background-color:#0b2034 !important;
    color:#e8f5ff !important;
}

/* Garante que nenhum pseudo-elemento recoloque branco */
[data-testid="stFileUploaderFile"]::before,
[data-testid="stFileUploaderFile"]::after {
    background:#0b2034 !important;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* V5.7 — uploader: cobre também FileData e a linha pai do arquivo */
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFileData"],
[data-testid="stFileUploaderFileData"] > div,
[data-testid="stFileUploaderFileData"] ~ div,
[data-testid="stFileUploaderFile"] > div,
[data-testid="stFileUploaderFile"] > div > div,
[data-testid="stFileUploaderFile"] > div > div > div {
    background: #0b2034 !important;
    background-color: #0b2034 !important;
    color: #eaf7ff !important;
    -webkit-text-fill-color: #eaf7ff !important;
}

/* O wrapper imediatamente acima do bloco de dados é o retângulo visível em algumas versões */
[data-testid="stFileUploader"] div:has(> [data-testid="stFileUploaderFileData"]),
[data-testid="stFileUploader"] div:has(> div > [data-testid="stFileUploaderFileData"]),
[data-testid="stFileUploader"] div:has([data-testid="stFileUploaderFileData"]) {
    background-color: #0b2034 !important;
}

/* textos */
[data-testid="stFileUploaderFileData"] *,
[data-testid="stFileUploaderFile"] p,
[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFile"] small {
    color:#eaf7ff !important;
    -webkit-text-fill-color:#eaf7ff !important;
}

/* botão remover e ícones */
[data-testid="stFileUploaderFile"] button,
[data-testid="stFileUploaderFile"] button * {
    background:#102c47 !important;
    background-color:#102c47 !important;
    color:#eaf7ff !important;
}
[data-testid="stFileUploaderFile"] svg {
    color:#9bd8ff !important;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* V5.8 — fundo nativo branco mantido; textos escuros para legibilidade */
[data-testid="stFileUploaderFile"] p,
[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFile"] small,
[data-testid="stFileUploaderFileData"],
[data-testid="stFileUploaderFileData"] p,
[data-testid="stFileUploaderFileData"] span,
[data-testid="stFileUploaderFileData"] small,
[data-testid="stFileUploaderFileData"] div {
    color:#12324b !important;
    -webkit-text-fill-color:#12324b !important;
    opacity:1 !important;
}

/* nome do arquivo mais forte */
[data-testid="stFileUploaderFileData"] p:first-child,
[data-testid="stFileUploaderFile"] p:first-child {
    color:#0a2942 !important;
    -webkit-text-fill-color:#0a2942 !important;
    font-weight:700 !important;
}

/* botão X continua escuro e legível */
[data-testid="stFileUploaderFile"] button,
[data-testid="stFileUploaderFile"] button * {
    color:#12324b !important;
    -webkit-text-fill-color:#12324b !important;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* V5.9 — texto dos arquivos carregados: seletor abrangente */
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] *,
[data-testid="stFileUploaderFileData"],
[data-testid="stFileUploaderFileData"] * {
    color:#0b2942 !important;
    -webkit-text-fill-color:#0b2942 !important;
    opacity:1 !important;
}

/* Streamlit atual pode usar elementos com title para nome/tamanho */
[data-testid="stFileUploader"] [title],
[data-testid="stFileUploader"] [title] *,
[data-testid="stFileUploader"] li *,
[data-testid="stFileUploader"] ul * {
    color:#0b2942 !important;
    -webkit-text-fill-color:#0b2942 !important;
}

/* mantém os ícones visíveis */
[data-testid="stFileUploader"] svg {
    color:#183c58 !important;
    fill:currentColor !important;
    -webkit-text-fill-color:initial !important;
}

/* botão remover */
[data-testid="stFileUploader"] button,
[data-testid="stFileUploader"] button * {
    color:#0b2942 !important;
    -webkit-text-fill-color:#0b2942 !important;
}
</style>
""", unsafe_allow_html=True)

# V3.0 — proteção responsiva para gráficos e controles no celular.
st.markdown("""
<style>
@media (max-width: 768px) {
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: .75rem !important; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-width: 100% !important; width: 100% !important; flex: 1 1 100% !important; }
  [data-testid="stPlotlyChart"], [data-testid="stPlotlyChart"] > div { width: 100% !important; max-width: 100% !important; overflow: visible !important; }
  .js-plotly-plot, .plot-container, .svg-container { width: 100% !important; max-width: 100% !important; }
  .main .block-container { padding-left: .7rem !important; padding-right: .7rem !important; }
}
</style>
""", unsafe_allow_html=True)
