
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
from datetime import date

# V4 PREMIUM — somente a aparência da Home autenticada.
# Login, cadastro, autenticação, permissões e páginas existentes permanecem intactos.
hero_b64 = base64.b64encode((Path(__file__).parent / 'hero_skater.jpg').read_bytes()).decode()
try:
    _hs = get_supabase().table('portal_settings').select('value').eq('key','home_hero_url').maybe_single().execute()
    hero_url = (_hs.data or {}).get('value') if _hs else None
except Exception:
    hero_url = None
hero_bg = f"url('{hero_url}')" if hero_url else f"url(data:image/jpeg;base64,{hero_b64})"

try:
    sb = get_supabase()
    visible_profiles = sb.table('profiles').select('id,full_name,role,status,photo_url,modality,city,state').execute().data or []
    visible_teams = sb.table('teams').select('id,name').execute().data or []
    visible_trainings = sb.table('training_sessions').select('id,athlete_id,training_date,title,created_at').order('training_date',desc=True).limit(1000).execute().data or []
except Exception as exc:
    visible_profiles, visible_teams, visible_trainings = [], [], []
    st.warning(f'Não foi possível atualizar os indicadores da Home: {exc}')

athletes = [x for x in visible_profiles if x.get('role') == 'skatista' and x.get('status') == 'ativo']
staff = [x for x in visible_profiles if x.get('role') in ('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica') and x.get('status') == 'ativo']
first = (name.split()[0] if name else 'Atleta')
photo = (profile or {}).get('photo_url') or ''
initials = ''.join([p[0].upper() for p in (name or 'SP').split()[:2]]) or 'SP'

