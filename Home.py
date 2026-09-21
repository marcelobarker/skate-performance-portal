
import streamlit as st
import streamlit.components.v1 as components
from auth_utils import sign_in, sign_up, sign_out, current_user, current_profile, load_profile, get_supabase, _navigation

from ui_theme import apply_ui_theme

st.set_page_config(initial_sidebar_state="expanded", page_title="Skate Performance • Portal", page_icon="🛹", layout="wide")
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
[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important}
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

st.markdown("""<div class="hero"><div class="brand">SKATE<span class="blue">PERFORMANCE</span><span class="time">BRASIL</span></div>
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
        # Ajuda Chrome/Safari/Edge a reconhecerem os campos como credenciais salvas.
        # Streamlit não expõe autocomplete diretamente no st.text_input, então ajustamos
        # os atributos dos inputs no DOM sem alterar a autenticação Python.
        components.html("""<script>
        (function(){
          function mark(){
            try{
              const d=window.parent.document;
              const inputs=[...d.querySelectorAll('input')];
              const email=inputs.find(i => (i.getAttribute('aria-label')||'').toLowerCase().includes('e-mail'));
              const pass=inputs.find(i => i.type==='password');
              if(email){email.setAttribute('autocomplete','email');email.setAttribute('name','email');email.setAttribute('id','sp-login-email');}
              if(pass){pass.setAttribute('autocomplete','current-password');pass.setAttribute('name','password');pass.setAttribute('id','sp-login-password');}
            }catch(e){}
          }
          mark(); setTimeout(mark,250); setTimeout(mark,900);
        })();
        </script>""", height=0)
        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="seu@email.com")
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
    display_role = "ADMINISTRADOR • MEMBRO DO STAFF" if role == "admin" else role.upper()
    st.caption(f"Perfil: {display_role} • Status: {status.upper()}")
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

_navigation(role)

import base64
from pathlib import Path
from datetime import date, datetime
hero_b64=base64.b64encode((Path(__file__).parent/'hero_skater.jpg').read_bytes()).decode()
try:
    _hs=get_supabase().table('portal_settings').select('value').eq('key','home_hero_url').maybe_single().execute()
    hero_url=(_hs.data or {}).get('value') if _hs else None
except Exception:
    hero_url=None
hero_bg = f"url('{hero_url}')" if hero_url else f"url(data:image/jpeg;base64,{hero_b64})"

def svg(kind):
    icons={
    'users':"<svg viewBox='0 0 24 24'><path d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75'/></svg>",
    'coach':"<svg viewBox='0 0 24 24'><path d='M20 21a8 8 0 0 0-16 0M12 13a5 5 0 1 0 0-10 5 5 0 0 0 0 10M18 8h4M20 6v4'/></svg>",
    'team':"<svg viewBox='0 0 24 24'><path d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75'/></svg>",
    'chart':"<svg viewBox='0 0 24 24'><path d='M3 3v18h18M7 16v-5M12 16V7M17 16v-9'/></svg>",
    'calendar':"<svg viewBox='0 0 24 24'><rect x='3' y='5' width='18' height='16' rx='2'/><path d='M16 3v4M8 3v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01'/></svg>",
    'profile':"<svg viewBox='0 0 24 24'><circle cx='12' cy='8' r='4'/><path d='M4 21a8 8 0 0 1 16 0'/></svg>",
    'upload':"<svg viewBox='0 0 24 24'><path d='M12 16V4M7 9l5-5 5 5M5 20h14'/></svg>"}
    return icons[kind]

st.caption('Portal V3.7 • atualização 20/09/2026')
st.markdown(f'''<style>
.sp-home{{margin-top:2px}} .sp-hero2{{height:300px;border:1px solid rgba(20,145,255,.40);border-radius:12px;position:relative;overflow:hidden;background:linear-gradient(90deg,rgba(2,11,20,.88),rgba(2,11,20,.52) 42%,rgba(2,11,20,.16) 72%,rgba(2,11,20,.34) 100%),linear-gradient(0deg,#03111ee8,transparent 55%),{hero_bg} center center/cover no-repeat;box-shadow:0 12px 36px #0008}}
.sp-hero-copy{{position:absolute;left:8%;top:50%;transform:translateY(-50%);max-width:620px}}.sp-hero-copy h1{{font-size:38px;margin:0 0 8px;color:#fff!important;text-shadow:0 0 18px #087cff45}}.sp-hero-copy p{{font-size:16px;color:#d3dfeb!important;line-height:1.55;margin:0}}
.sp-card-link{{display:block;text-decoration:none!important;color:inherit!important}}.sp-card-link:hover{{text-decoration:none!important}}
.sp-kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:18px;position:relative;z-index:3;padding:0 10px}}.sp-kpi2{{height:150px;border-radius:10px;padding:17px 20px;border:1px solid rgba(255,255,255,.18);box-shadow:0 10px 28px #0007,inset 0 1px 0 #ffffff20;position:relative;overflow:hidden}}.sp-kpi2:before{{content:'';position:absolute;width:90px;height:90px;left:-20px;top:-30px;background:#fff2;border-radius:50%;filter:blur(18px)}}.sp-kpi2 svg,.sp-q svg{{width:35px;height:35px;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 7px currentColor)}}.sp-kpi2 .num{{font-size:42px;font-weight:850;line-height:1;margin-top:7px}}.sp-kpi2 .label{{position:absolute;left:68px;top:76px;font-size:13px}}.sp-kpi2 .link{{position:absolute;bottom:14px;left:20px;font-size:12px;color:#eaf7ffcc}}.kblue{{background:linear-gradient(135deg,#087cffed,#004aafe8);color:#66d6ff}}.kgreen{{background:linear-gradient(135deg,#00a96fe0,#00523fe8);color:#38f3c0}}.kpurple{{background:linear-gradient(135deg,#9135e6e8,#4c1788ed);color:#e67cff}}.korange{{background:linear-gradient(135deg,#d76a00e8,#6d3000ed);color:#ffbd55}}
.sp-title{{font-size:19px;font-weight:800;color:#f5f8fc;margin:25px 0 10px}}.sp-quick-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}.sp-q{{min-height:122px;background:linear-gradient(145deg,#0b2034,#051422);border:1px solid rgba(45,130,190,.35);border-radius:10px;text-align:center;padding:17px;color:#29dfff;box-shadow:0 8px 22px #0005,inset 0 1px 0 #ffffff08}}.sp-q:hover{{transform:translateY(-2px);border-color:#00afff;box-shadow:0 0 22px #087cff2e}}.sp-q .qt{{font-size:15px;font-weight:800;color:#f5f8fc;margin-top:6px}}.sp-q .qs{{font-size:11px;color:#8499ad;margin-top:3px}}
.sp-home-panels{{display:grid;grid-template-columns:1.35fr .9fr;gap:14px;margin-top:20px}}.sp-panel2{{background:linear-gradient(145deg,#081b2d,#061727);border:1px solid rgba(50,130,190,.28);border-radius:10px;padding:14px;box-shadow:0 8px 24px #0004}}.sp-ath-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}}.sp-ath{{display:flex;gap:10px;background:#071827;border:1px solid rgba(42,102,145,.28);border-radius:9px;padding:8px;min-height:112px}}.sp-ath img{{width:82px;height:96px;object-fit:cover;border-radius:8px;border:1px solid #1c6a9d}}.sp-ath .nm{{font-weight:800;color:#fff;margin:4px 0}}.sp-ath .rl{{font-size:11px;color:#29a8ff}}.sp-ath .mt{{font-size:11px;color:#9aaec1;line-height:1.65;margin-top:5px}}.sp-event{{display:flex;gap:10px;padding:9px 0;border-bottom:1px solid #163b5938}}.sp-date{{width:58px;background:#0a2945;border-radius:6px;text-align:center;padding:6px;color:#fff;font-weight:800}}.sp-event b{{font-size:12px}}.sp-event small{{display:block;color:#8499ad}}.sp-training-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}}.sp-tr{{background:#071929;border:1px solid rgba(45,100,145,.25);border-radius:8px;padding:12px 14px;min-height:82px}}.sp-tr b{{font-size:15px}}.sp-tr small{{display:block;color:#9aaec1;margin-top:7px}}
@media(max-width:768px){{.sp-hero2{{height:280px;background-position:35% center}}.sp-hero-copy{{left:18px;right:18px;top:auto;bottom:24px;transform:none}}.sp-hero-copy h1{{font-size:29px}}.sp-kpi-grid{{grid-template-columns:repeat(2,1fr);margin-top:16px;padding:0}}.sp-kpi2{{height:132px;padding:13px}}.sp-kpi2 .num{{font-size:34px}}.sp-kpi2 .label{{left:54px;top:67px}}.sp-kpi2 .link{{left:13px;bottom:10px}}.sp-quick-grid{{grid-template-columns:repeat(2,1fr)}}.sp-home-panels{{grid-template-columns:1fr}}.sp-ath-grid{{grid-template-columns:1fr}}.sp-training-grid{{grid-template-columns:1fr}}}}
</style>''',unsafe_allow_html=True)

try:
    sb=get_supabase(); visible_profiles=sb.table('profiles').select('id,full_name,role,status,photo_url,modality,stance,city,state,birth_date').execute().data or []; visible_teams=sb.table('teams').select('id,name').execute().data or []; visible_trainings=sb.table('training_sessions').select('id,athlete_id,training_date,title,created_at').order('training_date',desc=True).limit(6).execute().data or []
    try: visible_events=sb.table('calendar_events').select('*').gte('event_date',date.today().isoformat()).order('event_date').limit(4).execute().data or []
    except: visible_events=[]
except Exception as exc:
    visible_profiles=[]; visible_teams=[]; visible_trainings=[]; visible_events=[]; st.warning(f'Não foi possível atualizar a Home: {exc}')
athletes=[x for x in visible_profiles if x.get('role')=='skatista' and x.get('status')=='ativo']; staff=[x for x in visible_profiles if x.get('role') in ('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica') and x.get('status')=='ativo']
first=name.split()[0] if name else 'Atleta'
if role == 'admin':
    with st.expander('🖼️ Personalizar imagem de boas-vindas'):
        hero_file=st.file_uploader('Imagem de fundo da Home',type=['jpg','jpeg','png','webp'],key='hero_upload')
        if hero_file and st.button('Salvar nova imagem de fundo',type='primary',use_container_width=True):
            try:
                ext=hero_file.name.rsplit('.',1)[-1].lower(); path=f"{user.id}/home-hero.{ext}"
                try: sb.storage.from_('profile-photos').remove([path])
                except Exception: pass
                sb.storage.from_('profile-photos').upload(path,hero_file.getvalue(),{'content-type':hero_file.type,'upsert':'true'})
                url=sb.storage.from_('profile-photos').get_public_url(path)
                sb.table('portal_settings').upsert({'key':'home_hero_url','value':url}).execute()
                st.success('Imagem de boas-vindas atualizada.'); st.rerun()
            except Exception as e: st.error(f'Não foi possível salvar a imagem: {e}')
st.markdown(f"<div class='sp-home'><div class='sp-hero2'><div class='sp-hero-copy'><h1>Bem-vindo, {first}!</h1><p>Acompanhe o desempenho da sua equipe, veja seus treinos, analise suas manobras e evolua junto com seus atletas.</p></div></div>",unsafe_allow_html=True)
kpis=[('users',len(athletes),'Atletas','kblue','Ver equipe →','pages/02_Times.py','home_kpi_athletes'),('coach',len(staff),'Técnicos','kgreen','Ver equipe →','pages/02_Times.py','home_kpi_staff'),('team',len(visible_teams),'Times','kpurple','Ver times →','pages/02_Times.py','home_kpi_teams'),('chart',len(visible_trainings),'Treinos','korange','Ver atletas →','pages/02_Times.py','home_kpi_trainings')]
# Mantém exatamente os cards HTML aprovados; um botão transparente por cima cuida só da navegação.
st.markdown("""<style>
/* V3.7 — os botões Streamlit continuam fazendo a navegação, mas ficam realmente
   sobre os cards aprovados e 100% invisíveis. Não existe mais botão 'abrir'. */
[class*='st-key-home_kpi_']{margin-top:-150px!important;height:150px!important;position:relative!important;z-index:30!important}
[class*='st-key-home_kpi_'] [data-testid='stButton'],
[class*='st-key-home_quick_'] [data-testid='stButton']{height:100%!important}
[class*='st-key-home_kpi_'] button{height:150px!important;width:100%!important;opacity:0!important;border:0!important;background:transparent!important;box-shadow:none!important;font-size:0!important;color:transparent!important;padding:0!important}
[class*='st-key-home_quick_']{margin-top:-122px!important;height:122px!important;position:relative!important;z-index:30!important}
[class*='st-key-home_quick_'] button{height:122px!important;width:100%!important;opacity:0!important;border:0!important;background:transparent!important;box-shadow:none!important;font-size:0!important;color:transparent!important;padding:0!important}
[class*='st-key-home_kpi_'] button *,[class*='st-key-home_quick_'] button *{display:none!important}
</style>""",unsafe_allow_html=True)
kcols=st.columns(4,gap='small')
for col,(ic,num,lab,cl,lk,page,key) in zip(kcols,kpis):
    with col:
        st.markdown(f"<div class='sp-kpi2 {cl}'>{svg(ic)}<div class='num'>{num}</div><div class='label'>{lab}</div><div class='link'>{lk}</div></div>",unsafe_allow_html=True)
        st.markdown("<div class='sp-nav-overlay'>",unsafe_allow_html=True)
        if st.button('abrir',key=key,width='stretch'): st.switch_page(page)
        st.markdown("</div>",unsafe_allow_html=True)
st.markdown("<div class='sp-title'>Acesso rápido</div>",unsafe_allow_html=True)
quick=[('team','Times','Veja sua equipe e os membros','pages/02_Times.py'),('calendar','Calendário','Próximos eventos','pages/06_Calendario.py'),('chart','Nova Análise','Analisar um CSV','pages/03_Analise_de_Treino.py'),('profile','Meu Perfil','Editar meus dados','pages/05_Meu_Perfil.py')]
if role in ('skatista','familiar'): quick[2]=('chart','Meu Feed','Vídeos e histórico do atleta','pages/07_Perfil_do_Atleta.py')
qcols=st.columns(4,gap='small')
for i,(ic,t,sub,page) in enumerate(quick):
    with qcols[i]:
        st.markdown(f"<div class='sp-q'>{svg(ic)}<div class='qt'>{t}</div><div class='qs'>{sub}</div></div>",unsafe_allow_html=True)
        st.markdown("<div class='sp-quick-overlay'>",unsafe_allow_html=True)
        if st.button('abrir',key=f'home_quick_{i}',width='stretch'): st.switch_page(page)
        st.markdown("</div>",unsafe_allow_html=True)

def age(v):
    try:
        b=date.fromisoformat(v); td=date.today(); return td.year-b.year-((td.month,td.day)<(b.month,b.day))
    except:return None
ath_html="<div class='sp-panel2'><div class='sp-title' style='margin-top:0'>Atletas da equipe</div><div class='sp-ath-grid'>"
for a in athletes[:6]:
    loc='/'.join(x for x in [a.get('city'),a.get('state')] if x) or 'Cidade não informada'; ag=age(a.get('birth_date')); img=a.get('photo_url') or ''
    photo=f"<img src='{img}' alt=''>" if img else "<div style='width:82px;height:96px;border-radius:8px;background:#0a2945;display:grid;place-items:center;font-size:30px'>🛹</div>"
    ath_html+=f"<div class='sp-ath'>{photo}<div><div class='nm'>{a.get('full_name') or 'Atleta'}</div><div class='rl'>Atleta</div><div class='mt'>♙ {str(ag)+' anos' if ag is not None else '—'}<br>◉ {a.get('modality') or '—'}<br>⌖ {loc}</div></div></div>"
ath_html+='</div></div>'
ev_html="<div class='sp-panel2'><div class='sp-title' style='margin-top:0'>Próximos eventos</div>"
for e in visible_events:
    try:d=date.fromisoformat(e.get('event_date')); ds=f"{d.day:02d}<br><small>{d.strftime('%b').upper()}</small>"
    except:ds=e.get('event_date','')
    ev_html+=f"<div class='sp-event'><div class='sp-date'>{ds}</div><div><b>{e.get('title') or 'Evento'}</b><small>{e.get('location') or 'Local não informado'}</small></div></div>"
ev_html += ("<div style='color:#8499ad'>Nenhum próximo evento.</div>" if not visible_events else '')+'</div>'
st.markdown(f"<div class='sp-home-panels'>{ath_html}{ev_html}</div>",unsafe_allow_html=True)
if athletes:
    st.markdown("<div style='margin-top:8px;color:#8499ad;font-size:11px'>Abrir perfil / feed do atleta</div>",unsafe_allow_html=True)
    acols=st.columns(min(len(athletes[:6]),3))
    for i,a in enumerate(athletes[:6]):
        with acols[i%len(acols)]:
            if st.button(f"🛹 {a.get('full_name') or 'Atleta'}",key=f"home_feed_{a['id']}",width='stretch'):
                st.session_state['selected_athlete_id']=a['id']; st.switch_page('pages/07_Perfil_do_Atleta.py')
st.markdown("<div class='sp-title'>Últimos treinos</div>",unsafe_allow_html=True)
pmap={p['id']:p.get('full_name','Atleta') for p in visible_profiles}; th="<div class='sp-training-grid'>"
for t in visible_trainings[:3]:
    try: ds=date.fromisoformat(t.get('training_date')).strftime('%d/%m/%Y')
    except: ds=t.get('training_date','—')
    th+=f"<div class='sp-tr'><span style='color:#29a8ff;font-size:11px'>TREINO</span><br><b>{ds}</b><small>{pmap.get(t.get('athlete_id'),'Atleta')} · {t.get('title') or 'Sessão'}</small></div>"
st.markdown(th+'</div></div>',unsafe_allow_html=True)
