# V4.09 - Times UI refinada: badges neon, icones SVG e formularios dark
from datetime import date
import html
import streamlit as st
from streamlit_elements import elements, mui
from auth_utils import require_login, get_supabase

st.set_page_config(initial_sidebar_state="collapsed", page_title="Times • Seleção Brasileira de Skateboarding", page_icon="🛹", layout="wide")
user, profile = require_login()
sb = get_supabase()
is_admin = True  # V4.42 temporário

ROLE = {
    "admin":"Administrador", "skatista":"Atleta", "tecnico":"Técnico",
    "presidente":"Presidente", "vice_presidente":"Vice-presidente",
    "chefe_equipe":"Chefe de equipe", "comissao_tecnica":"Comissão técnica",
    "familiar":"Familiar"
}
STAFF = {"admin","tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica"}
ROLE_ORDER = {"presidente":0,"vice_presidente":1,"chefe_equipe":2,"tecnico":3,"comissao_tecnica":4,"admin":5}

def safe(v): return html.escape(str(v or "—"))
def age(v):
    try:
        b=date.fromisoformat(v); t=date.today()
        return t.year-b.year-((t.month,t.day)<(b.month,b.day))
    except Exception: return None

def initials(name):
    p=[x for x in str(name or "").split() if x]
    return "".join(x[0].upper() for x in p[:2]) or "BR"