# CSS principal inspirado diretamente no mockup aprovado.
st.markdown(f"""
<style>
.block-container{{max-width:1480px!important;padding-top:.55rem!important;padding-left:1.2rem!important;padding-right:1.2rem!important}}
.spv4{{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#fff}}
.spv4-shell{{background:#020c16;border:1px solid #0b4c78;border-radius:24px;overflow:hidden;box-shadow:0 24px 70px #0009}}
.spv4-top{{height:76px;background:linear-gradient(90deg,#020b13 0%,#06192b 55%,#071827 100%);display:flex;align-items:center;padding:0 28px;border-bottom:1px solid #12324a;gap:34px}}
.spv4-logo{{min-width:195px;line-height:.9}} .spv4-logo strong{{font-size:18px;font-weight:950;letter-spacing:-.8px}} .spv4-logo strong span{{color:#12a9ff}} .spv4-logo small{{display:block;color:#11b7ff;font-size:7px;letter-spacing:3px;margin-top:6px;font-weight:900}}
.spv4-nav{{display:flex;align-items:center;gap:28px;flex:1;height:100%}} .spv4-nav span{{height:100%;display:flex;align-items:center;color:#9fb1c2;font-size:13px;font-weight:650;position:relative}} .spv4-nav .active{{color:#16b7ff}} .spv4-nav .active:after{{content:'';height:3px;background:#0aaeff;border-radius:3px;position:absolute;left:0;right:0;bottom:0;box-shadow:0 0 12px #0aaeff}}
.spv4-user{{display:flex;align-items:center;gap:10px;min-width:170px;justify-content:flex-end}} .spv4-avatar{{width:38px;height:38px;border-radius:50%;border:2px solid #1aaeff;object-fit:cover;background:#0b2940;display:grid;place-items:center;font-size:12px;font-weight:900}} .spv4-user b{{font-size:12px}} .spv4-user small{{display:block;color:#8297aa;font-size:9px}}
.spv4-hero{{height:435px;position:relative;background:linear-gradient(90deg,rgba(1,10,18,.92) 0%,rgba(1,10,18,.72) 31%,rgba(1,10,18,.10) 66%,rgba(1,10,18,.12) 100%),linear-gradient(0deg,#020c16 0%,transparent 38%),{hero_bg} center 52%/cover no-repeat}}
.spv4-copy{{position:absolute;left:46px;top:82px;width:560px}} .spv4-eyebrow{{font-size:14px;font-weight:900;letter-spacing:.5px}} .spv4-time{{color:#0fbaff;letter-spacing:4px;font-size:12px;font-weight:900;margin:5px 0 12px}} .spv4-copy h1{{font-size:47px!important;line-height:.98!important;margin:0 0 12px!important;color:white!important;font-weight:950!important;letter-spacing:-2px;text-shadow:0 3px 22px #000}} .spv4-copy p{{font-size:11px;color:#e4edf4!important;font-weight:800;letter-spacing:.3px;margin:0}}
.spv4-actions{{position:absolute;left:46px;top:282px;display:flex;gap:14px}} .spv4-action{{height:52px;min-width:180px;border-radius:9px;display:flex;align-items:center;justify-content:center;gap:10px;font-size:13px;font-weight:850;border:1px solid #078fff;background:#087cff;color:#fff;box-shadow:0 8px 22px #087cff3d}} .spv4-action.secondary{{background:#061321cc;border-color:#078fff;color:#eaf6ff;box-shadow:none}}
.spv4-kpis{{position:absolute;left:28px;right:28px;bottom:18px;display:grid;grid-template-columns:repeat(5,1fr);gap:10px}} .spv4-kpi{{height:92px;border-radius:13px;background:linear-gradient(145deg,rgba(15,34,49,.94),rgba(7,22,34,.94));border:1px solid #17394f;display:flex;align-items:center;padding:14px;gap:12px;box-shadow:0 12px 24px #0006,inset 0 1px 0 #ffffff0c}} .spv4-ico{{width:46px;height:46px;border-radius:50%;display:grid;place-items:center;font-size:24px;font-weight:900}} .spv4-kpi b{{font-size:24px;line-height:1}} .spv4-kpi small{{display:block;color:#b7c5d1;margin-top:5px;font-size:10px}} .spv4-kpi em{{display:block;color:#19e99d;font-size:10px;font-style:normal;font-weight:900;margin-top:4px}}
.i-purple{{background:#17204b;color:#8074ff}} .i-green{{background:#063b36;color:#16e7ba}} .i-yellow{{background:#47390a;color:#ffc719}} .i-blue{{background:#073557;color:#20b8ff}} .i-cyan{{background:#07364c;color:#21d7ff}}
.spv4-content{{padding:18px 28px 26px;background:linear-gradient(#020c16,#03111d)}} .spv4-section-title{{font-size:17px;font-weight:900;margin:0 0 12px}} .spv4-quick{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}} .spv4-tile{{height:150px;border:1px solid #087bc1;border-radius:12px;overflow:hidden;position:relative;background:#0b1c2a;box-shadow:0 10px 22px #0006}} .spv4-tile:before{{content:'';position:absolute;inset:0;background:linear-gradient(0deg,rgba(1,8,14,.92),rgba(1,8,14,.06) 70%)}} .spv4-tile .fakephoto{{position:absolute;inset:0;background:radial-gradient(circle at 70% 25%,#1a6b8c 0,#0c3248 25%,#071824 65%,#030c13 100%);opacity:.72}} .spv4-tile:nth-child(2) .fakephoto{{background:radial-gradient(circle at 35% 25%,#64543e 0,#173448 32%,#071824 70%)}} .spv4-tile:nth-child(3) .fakephoto{{background:radial-gradient(circle at 65% 35%,#2b7897 0,#1b4051 32%,#071824 70%)}} .spv4-tile:nth-child(4) .fakephoto{{background:radial-gradient(circle at 55% 30%,#616b75 0,#26323c 32%,#071824 70%)}} .spv4-tile b{{position:absolute;left:15px;bottom:14px;font-size:17px;z-index:2}} .spv4-arrow{{position:absolute;right:12px;bottom:11px;width:30px;height:30px;border-radius:50%;background:#ffffff16;display:grid;place-items:center;z-index:2;font-size:18px}}
/* Streamlit overlay buttons: navegação real sem alterar o desenho. */
[class*='st-key-v4_']{{position:relative!important;z-index:50!important}} [class*='st-key-v4_'] button{{opacity:0!important;width:100%!important;border:0!important;background:transparent!important;box-shadow:none!important;color:transparent!important;font-size:0!important;padding:0!important}} [class*='st-key-v4_action_']{{margin-top:-52px!important;height:52px!important}} [class*='st-key-v4_action_'] button{{height:52px!important}} [class*='st-key-v4_tile_']{{margin-top:-150px!important;height:150px!important}} [class*='st-key-v4_tile_'] button{{height:150px!important}}
.spv4-mobilebar{{display:none}}
@media(max-width:800px){{
 .block-container{{padding-left:.5rem!important;padding-right:.5rem!important;padding-top:.35rem!important}} .spv4-shell{{border-radius:17px}} .spv4-top{{height:62px;padding:0 16px}} .spv4-logo{{min-width:auto}} .spv4-logo strong{{font-size:15px}} .spv4-nav,.spv4-user{{display:none}} .spv4-hero{{height:510px;background-position:62% center}} .spv4-copy{{left:18px;right:18px;top:260px;width:auto}} .spv4-eyebrow,.spv4-time,.spv4-copy p{{display:none}} .spv4-copy h1{{font-size:31px!important;max-width:330px}} .spv4-actions{{left:18px;right:18px;top:350px}} .spv4-action{{width:100%;min-width:0}} .spv4-action.secondary{{display:none}} .spv4-kpis{{left:18px;right:18px;bottom:18px;grid-template-columns:1fr;gap:7px}} .spv4-kpi{{height:56px;padding:7px 12px}} .spv4-kpi:nth-child(n+4){{display:none}} .spv4-ico{{width:38px;height:38px;font-size:20px}} .spv4-kpi b{{font-size:20px}} .spv4-kpi small{{display:inline;margin-left:7px}} .spv4-kpi em{{display:none}} .spv4-content{{padding:16px 14px 80px}} .spv4-quick{{grid-template-columns:1fr 1fr}} .spv4-tile{{height:120px}} [class*='st-key-v4_tile_']{{margin-top:-120px!important;height:120px!important}} [class*='st-key-v4_tile_'] button{{height:120px!important}}
}}
</style>
""", unsafe_allow_html=True)

