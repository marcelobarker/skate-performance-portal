
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

# V4.01: a Home e o login não usam a sidebar antiga.
st.markdown("""<style>
section[data-testid="stSidebar"],[data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"],[data-testid="stSidebarCollapsedControl"],button[aria-label="Open sidebar"],button[aria-label="Close sidebar"]{display:none!important;visibility:hidden!important}
[data-testid="stAppViewContainer"]>.main{margin-left:0!important;width:100%!important}
</style>""", unsafe_allow_html=True)

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

# V4.01 PREMIUM — reconstrução da Home em tela cheia, sem a Home antiga/Sidebar.
def svg_icon(kind, color="#25c7ff"):
    icons = {
        "home": '<path d="M3 11.5 12 4l9 7.5v8a1.5 1.5 0 0 1-1.5 1.5H15v-6H9v6H4.5A1.5 1.5 0 0 1 3 19.5z"/>',
        "chart": '<path d="M4 20V10m6 10V4m6 16v-7m5 7V7"/>',
        "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm13 10v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
        "team": '<path d="M8 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2M14 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M2 21v-2a4 4 0 0 1 3-3.87M6 3.13a4 4 0 0 0 0 7.75"/>',
        "history": '<path d="M3 12a9 9 0 1 0 3-6.7L3 8m0-5v5h5M12 7v5l3 2"/>',
        "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v3m10 7h-3M12 22v-3M2 12h3"/>',
        "board": '<path d="M5 15c3 1 11 1 14 0M7 12h10M8 18a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm8 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z"/>',
        "play": '<path d="m9 7 8 5-8 5z"/>',
        "arrow": '<path d="M5 12h14m-5-5 5 5-5 5"/>',
    }
    return f'<svg viewBox="0 0 24 24" aria-hidden="true" style="width:1em;height:1em;fill:none;stroke:{color};stroke-width:2;stroke-linecap:round;stroke-linejoin:round">{icons.get(kind, icons["chart"])}</svg>'

hero_data = f"data:image/jpeg;base64,{hero_b64}"
hero_image = hero_url or hero_data
avatar_html = f"<img class='v401-avatar' src='{photo}'>" if photo else f"<div class='v401-avatar fallback'>{initials}</div>"
role_label = 'Administrador' if role=='admin' else role.replace('_',' ').title()