st.markdown(r'''<style>
:root{--bg:#020b14;--panel:#061727;--panel2:#081b2d;--border:#163b59;--blue:#087cff;--cyan:#20e6ff;--text:#f5f8fc;--muted:#8499ad;--green:#00e4a4;--purple:#b44cff}
[data-testid="stSidebar"],button[aria-label="Open sidebar"],button[aria-label="Close sidebar"]{display:none!important}
[data-testid="stHeader"],#MainMenu,footer{display:none!important}
html,body,[data-testid="stAppViewContainer"],.stApp{background:
radial-gradient(circle at 76% 0%,rgba(0,126,255,.16),transparent 32%),
radial-gradient(circle at 8% 45%,rgba(0,217,255,.055),transparent 28%),
linear-gradient(180deg,#020b14 0%,#03111e 58%,#020b14 100%)!important;
background-attachment:fixed!important}
.block-container{width:100%!important;max-width:1480px!important;padding:0 26px 64px!important;margin:0 auto!important;font-family:"Segoe UI Variable",Inter,Manrope,Arial,sans-serif!important}
.sp-nav{height:72px;margin:0 -26px 22px;padding:0 34px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(32,230,255,.14);background:linear-gradient(90deg,#03101c 0%,#061727 55%,#03101c 100%);box-shadow:0 10px 40px #0008;position:relative;z-index:2}
.sp-brand{display:flex;align-items:center;gap:12px}.sp-mark{width:36px;height:36px;border-radius:11px;display:grid;place-items:center;border:1px solid #00d9ff66;background:#06243a;box-shadow:0 0 20px #00d9ff26;color:#20e6ff;font-size:17px}.sp-brand-top{font:800 11px/1.1 "Segoe UI Variable",Inter,sans-serif;letter-spacing:1.5px;color:#fff}.sp-brand-sub{font:700 8px/1.2 "Segoe UI Variable",Inter,sans-serif;letter-spacing:1.4px;color:#20e6ff;margin-top:4px}.sp-menu{display:flex;gap:28px;font:700 11px "Segoe UI Variable",Inter,sans-serif;color:#8499ad}.sp-menu .on{color:#fff;position:relative}.sp-menu .on:after{content:"";position:absolute;left:0;right:0;bottom:-25px;height:2px;background:#20e6ff;box-shadow:0 0 12px #20e6ff}
.page-kicker{font:800 11px "Segoe UI Variable",Inter,sans-serif;letter-spacing:2px;color:#20e6ff;text-transform:uppercase;margin-top:10px}.page-title{font:900 clamp(30px,3vw,48px)/1 "Segoe UI Variable",Inter,sans-serif;color:#f5f8fc;letter-spacing:-1.4px;margin:8px 0}.page-desc{font:500 13px/1.6 "Segoe UI Variable",Inter,sans-serif;color:#8499ad;max-width:760px;margin-bottom:24px}.summary-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-bottom:28px}
.summary{min-height:112px;padding:18px 22px;border-radius:18px;background:linear-gradient(145deg,#071a2b,#04111d);box-shadow:0 16px 38px #0007,inset 0 1px #ffffff0a;display:flex;align-items:center;gap:18px;position:relative;overflow:hidden}
.summary:after{content:"";position:absolute;width:150px;height:150px;border-radius:50%;right:-55px;top:-75px;filter:blur(4px);opacity:.15}
.summary-icon{width:58px;height:58px;min-width:58px;border-radius:15px;display:grid;place-items:center;font-size:28px;border:1px solid currentColor;background:#061a2a;box-shadow:0 0 24px currentColor}
.summary-copy{display:flex;flex-direction:column;justify-content:center}.summary b{font:950 34px/1 "Segoe UI Variable",Inter,sans-serif;color:#fff;letter-spacing:-1px}.summary span{display:block;margin-top:8px;color:#c4d1df;font:850 10px/1.1 "Segoe UI Variable",Inter,sans-serif;letter-spacing:1.25px;text-transform:uppercase}
.summary.cyan{color:#20e6ff;border:1px solid #00d9ff88;box-shadow:0 0 28px #00d9ff13,0 16px 38px #0007}.summary.cyan:after{background:#00d9ff}.summary.blue{color:#29a8ff;border:1px solid #087cff88;box-shadow:0 0 28px #087cff13,0 16px 38px #0007}.summary.blue:after{background:#087cff}.summary.purple{color:#b44cff;border:1px solid #b44cff88;box-shadow:0 0 28px #b44cff13,0 16px 38px #0007}.summary.purple:after{background:#b44cff}
[data-baseweb="tab-list"]{display:grid!important;grid-template-columns:repeat(3,1fr)!important;gap:0!important;background:linear-gradient(145deg,#061827,#04111d)!important;border:1px solid #175277!important;border-radius:16px!important;padding:0!important;margin:4px 0 24px!important;overflow:hidden!important;box-shadow:0 14px 34px #0005!important}[data-baseweb="tab"]{width:100%!important;height:64px!important;border-radius:0!important;border-right:1px solid #175277!important;color:#a9bfd2!important;font-family:"Segoe UI Variable",Inter,sans-serif!important;font-weight:900!important;font-size:13px!important;letter-spacing:.35px!important;padding:0 18px!important;justify-content:center!important}[data-baseweb="tab"]:last-child{border-right:none!important}[data-baseweb="tab"][aria-selected="true"]{color:#fff!important;background:radial-gradient(circle at 75% 50%,#087cff55,transparent 48%),linear-gradient(135deg,#06233b,#087cff22)!important;border:1px solid #20e6ff!important;box-shadow:inset 0 0 28px #087cff35,0 0 22px #00d9ff45!important;text-shadow:0 0 12px #00d9ff55!important}.stTabs [data-baseweb="tab-highlight"]{display:none!important}
.section-head{display:flex;justify-content:space-between;align-items:end;margin:22px 0 12px}.section-head h3{margin:0;color:#f5f8fc;font:900 22px "Segoe UI Variable",Inter,sans-serif}.section-head p{margin:5px 0 0;color:#a8bacb;font-size:12px}.team-banner{min-height:96px;border:1px solid #175277;border-radius:18px;padding:17px 20px;display:flex;align-items:center;gap:16px;background:radial-gradient(circle at 82% 35%,#087cff2e,transparent 34%),linear-gradient(115deg,#071c30,#04111d);box-shadow:0 14px 36px #0007,inset 0 1px #ffffff08;margin:8px 0 20px}.team-icon{width:60px;height:60px;min-width:60px;border-radius:16px;display:grid;place-items:center;background:#08243a;border:1px solid #20e6ff66;color:#20e6ff;font-size:25px;box-shadow:0 0 24px #00d9ff18}.team-name{font:900 24px "Segoe UI Variable",Inter,sans-serif;color:#fff;letter-spacing:-.35px}.team-meta{font:700 12px "Segoe UI Variable",Inter,sans-serif;color:#8499ad;margin-top:6px;letter-spacing:.4px}.member-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin-bottom:10px;width:100%;max-width:none}.member-card{position:relative;min-height:340px;overflow:hidden;border-radius:20px;border:1px solid #1a496a;background:radial-gradient(circle at 85% 10%,#087cff1e,transparent 34%),linear-gradient(160deg,#081b2d,#04111d);box-shadow:0 16px 38px #0007,inset 0 1px #ffffff08;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease}.member-card:hover{transform:translateY(-3px);border-color:#20e6ff88;box-shadow:0 18px 42px #0008,0 0 24px #00d9ff12}.member-photo{width:100%;height:225px;object-fit:cover;object-position:center 22%;display:block;background:#071827}.member-ph{height:225px;display:grid;place-items:center;background:radial-gradient(circle at 50% 30%,#0c4164,#071827 68%);color:#20e6ff;font:900 48px "Segoe UI Variable",Inter,sans-serif;text-shadow:0 0 20px #00d9ff55}.member-body{padding:17px 18px 19px}.member-name{font:900 18px "Segoe UI Variable",Inter,sans-serif;color:#f5f8fc;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:-.2px}.role{display:inline-block;margin-top:5px;padding:3px 8px;border-radius:999px;background:#087cff16;border:1px solid #087cff55;color:#29a8ff;font:800 8px "Segoe UI Variable",Inter,sans-serif;text-transform:uppercase;letter-spacing:.7px}.role.staff{color:#20e6ff;border-color:#20e6ff55;background:#20e6ff12}.member-meta{margin-top:11px;color:#c4d1df;font:650 12px/1.65 "Segoe UI Variable",Inter,sans-serif}.empty{border:1px dashed #163b59;border-radius:16px;padding:28px;text-align:center;color:#8499ad;background:#06172788}.stButton>button{border-radius:10px!important;border:1px solid #1b668d!important;background:#071d30!important;color:#dff8ff!important;font-weight:800!important;font-size:11px!important;min-height:36px!important}.stButton>button:hover{border-color:#20e6ff!important;color:#fff!important;box-shadow:0 0 18px #00d9ff20!important}.stExpander{border:1px solid #163b59!important;border-radius:14px!important;background:#061727!important}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary p,[data-testid="stExpander"] svg{color:#d8e7f4!important;fill:#d8e7f4!important;font-family:"Segoe UI Variable",Inter,sans-serif!important;font-weight:750!important}
[data-testid="stExpander"] summary:hover,[data-testid="stExpander"] summary:hover p{color:#20e6ff!important}
[data-testid="stExpanderDetails"] label,[data-testid="stExpanderDetails"] p,[data-testid="stExpanderDetails"] span{color:#d8e7f4!important}
[data-testid="stWidgetLabel"] p{color:#d8e7f4!important;font-weight:700!important}
.stMarkdown p,.stCaptionContainer{color:#c4d1df!important}
@media(max-width:1050px){.member-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:760px){[data-baseweb="tab"]{height:56px!important;font-size:10px!important;padding:0 6px!important}.sp-menu{display:none}.member-grid{grid-template-columns:repeat(2,1fr)}.summary-grid{grid-template-columns:1fr}.block-container{padding:0 14px 40px!important}.sp-nav{margin:0 -14px 18px;padding:0 18px}.team-banner{padding:17px}.team-icon{width:58px;height:58px;min-width:58px}.team-name{font-size:19px}}@media(max-width:470px){.member-grid{grid-template-columns:1fr}}

/* Dialog / perfil no mesmo tema do portal */
[data-testid="stDialog"]>div, [role="dialog"]{background:linear-gradient(145deg,#071a2b,#03101c)!important;color:#f5f8fc!important;border:1px solid #1a5a80!important;border-radius:20px!important;box-shadow:0 30px 90px #000c,0 0 35px #00d9ff12!important}
[data-testid="stDialog"] h1,[data-testid="stDialog"] h2,[data-testid="stDialog"] h3,[data-testid="stDialog"] p,[data-testid="stDialog"] label,[role="dialog"] h1,[role="dialog"] h2,[role="dialog"] h3,[role="dialog"] p,[role="dialog"] label{color:#f5f8fc!important}
[data-testid="stDialog"] [data-testid="stMetricLabel"],[role="dialog"] [data-testid="stMetricLabel"]{color:#9fb4c7!important}
[data-testid="stDialog"] [data-testid="stMetricValue"],[role="dialog"] [data-testid="stMetricValue"]{color:#fff!important}
[data-testid="stDialog"] button,[role="dialog"] button{color:#dff8ff!important}
[data-testid="stDialog"] img,[role="dialog"] img{border-radius:16px!important;border:1px solid #1a5a80!important}
/* Botões de ação com alinhamento uniforme */
[data-testid="stHorizontalBlock"]{align-items:stretch!important}
[data-testid="column"] .stButton{width:100%!important}
[data-testid="column"] .stButton>button{width:100%!important;margin:0!important}
/* Formulários administrativos no mesmo tema dark/neon */
[data-testid="stForm"]{background:linear-gradient(145deg,#061827,#04111d)!important;border:1px solid #175277!important;border-radius:16px!important;padding:18px!important}
[data-testid="stTextInput"] input{background:#081b2d!important;color:#f5f8fc!important;border:1px solid #1b668d!important;border-radius:10px!important;-webkit-text-fill-color:#f5f8fc!important}
[data-testid="stTextInput"] input:focus{border-color:#20e6ff!important;box-shadow:0 0 0 1px #20e6ff,0 0 18px #00d9ff25!important}
[data-baseweb="select"]>div{background:#081b2d!important;color:#f5f8fc!important;border-color:#1b668d!important}
[data-baseweb="select"] span,[data-baseweb="select"] svg{color:#eaf7ff!important;fill:#eaf7ff!important}
[data-baseweb="popover"] ul,[role="listbox"]{background:#081b2d!important;color:#f5f8fc!important}
[role="option"]{color:#eaf7ff!important;background:#081b2d!important}
[role="option"]:hover{background:#0d2b45!important}
[data-testid="stFormSubmitButton"] button{background:linear-gradient(135deg,#087cff,#00bfe8)!important;color:#fff!important;border:1px solid #20e6ff!important;box-shadow:0 0 20px #00d9ff25!important;padding:0 22px!important}
/* badges neon separados nos seletores Street / Park / Comissão */
[data-baseweb="tab"]{position:relative!important;gap:12px!important}
[data-baseweb="tab"]:after{display:inline-grid!important;place-items:center!important;min-width:27px!important;height:24px!important;padding:0 7px!important;border-radius:8px!important;background:#0b3555!important;border:1px solid #1d6c99!important;color:#bfeaff!important;font:900 11px "Segoe UI Variable",Inter,sans-serif!important;box-shadow:inset 0 0 12px #087cff22!important}
[data-baseweb="tab"]:nth-child(1):after{content:"STREET_COUNT"}
[data-baseweb="tab"]:nth-child(2):after{content:"PARK_COUNT"}
[data-baseweb="tab"]:nth-child(3):after{content:"COMMISSION_COUNT"}
[data-baseweb="tab"][aria-selected="true"]:after{background:#087cff!important;border-color:#29a8ff!important;color:#fff!important;box-shadow:0 0 16px #087cff88!important}

/* V4.23 unified redesigned-page frame */
[data-testid="stMainBlockContainer"]{
  border-left:8px solid #f5f8fc!important;
  border-right:8px solid #f5f8fc!important;
  box-sizing:border-box!important;
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


/* V4.26 — correção estrutural real do topo e da moldura */
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"]{
  display:none!important;
  height:0!important;
  min-height:0!important;
}
html,body,.stApp,[data-testid="stAppViewContainer"],
[data-testid="stMain"],section.main{
  margin:0!important;
  padding-top:0!important;
}
[data-testid="stMainBlockContainer"]{
  width:100%!important;
  max-width:1480px!important;
  margin:0 auto!important;
  padding-top:0!important;
  border-top:0!important;
  border-bottom:0!important;
  border-left:8px solid #f5f8fc!important;
  border-right:8px solid #f5f8fc!important;
}
[data-testid="stMainBlockContainer"]::before,
[data-testid="stMainBlockContainer"]::after{
  content:none!important;
  display:none!important;
  height:0!important;
  background:transparent!important;
}
.block-container{
  margin-top:0!important;
  padding-top:0!important;
}
[data-testid="stMainBlockContainer"] > div:first-child,
[data-testid="stVerticalBlock"] > div:first-child,
[data-testid="stElementContainer"]:first-child{
  margin-top:0!important;
  padding-top:0!important;
}
[data-testid="stCustomComponentV1"],
[data-testid="stCustomComponentV1"] > div,
[data-testid="stCustomComponentV1"] iframe{
  margin:0!important;
  padding:0!important;
  border:0!important;
  outline:0!important;
  box-shadow:none!important;
  display:block!important;
  background:transparent!important;
}


/* V4.28 — navbar full bleed; conteúdo interno alinhado */
[data-testid="stMainBlockContainer"]{
  position:relative!important;
  padding-top:0!important;
  padding-left:18px!important;
  padding-right:18px!important;
  border-top:0!important;
  border-bottom:0!important;
}
[data-testid="stMainBlockContainer"]::before,
[data-testid="stMainBlockContainer"]::after{
  content:none!important;
  display:none!important;
}

/* Primeiro componente = navbar: ocupa até as bordas brancas */
[data-testid="stMainBlockContainer"] > div:first-child{
  margin-top:0!important;
}
[data-testid="stCustomComponentV1"]:first-of-type{
  width:calc(100% + 36px)!important;
  max-width:calc(100% + 36px)!important;
  margin-left:-18px!important;
  margin-right:-18px!important;
  margin-top:0!important;
  padding:0!important;
}
[data-testid="stCustomComponentV1"]:first-of-type > div,
[data-testid="stCustomComponentV1"]:first-of-type iframe{
  width:100%!important;
  max-width:100%!important;
  margin:0!important;
  padding:0!important;
  border:0!important;
  display:block!important;
}

/* nenhum separador branco horizontal ao redor da navbar */
[data-testid="stCustomComponentV1"]:first-of-type + div{
  border-top:0!important;
}

/* conteúdo volta ao alinhamento normal */
[data-testid="stMainBlockContainer"] .element-container{
  box-sizing:border-box!important;
}
</style>''', unsafe_allow_html=True)