avatar_html = f"<img class='spv4-avatar' src='{photo}'>" if photo else f"<div class='spv4-avatar'>{initials}</div>"

st.markdown(f"""
<div class='spv4'><div class='spv4-shell'>
  <div class='spv4-top'>
    <div class='spv4-logo'><strong>♛ SKATE<span>PERFORMANCE</span></strong><small>TIME BRASIL</small></div>
    <div class='spv4-nav'><span class='active'>Home</span><span>Análise</span><span>Atletas</span><span>Times</span><span>Histórico</span></div>
    <div class='spv4-user'>{avatar_html}<div><b>{name}</b><small>{'Administrador' if role=='admin' else role.replace('_',' ').title()}</small></div></div>
  </div>
  <div class='spv4-hero'>
    <div class='spv4-copy'><div class='spv4-eyebrow'>SKATE PERFORMANCE</div><div class='spv4-time'>TIME BRASIL</div><h1>PERFORMANCE<br>EM EVOLUÇÃO</h1><p>ANÁLISE DE TREINOS • DADOS REAIS • RESULTADOS</p></div>
    <div class='spv4-actions'><div class='spv4-action'>↗ &nbsp; Nova Análise</div><div class='spv4-action secondary'>▷ &nbsp; Ver Histórico</div></div>
    <div class='spv4-kpis'>
      <div class='spv4-kpi'><div class='spv4-ico i-purple'>▥</div><div><b>{len(visible_trainings)}</b><small>Treinos</small><em>histórico</em></div></div>
      <div class='spv4-kpi'><div class='spv4-ico i-green'>◉</div><div><b>{len(athletes)}</b><small>Atletas</small><em>ativos</em></div></div>
      <div class='spv4-kpi'><div class='spv4-ico i-yellow'>◎</div><div><b>{len(visible_teams)}</b><small>Times</small><em>cadastrados</em></div></div>
      <div class='spv4-kpi'><div class='spv4-ico i-blue'>◆</div><div><b>{len(staff)}</b><small>Staff</small><em>ativo</em></div></div>
      <div class='spv4-kpi'><div class='spv4-ico i-cyan'>♙</div><div><b>{len(visible_profiles)}</b><small>Usuários</small><em>portal</em></div></div>
    </div>
  </div>
  <div class='spv4-content'>
    <div class='spv4-section-title'>Acesso rápido</div>
    <div class='spv4-quick'>
      <div class='spv4-tile'><div class='fakephoto'></div><b>Análise</b><div class='spv4-arrow'>→</div></div>
      <div class='spv4-tile'><div class='fakephoto'></div><b>Atletas</b><div class='spv4-arrow'>→</div></div>
      <div class='spv4-tile'><div class='fakephoto'></div><b>Times</b><div class='spv4-arrow'>→</div></div>
      <div class='spv4-tile'><div class='fakephoto'></div><b>Histórico</b><div class='spv4-arrow'>→</div></div>
    </div>
  </div>
</div></div>
""", unsafe_allow_html=True)

