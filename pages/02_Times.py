from datetime import date
import html
import streamlit as st
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme

st.set_page_config(initial_sidebar_state="collapsed", page_title='Times • Skate Performance',page_icon='🛹',layout='wide'); apply_ui_theme()
user,profile=require_login(); sb=get_supabase(); is_admin=profile.get('role')=='admin'
ROLE={'admin':'Admin','skatista':'Atleta','tecnico':'Técnico','presidente':'Presidente','vice_presidente':'Vice-presidente','chefe_equipe':'Chefe de Equipe','comissao_tecnica':'Comissão Técnica','familiar':'Familiar'}
STAFF={'admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica'}
def age(v):
    try:b=date.fromisoformat(v);t=date.today();return t.year-b.year-((t.month,t.day)<(b.month,b.day))
    except:return None

def safe(v): return html.escape(str(v or '—'))

st.markdown('''<style>
.team-head{height:122px;border:1px solid rgba(20,145,255,.45);border-radius:11px;padding:20px 24px;display:flex;align-items:center;gap:18px;background:linear-gradient(90deg,#061727ee,#061727a8),radial-gradient(circle at 85% 40%,#087cff38,transparent 35%),#071827;box-shadow:0 10px 28px #0006}.team-logo{width:82px;height:82px;border:1px solid #3299df;border-radius:10px;display:grid;place-items:center;font-size:36px;background:#020b14cc}.team-name{font-size:25px;font-weight:850;color:#fff}.team-meta{color:#c4d1df;font-size:13px;margin-top:5px}.tabs-fake{display:flex;gap:30px;border-bottom:1px solid #163b59;margin:8px 0 16px}.tabs-fake span{padding:9px 2px;color:#aab9c8;font-size:12px}.tabs-fake .on{color:#00d9ff;border-bottom:2px solid #00afff}.member-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.member-card{height:132px;background:#071827;border:1px solid rgba(42,102,145,.28);border-radius:9px;display:flex;overflow:hidden;box-shadow:0 8px 22px #0004}.member-photo{width:96px;min-width:96px;height:132px;object-fit:cover;border-right:1px solid #164f78}.member-placeholder{width:96px;min-width:96px;height:132px;display:grid;place-items:center;font-size:34px;background:#0a2945}.member-info{padding:12px 10px}.member-name{font-weight:800;color:#fff;font-size:14px}.badge{display:inline-block;font-size:10px;color:#29a8ff;margin:3px 0 6px}.badge.orange{color:#ffb13b}.member-meta{font-size:11px;color:#a9bdd0;line-height:1.75}.eye-row [data-testid="stButton"] button{min-height:31px!important;height:31px!important;padding:0 12px!important;border-radius:8px!important}.team-section{font-size:17px;font-weight:800;margin:14px 0 8px;color:#fff}
[data-testid="stImage"] button{display:none!important}
@media(max-width:900px){.member-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:600px){.member-grid{grid-template-columns:1fr}.team-head{height:auto}.member-card{height:126px;width:100%;max-width:100%;overflow:hidden}.member-photo,.member-placeholder{width:92px;min-width:92px;height:126px}.member-info{min-width:0;flex:1;padding:10px}.member-name{font-size:13px;white-space:normal;overflow-wrap:anywhere}.member-meta{font-size:10px;line-height:1.6;white-space:normal;overflow-wrap:anywhere}.eye-row [data-testid='stHorizontalBlock']{display:flex!important;flex-wrap:nowrap!important;gap:8px!important}.eye-row [data-testid='stHorizontalBlock']>[data-testid='stColumn']{min-width:0!important;width:50%!important;flex:1 1 50%!important}.eye-row button{font-size:12px!important;padding:0 8px!important}}
</style>''',unsafe_allow_html=True)