st.markdown(f"""
<style>
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"],.stApp{{background:#020b14!important}}
header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{{display:none!important}}
section[data-testid="stSidebar"],[data-testid="stSidebar"],[data-testid="stSidebarNav"]{{display:none!important;visibility:hidden!important;width:0!important;min-width:0!important;transform:translateX(-100%)!important}}
[data-testid="stAppViewContainer"]>.main{{margin-left:0!important;width:100%!important}}
.block-container{{max-width:1660px!important;width:100%!important;padding:18px 28px 38px!important;margin:0 auto!important}}
.v401{{font-family:Inter,ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;color:#f7fbff}} .v401 *{{box-sizing:border-box}}
.v401-shell{{overflow:hidden;border:1px solid #0d4267;border-radius:18px;background:#020c16;box-shadow:0 26px 80px rgba(0,0,0,.55)}}
.v401-top{{height:74px;display:flex;align-items:center;padding:0 26px;background:rgba(3,16,28,.97);border-bottom:1px solid #12324a;gap:34px}}
.v401-brand{{display:flex;align-items:center;gap:10px;min-width:235px;text-decoration:none}} .v401-mark{{width:39px;height:39px;display:grid;place-items:center;filter:drop-shadow(0 0 12px #0caeff88)}} .v401-mark svg{{width:39px;height:39px}}
.v401-brandtext{{line-height:.88}} .v401-brandtext b{{font-size:18px;font-weight:950;letter-spacing:-.8px;color:#fff}} .v401-brandtext b i{{color:#15b6ff;font-style:normal}} .v401-brandtext small{{display:block;color:#b6c8d6;font-size:6px;letter-spacing:1.6px;margin-top:7px;font-weight:800}}
.v401-nav{{height:100%;display:flex;align-items:center;gap:32px;flex:1}} .v401-nav a{{height:100%;display:flex;align-items:center;gap:7px;color:#93a8ba!important;text-decoration:none!important;font-size:12px;font-weight:750;position:relative}} .v401-nav a svg{{font-size:15px}} .v401-nav a:hover{{color:#fff!important}} .v401-nav a.active{{color:#16bdff!important}} .v401-nav a.active:after{{content:'';height:3px;border-radius:3px;background:#12baff;box-shadow:0 0 15px #0baeff;position:absolute;left:0;right:0;bottom:0}}
.v401-tools{{display:flex;align-items:center;gap:14px;color:#b8c8d5}} .v401-tool{{width:30px;height:30px;display:grid;place-items:center;border-radius:50%;font-size:17px}} .v401-user{{display:flex;align-items:center;gap:10px;margin-left:2px}} .v401-avatar{{width:38px;height:38px;border-radius:50%;object-fit:cover;border:2px solid #13baff;box-shadow:0 0 15px #0aaeff55}} .v401-avatar.fallback{{display:grid;place-items:center;background:#0b314b;font-size:11px;font-weight:900}} .v401-user b{{font-size:11px;color:#fff}} .v401-user small{{display:block;font-size:8px;color:#7f98ab;margin-top:2px}}
.v401-hero{{height:490px;position:relative;background-image:linear-gradient(90deg,rgba(1,9,16,.90) 0%,rgba(1,9,16,.70) 30%,rgba(1,9,16,.10) 63%,rgba(1,9,16,.18) 100%),linear-gradient(0deg,#020c16 0%,rgba(2,12,22,.12) 45%),url('{hero_image}');background-size:cover;background-position:center 48%}}
.v401-copy{{position:absolute;left:44px;top:82px;width:520px;text-shadow:0 4px 25px #000}} .v401-kicker{{font-size:13px;font-weight:950;letter-spacing:.7px;color:#fff}} .v401-country{{font-size:11px;color:#15c2ff;font-weight:950;letter-spacing:4px;margin-top:5px}} .v401-copy h1{{font-size:48px!important;line-height:.95!important;letter-spacing:-2.1px!important;color:#fff!important;margin:14px 0 12px!important;font-weight:950!important}} .v401-copy p{{font-size:10px!important;color:#dbe7ef!important;font-weight:800!important;letter-spacing:.3px}}
.v401-actions{{position:absolute;left:44px;top:285px;display:flex;gap:13px}} .v401-btn{{height:50px;min-width:178px;padding:0 22px;border-radius:8px;border:1px solid #079cff;background:linear-gradient(180deg,#159cff,#0676f4);color:#fff!important;text-decoration:none!important;display:flex;align-items:center;justify-content:center;gap:9px;font-size:12px;font-weight:900;box-shadow:0 9px 24px #057cff55,inset 0 1px 0 #ffffff44;transition:.18s}} .v401-btn:hover{{transform:translateY(-2px);filter:brightness(1.08);box-shadow:0 11px 28px #057cff77}} .v401-btn.alt{{background:rgba(2,14,25,.72);border-color:#168bd0;box-shadow:inset 0 0 22px #0a82cf14}}
.v401-kpis{{position:absolute;left:28px;right:28px;bottom:18px;display:grid;grid-template-columns:repeat(5,1fr);gap:10px}} .v401-kpi{{height:94px;border-radius:11px;border:1px solid #173b55;background:linear-gradient(145deg,rgba(13,35,51,.95),rgba(5,20,32,.96));display:flex;align-items:center;gap:13px;padding:14px 16px;box-shadow:0 12px 30px #0007,inset 0 1px #ffffff0d}} .v401-kicon{{width:45px;height:45px;flex:0 0 45px;border-radius:50%;display:grid;place-items:center;font-size:23px}} .v401-kicon svg{{font-size:23px}} .v401-kpi strong{{font-size:22px;color:#fff;line-height:1}} .v401-kpi label{{display:block!important;color:#a9bbc9!important;font-size:9px;margin-top:5px}} .v401-kpi em{{display:block;color:#14e8a0;font-size:9px;font-style:normal;font-weight:900;margin-top:3px}}
.k-purple{{background:#171c4b;box-shadow:0 0 20px #685cff33}} .k-green{{background:#063d35;box-shadow:0 0 20px #00e4a433}} .k-gold{{background:#493b08;box-shadow:0 0 20px #ffc40033}} .k-blue{{background:#073857;box-shadow:0 0 20px #14b6ff33}} .k-cyan{{background:#07394c;box-shadow:0 0 20px #00dcff33}}
.v401-body{{padding:19px 28px 28px;background:linear-gradient(180deg,#020c16,#03121f)}} .v401-title{{font-size:16px;font-weight:950;color:#fff;margin:0 0 13px}} .v401-quick{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}} .v401-card{{height:155px;position:relative;overflow:hidden;border-radius:11px;border:1px solid #087ebf;text-decoration:none!important;background-size:cover;background-position:center;box-shadow:0 9px 25px #0007,0 0 18px #008cff12;transition:.2s}} .v401-card:before{{content:'';position:absolute;inset:0;background:linear-gradient(0deg,rgba(1,9,16,.96),rgba(1,9,16,.10) 72%),linear-gradient(90deg,rgba(3,20,32,.35),transparent)}} .v401-card:hover{{transform:translateY(-3px);border-color:#18baff;box-shadow:0 12px 30px #0008,0 0 22px #00aaff2e}} .v401-card span{{position:absolute;left:15px;bottom:13px;color:#fff;font-size:15px;font-weight:900;z-index:2}} .v401-card .arr{{position:absolute;right:12px;bottom:10px;width:31px;height:31px;border-radius:50%;display:grid;place-items:center;background:#ffffff12;border:1px solid #ffffff0c;z-index:2}} .v401-card .arr svg{{font-size:16px}}
.v401-card.c1{{background-image:url('{hero_image}');background-position:20% 65%}} .v401-card.c2{{background-image:url('{hero_image}');background-position:48% 48%;filter:saturate(.75)}} .v401-card.c3{{background-image:url('{hero_image}');background-position:72% 60%}} .v401-card.c4{{background-image:linear-gradient(rgba(4,15,24,.30),rgba(4,15,24,.30)),url('{hero_image}');background-position:88% 45%;filter:grayscale(.75)}} .v401-mobilemenu{{display:none}}
@media(max-width:800px){{.block-container{{padding:0!important;max-width:none!important}} .v401-shell{{border-radius:0;border-left:0;border-right:0;min-height:100vh}} .v401-top{{height:66px;padding:0 16px;gap:12px}} .v401-brand{{min-width:0;flex:1}} .v401-brandtext b{{font-size:15px}} .v401-brandtext small{{font-size:5px}} .v401-mark{{width:32px}} .v401-mark svg{{width:32px}} .v401-nav,.v401-tools,.v401-user{{display:none}} .v401-mobilemenu{{display:grid;width:38px;height:38px;place-items:center;font-size:24px;color:#dceaf5}} .v401-hero{{height:565px;background-position:61% center}} .v401-copy{{left:18px;right:18px;top:300px;width:auto}} .v401-kicker,.v401-country,.v401-copy p{{display:none}} .v401-copy h1{{font-size:31px!important;line-height:1!important;max-width:310px;margin:0!important}} .v401-actions{{left:18px;right:18px;top:378px}} .v401-btn{{width:100%;min-width:0;height:49px}} .v401-btn.alt{{display:none}} .v401-kpis{{left:18px;right:18px;bottom:16px;grid-template-columns:1fr;gap:7px}} .v401-kpi{{height:55px;padding:6px 12px}} .v401-kpi:nth-child(n+4){{display:none}} .v401-kicon{{width:37px;height:37px;flex-basis:37px}} .v401-kpi strong{{font-size:18px}} .v401-kpi label{{display:inline!important;margin-left:7px}} .v401-kpi em{{display:none}} .v401-body{{padding:17px 14px 82px}} .v401-quick{{grid-template-columns:1fr 1fr}} .v401-card{{height:120px}}}}
</style>
""", unsafe_allow_html=True)