# Botões reais invisíveis sobre os dois CTAs.
a1,a2 = st.columns([1,1])
with a1:
    if st.button('Nova Análise', key='v4_action_analysis', use_container_width=True):
        if role in ('skatista','familiar'): st.switch_page('pages/04_Historico_de_Treinos.py')
        else: st.switch_page('pages/03_Analise_de_Treino.py')
with a2:
    if st.button('Ver Histórico', key='v4_action_history', use_container_width=True): st.switch_page('pages/04_Historico_de_Treinos.py')

# Botões reais invisíveis sobre os cards de acesso rápido.
q1,q2,q3,q4 = st.columns(4, gap='small')
with q1:
    if st.button('Análise', key='v4_tile_analysis', use_container_width=True):
        if role in ('skatista','familiar'): st.switch_page('pages/04_Historico_de_Treinos.py')
        else: st.switch_page('pages/03_Analise_de_Treino.py')
with q2:
    if st.button('Atletas', key='v4_tile_athletes', use_container_width=True): st.switch_page('pages/02_Times.py')
with q3:
    if st.button('Times', key='v4_tile_teams', use_container_width=True): st.switch_page('pages/02_Times.py')
with q4:
    if st.button('Histórico', key='v4_tile_history', use_container_width=True): st.switch_page('pages/04_Historico_de_Treinos.py')

# Mantém a personalização de imagem que já existia para o administrador.
if role == 'admin':
    with st.expander('🖼️ Personalizar imagem principal da Home'):
        hero_file = st.file_uploader('Imagem de fundo da Home', type=['jpg','jpeg','png','webp'], key='hero_upload_v4')
        if hero_file and st.button('Salvar nova imagem de fundo', type='primary', use_container_width=True):
            try:
                ext = hero_file.name.rsplit('.',1)[-1].lower(); path = f"{user.id}/home-hero.{ext}"
                try: sb.storage.from_('profile-photos').remove([path])
                except Exception: pass
                sb.storage.from_('profile-photos').upload(path, hero_file.getvalue(), {'content-type':hero_file.type,'upsert':'true'})
                url = sb.storage.from_('profile-photos').get_public_url(path)
                sb.table('portal_settings').upsert({'key':'home_hero_url','value':url}).execute()
                st.success('Imagem principal atualizada.'); st.rerun()
            except Exception as e: st.error(f'Não foi possível salvar a imagem: {e}')