@st.dialog('Perfil do membro',width='large')
def card(p):
    ag=age(p.get('birth_date')); loc=' / '.join(x for x in [p.get('city'),p.get('state')] if x) or '—'; role=ROLE.get(p.get('role'),'Membro'); photo=p.get('photo_url')
    pic=f"<img class='profile-card-photo' src='{safe(photo)}'>" if photo else "<div class='profile-card-ph'>🛹</div>"
    accent='#ff9f2f' if p.get('role')=='chefe_equipe' else '#087cff'
    st.markdown(f"""<style>.pc{{position:relative;overflow:hidden;background:radial-gradient(circle at 85% 10%,{accent}22,transparent 32%),linear-gradient(145deg,#081d31,#020b14);border:1px solid #168edb;border-radius:16px;padding:22px;box-shadow:0 20px 60px #000b,0 0 32px #087cff18}}.pc:after{{content:'SKATE';position:absolute;right:-8px;bottom:-24px;font-size:92px;font-weight:950;color:#ffffff05;transform:rotate(-8deg)}}.pc-grid{{display:grid;grid-template-columns:190px 1fr;gap:24px;align-items:center;position:relative;z-index:1}}.profile-card-photo,.profile-card-ph{{width:190px;height:230px;object-fit:cover;border-radius:13px;border:1px solid #3299df;box-shadow:0 0 25px #087cff26}}.profile-card-ph{{display:grid;place-items:center;background:#0a2945;font-size:54px}}.pc h2{{font-size:27px;margin:0 0 7px!important}}.pc-role{{display:inline-block;background:linear-gradient(90deg,{accent},#006aff);color:white!important;padding:5px 14px;border-radius:999px;font-size:11px;font-weight:800;box-shadow:0 0 14px {accent}55}}.pc-info{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}}.pc-i{{background:#081b2d;border:1px solid #163b59;border-radius:9px;padding:10px 12px}}.pc-i span{{display:block;color:#8499ad!important;font-size:10px;text-transform:uppercase;letter-spacing:.7px}}.pc-i b{{display:block;color:#f5f8fc!important;margin-top:3px;font-size:13px}}@media(max-width:600px){{.pc-grid{{grid-template-columns:1fr}}.profile-card-photo,.profile-card-ph{{width:100%;height:330px}}}}</style><div class='pc'><div class='pc-grid'>{pic}<div><h2>{safe(p.get('full_name'))}</h2><span class='pc-role'>{safe(role)}</span><div class='pc-info'><div class='pc-i'><span>Idade</span><b>{str(ag)+' anos' if ag is not None else '—'}</b></div><div class='pc-i'><span>Modalidade</span><b>{safe(p.get('modality'))}</b></div><div class='pc-i'><span>Base</span><b>{safe(p.get('stance'))}</b></div><div class='pc-i'><span>Cidade</span><b>{safe(loc)}</b></div></div></div></div></div>""",unsafe_allow_html=True)

def fetch():
    # A vitrine de Times é visível para todos os usuários ativos.
    # A Comissão Técnica vem diretamente dos cargos ativos e não depende de vínculo em Street/Park.
    teams=sb.table('teams').select('*').order('name').execute().data or []
    mem=sb.table('team_members').select('team_id,profile_id').execute().data or []
    prof=sb.table('profiles').select('id,full_name,email,role,status,modality,stance,photo_url,birth_date,city,state').eq('status','ativo').order('full_name').execute().data or []
    return teams,prof,mem

def render_people(group, scope):
    if not group:
        st.caption('Nenhum membro nesta seção.'); return
    rows=[group[i:i+3] for i in range(0,len(group),3)]
    for ri,row in enumerate(rows):
        cols=st.columns(3,gap='small')
        for j,p in enumerate(row):
            with cols[j]:
                ag=age(p.get('birth_date')); loc='/'.join(x for x in [p.get('city'),p.get('state')] if x) or '—'; ph=p.get('photo_url'); rolelbl=ROLE.get(p.get('role'),'Membro'); orange=' orange' if p.get('role')=='chefe_equipe' else ''
                pic=f"<img class='member-photo' src='{safe(ph)}'>" if ph else "<div class='member-placeholder'>🛹</div>"
                meta=(f"Idade: {str(ag)+' anos' if ag is not None else '—'}<br>Modalidade: {safe(p.get('modality'))}<br>Local: {safe(loc)}") if p.get('role')=='skatista' else f"Modalidade: {safe(p.get('modality'))}<br>Local: {safe(loc)}"
                st.markdown(f"<div class='member-card'>{pic}<div class='member-info'><div class='member-name'>{safe(p.get('full_name'))}</div><div class='badge{orange}'>{safe(rolelbl)}</div><div class='member-meta'>{meta}</div></div></div>",unsafe_allow_html=True)
                if p.get('role')=='skatista':
                    b1,b2=st.columns(2,gap='small')
                    if b1.button('Cartão',key=f"eye_{scope}_{p['id']}",use_container_width=True): card(p)
                    if b2.button('Perfil / Feed',key=f"feed_{scope}_{p['id']}",use_container_width=True):
                        st.session_state['selected_athlete_id']=p['id']; st.switch_page('pages/07_Perfil_do_Atleta.py')
                else:
                    if st.button('Ver cartão',key=f"eye_{scope}_{p['id']}",use_container_width=True): card(p)