# Navbar V4.29 visual preservado; links nativos fora de iframe.
nav_name = str((profile or {}).get("full_name") or getattr(user, "email", None) or "Usuário").strip()
nav_role = str((profile or {}).get("role") or "membro").replace("_", " ").title()
nav_photo = (profile or {}).get("photo_url")
from nav_v472 import render_top_nav
render_top_nav(nav_name=nav_name, nav_role=nav_role, nav_photo=nav_photo, active='Times', key="nav_pages_02_Times.py")

@st.dialog("Perfil do atleta", width="large")
def member_dialog(p):
    ag=age(p.get("birth_date")); loc=" / ".join(x for x in [p.get("city"),p.get("state")] if x) or "—"
    left,right=st.columns([1,1.35],gap="large")
    with left:
        if p.get("photo_url"):
            st.image(p["photo_url"],use_container_width=True)
        else:
            st.markdown(f'<div class="member-ph" style="border-radius:16px;height:300px">{safe(initials(p.get("full_name")))}</div>',unsafe_allow_html=True)
    with right:
        st.markdown(f"## {safe(p.get('full_name'))}")
        st.caption(ROLE.get(p.get("role"),"Membro").upper())
        st.markdown(f"**Idade:** {f'{ag} anos' if ag is not None else '—'}")
        st.markdown(f"**Modalidade:** {safe(p.get('modality') or '—')}")
        st.markdown(f"**Base:** {safe(p.get('stance') or '—')}")
        st.markdown(f"**Local:** {safe(loc)}")
    st.divider()
    a,b=st.columns(2,gap="medium")
    a.button("▣  Ver cartão",key=f"dlg_card_{p.get('id')}",use_container_width=True)
    b.button("♙  Ver perfil completo",key=f"dlg_profile_{p.get('id')}",use_container_width=True)