logo_svg = '<svg viewBox="0 0 48 48"><path fill="#11baff" d="M8 10l8 8 8-13 6 14 10-9-5 29H13z"/><path fill="#fff" d="M15 31h19l-1 5H16z"/></svg>'
st.markdown(f"""
<div class="v401"><div class="v401-shell"><div class="v401-top">
<a class="v401-brand" href="/" target="_self"><div class="v401-mark">{logo_svg}</div><div class="v401-brandtext"><b>SKATE<i>PERFORMANCE</i></b><small>ATHLETE MANAGEMENT • TRAINING INTELLIGENCE</small></div></a>
<nav class="v401-nav"><a class="active" href="/" target="_self">{svg_icon('home')} Home</a><a href="/Analise_de_Treino" target="_self">{svg_icon('chart')} Análise</a><a href="/Times" target="_self">{svg_icon('users')} Atletas</a><a href="/Times" target="_self">{svg_icon('team')} Times</a><a href="/Historico_de_Treinos" target="_self">{svg_icon('history')} Histórico</a></nav>
<div class="v401-tools"><div class="v401-tool">⌕</div><div class="v401-tool">♢</div></div><div class="v401-user">{avatar_html}<div><b>{name}</b><small>{role_label}</small></div></div><div class="v401-mobilemenu">☰</div></div>
<section class="v401-hero"><div class="v401-copy"><div class="v401-kicker">SKATE PERFORMANCE</div><div class="v401-country">TIME BRASIL</div><h1>PERFORMANCE<br>EM EVOLUÇÃO</h1><p>ANÁLISE DE TREINOS • DADOS REAIS • RESULTADOS</p></div>
<div class="v401-actions"><a class="v401-btn" href="/Analise_de_Treino" target="_self">{svg_icon('chart','#fff')} Nova Análise</a><a class="v401-btn alt" href="/Historico_de_Treinos" target="_self">{svg_icon('play','#fff')} Ver Histórico</a></div>
<div class="v401-kpis"><div class="v401-kpi"><div class="v401-kicon k-purple">{svg_icon('chart','#8d7cff')}</div><div><strong>{len(visible_trainings)}</strong><label>Treinos</label><em>histórico</em></div></div><div class="v401-kpi"><div class="v401-kicon k-green">{svg_icon('target','#15e5b2')}</div><div><strong>{len(athletes)}</strong><label>Atletas</label><em>ativos</em></div></div><div class="v401-kpi"><div class="v401-kicon k-gold">{svg_icon('target','#ffc719')}</div><div><strong>{len(visible_teams)}</strong><label>Times</label><em>cadastrados</em></div></div><div class="v401-kpi"><div class="v401-kicon k-blue">{svg_icon('board','#20b8ff')}</div><div><strong>{len(staff)}</strong><label>Staff</label><em>ativo</em></div></div><div class="v401-kpi"><div class="v401-kicon k-cyan">{svg_icon('users','#21d7ff')}</div><div><strong>{len(visible_profiles)}</strong><label>Usuários</label><em>portal</em></div></div></div></section>
<section class="v401-body"><div class="v401-title">Acesso rápido</div><div class="v401-quick"><a class="v401-card c1" href="/Analise_de_Treino" target="_self"><span>Análise</span><div class="arr">{svg_icon('arrow','#fff')}</div></a><a class="v401-card c2" href="/Times" target="_self"><span>Atletas</span><div class="arr">{svg_icon('arrow','#fff')}</div></a><a class="v401-card c3" href="/Times" target="_self"><span>Times</span><div class="arr">{svg_icon('arrow','#fff')}</div></a><a class="v401-card c4" href="/Historico_de_Treinos" target="_self"><span>Histórico</span><div class="arr">{svg_icon('arrow','#fff')}</div></a></div></section></div></div>
""", unsafe_allow_html=True)


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