def render_team(team, profiles, memberships, scope):
    tid=team['id']; byid={p['id']:p for p in profiles}; ids=[m['profile_id'] for m in memberships if m['team_id']==tid]
    people=[byid[x] for x in ids if x in byid]; athletes=[p for p in people if p.get('role')=='skatista']
    st.markdown(f"<div class='team-head'><div class='team-logo'>🛹</div><div><div class='team-name'>{safe(team.get('name'))}</div><div class='team-meta'>{safe(team.get('modality'))} &nbsp; • &nbsp; {len(athletes)} atletas</div></div></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='team-section'>Atletas ({len(athletes)})</div>",unsafe_allow_html=True)
    render_people(athletes,scope)
    if is_admin:
        with st.expander('⚙️ Gerenciar time'):
            opts={f"{p.get('full_name') or p.get('email')} • {ROLE.get(p.get('role'),'Membro')}":p['id'] for p in profiles}; defaults=[k for k,v in opts.items() if v in ids]
            sel=st.multiselect('Membros do time',list(opts),default=defaults,key=f'm_{tid}')
            if st.button('Salvar membros',key=f's_{tid}'):
                new={opts[x] for x in sel};old=set(ids)
                for pid in old-new: sb.table('team_members').delete().eq('team_id',tid).eq('profile_id',pid).execute()
                rows=[{'team_id':tid,'profile_id':pid} for pid in new-old]
                if rows: sb.table('team_members').insert(rows).execute()
                st.rerun()

st.title('Times')
st.caption('Seleção Brasileira • Street, Park e Comissão Técnica')
try: teams,profiles,memberships=fetch()
except Exception as e: st.error(f'Não foi possível carregar os times: {e}'); st.stop()

if is_admin:
    with st.expander('＋ Criar novo time'):
        with st.form('newteam'): name=st.text_input('Nome do time'); mod=st.selectbox('Modalidade',['Street','Park','Vert','Misto']); ok=st.form_submit_button('Criar time')
        if ok and name.strip(): sb.table('teams').insert({'name':name.strip(),'modality':mod}).execute();st.rerun()

street=[t for t in teams if str(t.get('modality') or '').lower()=='street']
park=[t for t in teams if str(t.get('modality') or '').lower()=='park']
commission=[p for p in profiles if p.get('role') in STAFF]

t1,t2,t3=st.tabs([f'🛹 STREET ({len(street)})',f'◉ PARK ({len(park)})',f'★ COMISSÃO TÉCNICA ({len(commission)})'])
with t1:
    if not street: st.info('Nenhum time Street cadastrado.')
    for i,t in enumerate(street): render_team(t,profiles,memberships,f'street_{i}')
with t2:
    if not park: st.info('Nenhum time Park cadastrado.')
    for i,t in enumerate(park): render_team(t,profiles,memberships,f'park_{i}')
with t3:
    st.markdown("<div class='team-head'><div class='team-logo'>★</div><div><div class='team-name'>Comissão Técnica</div><div class='team-meta'>Presidência, chefia de equipe, técnicos e staff ativo</div></div></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='team-section'>Equipe ({len(commission)})</div>",unsafe_allow_html=True)
    render_people(commission,'commission')
