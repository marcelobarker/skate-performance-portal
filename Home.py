
import streamlit as st
from auth_utils import sign_in, sign_up, sign_out, current_user, current_profile, load_profile

from ui_theme import apply_ui_theme

st.set_page_config(page_title="Skate Performance • Portal", page_icon="🛹", layout="wide")
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
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"],[data-baseweb="calendar"]{background:#081827!important;color:#eef8ff!important;}
[data-baseweb="menu"] li,[role="option"],[data-baseweb="calendar"] button{background:#081827!important;color:#eef8ff!important;}
[data-baseweb="menu"] li:hover,[role="option"]:hover{background:#12304b!important;}
</style>""", unsafe_allow_html=True)

st.markdown("""
<style>
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}
[data-testid="stSidebar"]{background:#081827!important}
[data-testid="stSidebar"] *{color:#d9eafa!important}
[data-testid="stHeader"],header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important}
.block-container{max-width:1400px;padding-top:1.2rem!important}
.hero{background:#0b1d31;border:1px solid #173b5a;border-radius:18px;padding:24px 28px;margin-bottom:22px}
.brand{font-size:31px;font-weight:900;font-style:italic;letter-spacing:-1px}
.brand .blue{color:#1398ff}.brand .time{font-size:15px;font-style:normal;margin-left:8px}
.sub{color:#6bc1f7;font-size:11px;letter-spacing:.7px}
.card{background:#0b1d31;border:1px solid #173b5a;border-radius:16px;padding:20px;height:155px}
.card h3{margin:0 0 8px;color:#f5f8ff}.muted{color:#9bb2c8}
[data-testid="stMetric"]{background:#0b1d31;border:1px solid #173b5a;padding:14px;border-radius:14px}
[data-testid="stMetricLabel"] p,[data-testid="stMetricValue"],[data-testid="stMetricValue"] div{color:#eef8ff!important}
[data-testid="stCaptionContainer"] p{color:#9bb2c8!important}
h1,h2,h3,p,label{color:#eef8ff}
/* Login/cadastro: remove os blocos brancos do tema padrão */
[data-testid="stTextInput"] input{background:#0b1d31!important;color:#eef8ff!important;border:1px solid #245274!important;border-radius:10px!important}
[data-testid="stTextInput"] input:focus{border-color:#1398ff!important;box-shadow:0 0 0 1px #1398ff!important}
[data-testid="stTextInput"] input::placeholder{color:#7893aa!important}
[data-testid="stTextInput"] button{background:transparent!important;color:#9fc7e5!important}
[data-testid="stFormSubmitButton"] button{background:#1398ff!important;color:#fff!important;border:1px solid #1398ff!important;border-radius:10px!important;font-weight:800!important}
[data-testid="stFormSubmitButton"] button:hover{background:#087fd8!important;border-color:#34aaff!important;color:#fff!important}
[data-testid="stForm"]{border-color:#173b5a!important;background:#081827!important}
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><div class="brand">SKATE<span class="blue">PERFORMANCE</span><span class="time">TIME BRASIL</span></div>
<div class="sub">ATHLETE MANAGEMENT • TRAINING INTELLIGENCE</div></div>""", unsafe_allow_html=True)

user = current_user()
profile = current_profile()
if user and not profile:
    profile = load_profile(user.id)

if not user:
    st.title("Bem-vindo ao Skate Performance")
    st.caption("Entre na sua conta ou solicite um novo cadastro.")
    login_tab, signup_tab = st.tabs(["ENTRAR", "CRIAR CONTA"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("E-mail")
            password = st.text_input("Senha", type="password")
            keep_connected = st.checkbox("Me manter conectado neste dispositivo")
            submit = st.form_submit_button("Entrar", use_container_width=True)
        if submit:
            try:
                sign_in(email, password, keep_connected=keep_connected)
                st.success("Login realizado.")
                st.rerun()
            except Exception:
                st.error("Não foi possível entrar. Confira e-mail, senha e se o e-mail já foi confirmado.")

    with signup_tab:
        with st.form("signup_form"):
            full_name = st.text_input("Nome completo")
            email2 = st.text_input("E-mail")
            password2 = st.text_input("Senha", type="password", help="Use pelo menos 6 caracteres.")
            role_label = st.selectbox("Quero me cadastrar como", ["Skatista", "Técnico", "Presidente", "Vice-presidente", "Chefe de Equipe", "Comissão Técnica", "Familiar"])
            linked_athlete_id=None
            if role_label == "Familiar":
                try:
                    avail=get_supabase().rpc("signup_athletes").execute().data or []
                except Exception: avail=[]
                if avail:
                    amap={a.get("full_name") or "Atleta":a["id"] for a in avail}
                    linked_athlete_id=amap[st.selectbox("Atleta que ficará vinculado a esta conta",list(amap))]
                else:
                    st.info("Ainda não há atleta ativo disponível para vínculo.")
            modality = st.selectbox("Modalidade principal", ["Street","Park","Vert","Outro"])
            accept = st.checkbox("Confirmo que os dados acima estão corretos.")
            create = st.form_submit_button("Solicitar cadastro", use_container_width=True)
        if create:
            if not full_name.strip() or not email2.strip() or len(password2) < 6 or not accept:
                st.error("Preencha os campos, use uma senha com pelo menos 6 caracteres e confirme os dados.")
            else:
                try:
                    role_map={"Skatista":"skatista","Técnico":"tecnico","Presidente":"presidente","Vice-presidente":"vice_presidente","Chefe de Equipe":"chefe_equipe","Comissão Técnica":"comissao_tecnica","Familiar":"familiar"}
                    role = role_map[role_label]
                    res = sign_up(full_name, email2, password2, role, modality, linked_athlete_id)
                    if getattr(res, "session", None):
                        st.session_state["sp_user"] = res.user
                        st.session_state["sp_session"] = res.session
                        load_profile(res.user.id)
                        st.success("Conta criada. Seu cadastro está aguardando aprovação.")
                        st.rerun()
                    else:
                        st.success("Conta criada. Confira seu e-mail para confirmar o cadastro; depois volte aqui para entrar.")
                except Exception as e:
                    st.error("Não foi possível criar a conta. O e-mail pode já estar cadastrado ou os dados precisam ser revisados.")
    st.stop()

status = (profile or {}).get("status","pendente")
role = (profile or {}).get("role","skatista")
name = (profile or {}).get("full_name", getattr(user,"email","Usuário"))

if role != "admin":
    st.markdown("""<style>[data-testid="stSidebarNav"] a[href*="01_Cadastros"],[data-testid="stSidebarNav"] a[href*="Cadastros"]{display:none!important}</style>""", unsafe_allow_html=True)
if role in ("skatista","familiar"):
    st.markdown("""<style>[data-testid="stSidebarNav"] a[href*="Analise_de_Treino"],[data-testid="stSidebarNav"] a[href*="03_Analise"]{display:none!important}</style>""", unsafe_allow_html=True)

top1, top2 = st.columns([5,1])
with top1:
    st.title(f"Olá, {name}")
    st.caption(f"Perfil: {role.upper()} • Status: {status.upper()}")
with top2:
    if st.button("Sair", use_container_width=True):
        sign_out(); st.rerun()

if status == "bloqueado":
    st.error("⛔ Seu acesso está bloqueado. Procure o administrador.")
    st.stop()
if status != "ativo":
    st.info("⏳ Seu cadastro foi recebido e está aguardando aprovação do administrador.")
    st.write("Assim que for aprovado, as áreas de equipe e análise serão liberadas.")
    st.stop()

import base64
from pathlib import Path
from datetime import date
from auth_utils import get_supabase

hero_b64=base64.b64encode((Path(__file__).parent/'hero_skater.png').read_bytes()).decode()
st.markdown(f"""<style>
.sp-topbar{{height:56px;background:rgba(2,12,23,.96);border:1px solid rgba(30,130,200,.30);border-radius:10px;padding:0 16px;display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;box-shadow:0 8px 24px #0004}}.sp-logo{{font-weight:900;font-size:18px;letter-spacing:-.5px}}.sp-logo b{{color:#159bff}}.sp-user{{color:#9fb4c8;font-size:12px}}
.sp-hero{{min-height:245px;border:1px solid rgba(20,145,255,.45);border-radius:12px;padding:46px 34px 30px 39%;background:linear-gradient(90deg,rgba(1,10,20,.10) 0%,rgba(2,13,24,.42) 40%,rgba(2,13,24,.94) 100%),linear-gradient(0deg,rgba(2,10,20,.75),transparent 55%),url(data:image/png;base64,{hero_b64}) left center/48% 100% no-repeat,#071522;box-shadow:0 16px 45px #0007;margin:0 0 -22px;position:relative;overflow:hidden}}.sp-hero:after{{content:'';position:absolute;inset:auto 0 0;height:60px;background:linear-gradient(transparent,#03111e)}}.sp-hero h1{{position:relative;z-index:2;font-size:40px;line-height:1.1;margin:0 0 9px;color:#fff!important;text-shadow:0 0 18px #087cff35}}.sp-hero p{{position:relative;z-index:2;color:#d3dfeb!important;font-size:16px;max-width:650px;line-height:1.5}}
.sp-kpis{{position:relative;z-index:4}}.sp-kpi{{border-radius:10px;padding:18px;min-height:152px;border:1px solid #ffffff24;box-shadow:0 12px 30px #0005,inset 0 1px 0 #ffffff12;transition:.18s ease}}.sp-kpi:hover{{transform:translateY(-2px);filter:brightness(1.06)}}.sp-icon{{font-size:34px;filter:drop-shadow(0 0 6px rgba(0,200,255,.35))}}.sp-num{{font-size:44px;font-weight:900;line-height:1;margin:10px 0 2px;color:#fff}}.sp-name{{font-size:14px;font-weight:750;color:#fff}}.sp-hint{{font-size:11px;color:#e8f4ffcf;margin-top:13px}}.sp-blue{{background:linear-gradient(135deg,rgba(0,115,255,.88),rgba(0,65,170,.72))}}.sp-green{{background:linear-gradient(135deg,rgba(0,175,105,.80),rgba(0,85,65,.82))}}.sp-purple{{background:linear-gradient(135deg,rgba(145,35,225,.82),rgba(75,20,130,.82))}}.sp-orange{{background:linear-gradient(135deg,rgba(220,100,0,.85),rgba(105,45,0,.88))}}
.sp-section{{font-size:19px;font-weight:800;margin:25px 0 10px;color:#f5f8fc}}.sp-quick{{background:linear-gradient(145deg,rgba(11,32,52,.95),rgba(5,20,34,.95));border:1px solid rgba(45,130,190,.30);border-radius:10px;padding:18px;text-align:center;min-height:122px;box-shadow:0 8px 24px #0004;transition:.18s ease}}.sp-quick:hover{{transform:translateY(-2px);border-color:rgba(0,170,255,.65);background:#102c46}}.sp-quick-icon{{font-size:32px;filter:drop-shadow(0 0 6px rgba(0,200,255,.35))}}.sp-quick-title{{font-weight:800;margin-top:6px;color:#f5f8fc}}.sp-quick-sub{{font-size:11px;color:#8499ad;margin-top:3px}}
.sp-person{{background:#071827;border:1px solid rgba(42,102,145,.25);border-radius:9px;padding:10px;min-height:235px;box-shadow:0 8px 24px #0004;transition:.18s ease}}.sp-person:hover{{transform:translateY(-2px);border-color:#087eeb}}.sp-person-name{{font-weight:800;margin-top:7px;color:#f5f8fc}}.sp-person-role{{color:#29a8ff;font-size:12px;font-weight:700}}.sp-person-meta{{color:#9aaec1;font-size:12px;line-height:1.6}}.sp-panel{{background:linear-gradient(145deg,#081b2d,#061727);border:1px solid rgba(50,130,190,.25);border-radius:10px;padding:16px;box-shadow:0 8px 24px #0004;min-height:180px}}.sp-event{{display:flex;gap:12px;align-items:center;padding:10px 0;border-bottom:1px solid rgba(50,130,190,.18)}}.sp-event:last-child{{border:0}}.sp-date{{min-width:58px;text-align:center;background:#0a2945;border-radius:6px;padding:7px;color:#fff;font-weight:800}}.sp-event-name{{font-weight:700;color:#f5f8fc}}.sp-event-loc{{font-size:11px;color:#8499ad}}.sp-train{{background:#071929;border:1px solid rgba(45,100,145,.25);border-radius:8px;padding:12px 14px;min-height:86px}}.sp-train-date{{font-size:17px;font-weight:800}}.sp-train-name{{font-size:11px;color:#9aaec1;margin-top:7px}}
@media(max-width:768px){{.sp-topbar{{height:auto;min-height:52px}}.sp-hero{{padding:155px 18px 24px;background:linear-gradient(0deg,#071522 36%,rgba(4,16,29,.08) 100%),url(data:image/png;base64,{hero_b64}) center top/100% 170px no-repeat,#071522;min-height:300px;margin-bottom:12px}}.sp-hero h1{{font-size:29px}}.sp-kpi{{min-height:132px;padding:14px}}.sp-num{{font-size:36px}}}}
</style>""",unsafe_allow_html=True)

st.markdown(f"<div class='sp-topbar'><div class='sp-logo'>🛹 SKATE <b>PERFORMANCE</b></div><div class='sp-user'>{name} · {role.replace('_',' ').title()}</div></div>",unsafe_allow_html=True)
st.markdown(f"<div class='sp-hero'><h1>Bem-vindo, {name.split()[0]}!</h1><p>Acompanhe o desempenho da sua equipe, veja seus treinos, analise suas manobras e evolua junto com seus atletas.</p></div>",unsafe_allow_html=True)
try:
    sb=get_supabase(); visible_profiles=sb.table('profiles').select('id,full_name,role,status,photo_url,modality,stance,city,state,birth_date').execute().data or []; visible_teams=sb.table('teams').select('id,name').execute().data or []; visible_trainings=sb.table('training_sessions').select('id,athlete_id,training_date,title,created_at').order('training_date',desc=True).limit(6).execute().data or []
    try: visible_events=sb.table('events').select('*').gte('event_date',date.today().isoformat()).order('event_date').limit(4).execute().data or []
    except Exception: visible_events=[]
except Exception as exc:
    visible_profiles=[];visible_teams=[];visible_trainings=[];visible_events=[];st.warning(f'Não foi possível atualizar a Home: {exc}')
athletes=[x for x in visible_profiles if x.get('role')=='skatista' and x.get('status')=='ativo']; staff=[x for x in visible_profiles if x.get('role') in ('tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica') and x.get('status')=='ativo']
items=[('👥',len(athletes),'Atletas','sp-blue','Ver equipe →'),('♟',len(staff),'Equipe técnica','sp-green','Ver equipe →'),('🛹',len(visible_teams),'Times','sp-purple','Ver times →'),('▥',len(visible_trainings),'Treinos recentes','sp-orange','Ver histórico →')]
cols=st.columns(4,gap='small')
for col,(ico,num,label,klass,hint) in zip(cols,items): col.markdown(f"<div class='sp-kpi {klass}'><div class='sp-icon'>{ico}</div><div class='sp-num'>{num}</div><div class='sp-name'>{label}</div><div class='sp-hint'>{hint}</div></div>",unsafe_allow_html=True)

st.markdown("<div class='sp-section'>Acesso rápido</div>",unsafe_allow_html=True)
quick=[]
quick.append(('👥','Times','Veja sua equipe e os membros','pages/02_Times.py'))
quick.append(('▣','Calendário','Eventos, treinos e campeonatos','pages/06_Calendario.py'))
if role not in ('skatista','familiar'): quick.append(('▥','Nova Análise','Analisar um novo CSV','pages/03_Analise_de_Treino.py'))
else: quick.append(('▥','Meus Treinos','Histórico e relatórios','pages/04_Historico_de_Treinos.py'))
quick.append(('👤','Meu Perfil','Editar meus dados','pages/05_Meu_Perfil.py'))
qcols=st.columns(4,gap='small')
for i,(ico,title,sub,page) in enumerate(quick):
    with qcols[i]:
        st.markdown(f"<div class='sp-quick'><div class='sp-quick-icon'>{ico}</div><div class='sp-quick-title'>{title}</div><div class='sp-quick-sub'>{sub}</div></div>",unsafe_allow_html=True)
        if st.button(f'Abrir {title} →',key=f'quick_{i}',use_container_width=True): st.switch_page(page)

left,right=st.columns([1.45,1],gap='large')
with left:
    st.markdown("<div class='sp-section'>Atletas da equipe</div>",unsafe_allow_html=True)
    show_people=athletes[:6]
    if show_people:
        pcs=st.columns(3,gap='small')
        for i,a in enumerate(show_people):
            with pcs[i%3]:
                st.markdown("<div class='sp-person'>",unsafe_allow_html=True)
                if a.get('photo_url'): st.image(a['photo_url'],use_container_width=True)
                else: st.markdown("<div style='height:120px;display:flex;align-items:center;justify-content:center;font-size:44px;background:#091827;border-radius:8px'>🛹</div>",unsafe_allow_html=True)
                loc='/'.join(x for x in [a.get('city'),a.get('state')] if x)
                st.markdown(f"<div class='sp-person-name'>{a.get('full_name') or 'Atleta'}</div><div class='sp-person-role'>Atleta · {a.get('modality') or '—'}</div><div class='sp-person-meta'>◉ {a.get('stance') or 'Base não informada'}<br>⌖ {loc or 'Cidade não informada'}</div></div>",unsafe_allow_html=True)
                if st.button('Ver equipe →',key=f"home_person_{a['id']}",use_container_width=True): st.switch_page('pages/02_Times.py')
    else: st.info('Nenhum atleta visível para este perfil.')
with right:
    st.markdown("<div class='sp-section'>Próximos eventos</div>",unsafe_allow_html=True)
    if visible_events:
        evhtml="<div class='sp-panel'>"
        for e in visible_events:
            raw=e.get('event_date') or ''
            try: d=date.fromisoformat(raw); db=f"{d.day:02d}<br><span style='font-size:10px'>{d.strftime('%b').upper()}</span>"
            except: db=raw
            evhtml+=f"<div class='sp-event'><div class='sp-date'>{db}</div><div><div class='sp-event-name'>{e.get('title') or 'Evento'}</div><div class='sp-event-loc'>{e.get('location') or 'Local não informado'}</div></div></div>"
        st.markdown(evhtml+'</div>',unsafe_allow_html=True)
    else: st.markdown("<div class='sp-panel'><div style='color:#8499ad'>Nenhum próximo evento cadastrado.</div></div>",unsafe_allow_html=True)
    if st.button('Ver calendário completo →',use_container_width=True,key='fullcal'): st.switch_page('pages/06_Calendario.py')

st.markdown("<div class='sp-section'>Últimos treinos</div>",unsafe_allow_html=True)
if visible_trainings:
    tcols=st.columns(min(3,len(visible_trainings)),gap='small')
    pmap={p['id']:p.get('full_name','Atleta') for p in visible_profiles}
    for i,t in enumerate(visible_trainings[:3]):
        raw=t.get('training_date') or ''
        try: ds=date.fromisoformat(raw).strftime('%d/%m/%Y')
        except: ds=raw
        with tcols[i]: st.markdown(f"<div class='sp-train'><div style='color:#29a8ff;font-size:11px'>TREINO</div><div class='sp-train-date'>{ds}</div><div class='sp-train-name'>{pmap.get(t.get('athlete_id'),'Atleta')} · {t.get('title') or 'Sessão de treino'}</div></div>",unsafe_allow_html=True)
else: st.caption('Nenhum treino visível ainda.')