@st.dialog("Editar atleta", width="large")
def edit_athlete_dialog(p):
    if not is_admin:
        st.warning("Apenas administradores podem editar dados do atleta."); return
    st.caption("Atualize os dados esportivos e pessoais exibidos no portal.")
    with st.form(f"edit_athlete_{p.get('id')}"):
        c1,c2=st.columns(2)
        full_name=c1.text_input("Nome completo",value=p.get("full_name") or "")
        modality_opts=["Street","Park","Vert","Outro"]
        mv=p.get("modality") or "Street"
        modality=c2.selectbox("Modalidade",modality_opts,index=modality_opts.index(mv) if mv in modality_opts else 0)
        c3,c4=st.columns(2)
        stance_opts=["Regular","Goofy","Não informado"]
        sv=p.get("stance") or "Não informado"
        stance=c3.selectbox("Base",stance_opts,index=stance_opts.index(sv) if sv in stance_opts else 2)
        city=c4.text_input("Cidade",value=p.get("city") or "")
        c5,c6=st.columns(2)
        states=["","AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO","EXTERIOR"]
        statev=(p.get("state") or "").upper()
        state=c5.selectbox("Estado/UF",states,index=states.index(statev) if statev in states else 0)
        birth=c6.text_input("Nascimento",value=p.get("birth_date") or "",placeholder="AAAA-MM-DD")
        save=st.form_submit_button("Salvar alterações",use_container_width=True)
    if save:
        try:
            payload={"full_name":full_name.strip() or p.get("full_name") or "Sem nome","modality":modality,"stance":None if stance=="Não informado" else stance,"city":city.strip() or None,"state":state or None,"birth_date":birth.strip() or None}
            sb.table("profiles").update(payload).eq("id",p["id"]).execute()
            st.success("Atleta atualizado."); st.rerun()
        except Exception as exc:
            st.error(f"Não foi possível salvar: {exc}")

def fetch():
    teams=sb.table("teams").select("*").order("name").execute().data or []
    mem=sb.table("team_members").select("team_id,profile_id").execute().data or []
    prof=sb.table("profiles").select("id,full_name,email,role,status,modality,stance,photo_url,birth_date,city,state").eq("status","ativo").order("full_name").execute().data or []
    return teams,prof,mem

def person_card_html(p, staff=False):
    ag=age(p.get("birth_date")); loc=" / ".join(x for x in [p.get("city"),p.get("state")] if x) or "—"
    photo=p.get("photo_url")
    visual=f'<img class="member-photo" src="{safe(photo)}">' if photo else f'<div class="member-ph">{safe(initials(p.get("full_name")))}</div>'
    role=ROLE.get(p.get("role"),"Membro")
    meta=[]
    if p.get("role")=="skatista" and ag is not None: meta.append(f"{ag} anos")
    if p.get("modality"): meta.append(safe(p.get("modality")))
    if p.get("stance") and p.get("role")=="skatista": meta.append(f"Base {safe(p.get('stance'))}")
    if loc!="—": meta.append(safe(loc))
    return f'''<div class="member-card">{visual}<div class="member-body"><div class="member-name">{safe(p.get('full_name'))}</div><span class="role{' staff' if staff else ''}">{safe(role)}</span><div class="member-meta">{' • '.join(meta) if meta else 'Seleção Brasileira de Skateboarding'}</div></div></div>'''

def render_people(group, scope, staff=False):
    if not group:
        st.markdown('<div class="empty">Nenhum membro cadastrado nesta seção.</div>', unsafe_allow_html=True); return
    # Cards premium em linhas de três, com ações alinhadas logo abaixo.
    for start in range(0,len(group),3):
        row=group[start:start+3]
        st.markdown('<div class="member-grid">'+''.join(person_card_html(p,staff) for p in row)+'</div>', unsafe_allow_html=True)
        cols=st.columns(3,gap="medium")
        for i,p in enumerate(row):
            with cols[i]:
                if p.get("role")=="skatista":
                    a,b=st.columns(2,gap="small")
                    if a.button("Cartão",key=f"card_{scope}_{p['id']}",use_container_width=True): member_dialog(p)
                    if b.button("Editar",key=f"edit_{scope}_{p['id']}",use_container_width=True):
                        edit_athlete_dialog(p)
                else:
                    if st.button("Ver cartão",key=f"card_{scope}_{p['id']}",use_container_width=True): member_dialog(p)
        st.write("")

def render_team(team, profiles, memberships, scope):
    tid=team["id"]; byid={p["id"]:p for p in profiles}; ids=[m["profile_id"] for m in memberships if m["team_id"]==tid]
    people=[byid[x] for x in ids if x in byid]; athletes=[p for p in people if p.get("role")=="skatista"]
    st.markdown(f'''<div class="team-banner"><div class="team-icon">🛹</div><div><div class="team-name">{safe(team.get('name'))}</div><div class="team-meta">{safe(team.get('modality'))} • {len(athletes)} ATLETAS ATIVOS</div></div></div>''', unsafe_allow_html=True)
    st.markdown(f'<div class="section-head"><div><h3>Atletas</h3><p>{len(athletes)} integrantes neste time</p></div></div>', unsafe_allow_html=True)
    render_people(athletes,scope)
    if is_admin:
        with st.expander("⚙️ Gerenciar integrantes do time"):
            opts={f"{p.get('full_name') or p.get('email')} • {ROLE.get(p.get('role'),'Membro')}":p["id"] for p in profiles}
            defaults=[k for k,v in opts.items() if v in ids]
            sel=st.multiselect("Membros do time",list(opts),default=defaults,key=f"m_{tid}")
            if st.button("Salvar membros",key=f"s_{tid}"):
                new={opts[x] for x in sel}; old=set(ids)
                for pid in old-new: sb.table("team_members").delete().eq("team_id",tid).eq("profile_id",pid).execute()
                rows=[{"team_id":tid,"profile_id":pid} for pid in new-old]
                if rows: sb.table("team_members").insert(rows).execute()
                st.rerun()

try:
    teams,profiles,memberships=fetch()
except Exception as e:
    st.error(f"Não foi possível carregar os times: {e}"); st.stop()

street=[t for t in teams if str(t.get("modality") or "").lower()=="street"]
park=[t for t in teams if str(t.get("modality") or "").lower()=="park"]
commission=sorted([p for p in profiles if p.get("role") in STAFF], key=lambda p:(ROLE_ORDER.get(p.get("role"),99),str(p.get("full_name") or "")))
athletes=[p for p in profiles if p.get("role")=="skatista"]

st.markdown(f"""<style>
</style>""", unsafe_allow_html=True)

st.markdown('<div class="page-kicker">Seleção Brasileira</div><div class="page-title">Times & Comissão Técnica</div><div class="page-desc">Visualize a composição das equipes Street e Park e os profissionais que fazem parte da estrutura técnica da Seleção Brasileira de Skateboarding.</div>', unsafe_allow_html=True)
st.markdown(f'''<div class="summary-grid">
<div class="summary cyan"><div class="summary-icon"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg></div><div class="summary-copy"><b>{len(athletes)}</b><span>Atletas ativos</span></div></div>
<div class="summary blue"><div class="summary-icon"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v6c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 11v6c0 1.7 4 3 9 3s9-1.3 9-3v-6"/></svg></div><div class="summary-copy"><b>{len(street)+len(park)}</b><span>Times cadastrados</span></div></div>
<div class="summary purple"><div class="summary-icon"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-4-4h-1"/><circle cx="18" cy="7" r="3"/></svg></div><div class="summary-copy"><b>{len(commission)}</b><span>Comissão técnica</span></div></div>
</div>''', unsafe_allow_html=True)

if is_admin:
    with st.expander("＋ Criar novo time"):
        with st.form("newteam"):
            name=st.text_input("Nome do time"); mod=st.selectbox("Modalidade",["Street","Park","Vert","Misto"]); ok=st.form_submit_button("Criar time")
        if ok and name.strip(): sb.table("teams").insert({"name":name.strip(),"modality":mod}).execute(); st.rerun()

# Seletor principal — botões reais (sem contadores no rótulo)
if "times_section" not in st.session_state:
    st.session_state.times_section = "street"

st.markdown("""<style>
/* Seletor Street / Park / Comissão — premium neon */
div[data-testid="stHorizontalBlock"]:has(button[kind="secondary"]) {gap:12px!important;}
div[data-testid="column"] > div > div > div > div > .stButton > button {
  min-height:64px!important;border-radius:16px!important;
  background:linear-gradient(145deg,#061a2b,#071f34)!important;
  border:1px solid #155071!important;color:#d9e9f5!important;
  font:900 13px/1 "Segoe UI Variable",Inter,sans-serif!important;
  letter-spacing:.65px!important;text-transform:uppercase!important;
  box-shadow:inset 0 1px #ffffff08,0 10px 28px #0005!important;
  transition:.18s ease!important;
}
div[data-testid="column"] > div > div > div > div > .stButton > button:hover {
  color:#fff!important;border-color:#20e6ff!important;
  background:linear-gradient(135deg,#072844,#083a62)!important;
  box-shadow:0 0 0 1px #20e6ff44,0 0 26px #00d9ff35,inset 0 1px #ffffff14!important;
  transform:translateY(-1px)!important;
}
/* selected button marked via injected wrapper classes below */
.neon-selector-label{margin:18px 0 8px;color:#8499ad;font:800 10px "Segoe UI Variable",Inter,sans-serif;letter-spacing:1.2px;text-transform:uppercase}
</style>""", unsafe_allow_html=True)

c1,c2,c3=st.columns(3,gap="small")
with c1:
    if st.button("STREET", key="nav_times_street", icon=":material/skateboarding:", use_container_width=True):
        st.session_state.times_section="street"; st.rerun()
with c2:
    if st.button("PARK", key="nav_times_park", icon=":material/landscape:", use_container_width=True):
        st.session_state.times_section="park"; st.rerun()
with c3:
    if st.button("COMISSÃO TÉCNICA", key="nav_times_staff", icon=":material/groups:", use_container_width=True):
        st.session_state.times_section="staff"; st.rerun()

# Glow mais forte no item ativo, sem números/badges desnecessários.
active_index={"street":1,"park":2,"staff":3}[st.session_state.times_section]
st.markdown(f"""<style>
div[data-testid="stHorizontalBlock"] > div:nth-child({active_index}) .stButton > button {{
 color:#fff!important;border-color:#20e6ff!important;
 background:radial-gradient(circle at 82% 25%,#087cff66,transparent 42%),linear-gradient(135deg,#06335a,#075ea8)!important;
 box-shadow:0 0 0 1px #20e6ff55,0 0 30px #00d9ff55,inset 0 1px #ffffff20!important;
}}
</style>""",unsafe_allow_html=True)

if st.session_state.times_section=="street":
    if not street: st.markdown('<div class="empty">Nenhum time Street cadastrado.</div>',unsafe_allow_html=True)
    for i,t in enumerate(street): render_team(t,profiles,memberships,f"street_{i}")
elif st.session_state.times_section=="park":
    if not park: st.markdown('<div class="empty">Nenhum time Park cadastrado.</div>',unsafe_allow_html=True)
    for i,t in enumerate(park): render_team(t,profiles,memberships,f"park_{i}")
else:
    st.markdown(f'''<div class="team-banner"><div class="team-icon">✦</div><div><div class="team-name">Comissão Técnica</div><div class="team-meta">PRESIDÊNCIA • CHEFIA DE EQUIPE • TÉCNICOS • STAFF</div></div></div><div class="section-head"><div><h3>Equipe técnica</h3><p>{len(commission)} profissionais ativos</p></div></div>''',unsafe_allow_html=True)
    render_people(commission,"commission",staff=True)
