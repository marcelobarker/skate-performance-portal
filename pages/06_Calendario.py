from datetime import date, datetime, timedelta
import calendar, html
import streamlit as st
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme

st.set_page_config(page_title='Calendário • Skate Performance', page_icon='📅', layout='wide')
apply_ui_theme(); user, profile = require_login(); sb = get_supabase()

st.markdown('''<style>
.cal-form{background:linear-gradient(145deg,#071a2b,#04111e);border:1px solid #163b59;border-radius:14px;padding:18px;margin:10px 0 18px;box-shadow:0 10px 30px #0005}.cal-wrap{display:grid;grid-template-columns:1.12fr .88fr;gap:14px}.cal-card,.events-card{background:linear-gradient(145deg,#071a2b,#04111e);border:1px solid rgba(50,130,190,.30);border-radius:14px;padding:18px;box-shadow:0 12px 34px #0006}.cal-head{display:flex;justify-content:space-between;align-items:center;font-weight:850;margin-bottom:14px}.week,.days{display:grid;grid-template-columns:repeat(7,1fr);text-align:center;gap:7px}.week div{font-size:10px;color:#8499ad;padding:5px}.day{height:42px;display:grid;place-items:center;border-radius:9px;font-size:12px;color:#eaf3fa;position:relative;border:1px solid transparent}.day.today{border-color:#29a8ff;color:#fff;font-weight:900;box-shadow:inset 0 0 0 1px #29a8ff22}.day.event{background:#00d9ff0b}.day.event:after{content:'';position:absolute;bottom:4px;width:5px;height:5px;border-radius:50%;background:#00d9ff;box-shadow:0 0 8px #00d9ff}.event-row{display:grid;grid-template-columns:68px 1fr;gap:12px;padding:11px 0;border-bottom:1px solid #163b5940}.event-row:last-child{border:0}.date-block{background:linear-gradient(145deg,#0a2945,#082039);border:1px solid #164f78;border-radius:10px;text-align:center;padding:8px;font-weight:850;line-height:1.05}.date-block small{font-size:9px;color:#9dbfff}.ename{font-size:13px;font-weight:850;color:#fff;margin-top:3px}.eloc{font-size:11px;color:#8499ad;margin-top:4px}.period{color:#20e6ff;font-size:10px;margin-top:4px}.cal-legend{font-size:10px;color:#8499ad}.cal-dot{display:inline-block;width:6px;height:6px;background:#00d9ff;border-radius:50%;box-shadow:0 0 7px #00d9ff;margin-right:5px}
[data-testid="stTextInput"] label p,[data-testid="stSelectbox"] label p,[data-testid="stTextArea"] label p{color:#c4d1df!important;font-weight:700!important}.stTextInput input,.stTextArea textarea{background:#10263b!important;color:#f5f8fc!important;border-color:#245779!important}.stSelectbox [data-baseweb="select"]>div{background:#10263b!important;color:#f5f8fc!important;border-color:#245779!important}
@media(max-width:700px){.cal-wrap{grid-template-columns:1fr}.day{height:38px}.week,.days{gap:4px}}
</style>''', unsafe_allow_html=True)

st.title('Calendário de Eventos')
st.caption('Agenda oficial de treinos, campeonatos, viagens e reuniões do time.')

def parse_br(v): return datetime.strptime(v.strip(), '%d/%m/%Y').date()

st.markdown("<div class='cal-form'><b style='font-size:16px;color:#fff'>＋ Adicionar evento</b><div style='font-size:11px;color:#8499ad;margin-top:3px'>Cadastre o período completo do evento.</div></div>",unsafe_allow_html=True)
with st.form('ev', clear_on_submit=False):
    title = st.text_input('Evento', placeholder='Ex.: Mundial de Skate')
    a,b = st.columns(2)
    start_text = a.text_input('Data inicial', value=date.today().strftime('%d/%m/%Y'), placeholder='DD/MM/AAAA')
    end_text = b.text_input('Data final', value=date.today().strftime('%d/%m/%Y'), placeholder='DD/MM/AAAA')
    c,d = st.columns(2); loc=c.text_input('Local'); kind=d.selectbox('Tipo',['Treino','Campeonato','Viagem','Reunião','Outro'])
    notes=st.text_area('Observações',height=90)
    ok=st.form_submit_button('Adicionar evento',width='stretch',type='primary')
if ok:
    try:
        dt,end_dt=parse_br(start_text),parse_br(end_text)
        if not title.strip(): st.error('Digite o nome do evento.')
        elif end_dt<dt: st.error('A data final não pode ser anterior à data inicial.')
        else:
            sb.table('calendar_events').insert({'title':title.strip(),'event_date':dt.isoformat(),'event_end_date':end_dt.isoformat(),'location':loc.strip() or None,'event_type':kind,'notes':notes.strip() or None,'created_by':user.id}).execute(); st.success('Evento adicionado.'); st.rerun()
    except ValueError: st.error('Use as datas no formato DD/MM/AAAA.')

try: events=sb.table('calendar_events').select('*').order('event_date').execute().data or []
except Exception as e: events=[]; st.warning(f'Calendário ainda não disponível: {e}')

today=date.today(); month_names=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
if 'cal_month' not in st.session_state: st.session_state.cal_month=today.replace(day=1)
nav1,nav2,nav3=st.columns([1,5,1])
if nav1.button('‹',key='cal_prev',width='stretch'):
    cur=st.session_state.cal_month; st.session_state.cal_month=(cur.replace(day=1)-timedelta(days=1)).replace(day=1); st.rerun()
nav2.markdown(f"<div style='text-align:center;font-weight:900;font-size:18px;padding:7px'>{month_names[st.session_state.cal_month.month-1]} {st.session_state.cal_month.year}</div>",unsafe_allow_html=True)
if nav3.button('›',key='cal_next',width='stretch'):
    cur=st.session_state.cal_month; st.session_state.cal_month=(cur.replace(day=28)+timedelta(days=5)).replace(day=1); st.rerun()
y,m=st.session_state.cal_month.year,st.session_state.cal_month.month
eds=set()
for e in events:
    try:
        d0=date.fromisoformat(str(e.get('event_date'))); d1=date.fromisoformat(str(e.get('event_end_date') or e.get('event_date')))
        while d0<=d1: eds.add(d0.isoformat()); d0+=timedelta(days=1)
    except: pass
weeks=calendar.Calendar(firstweekday=6).monthdayscalendar(y,m)
ch=f"<div class='cal-card'><div class='cal-head'><span>Calendário</span><span class='cal-legend'><i class='cal-dot'></i>evento</span></div><div class='week'>"+''.join(f'<div>{x}</div>' for x in ['D','S','T','Q','Q','S','S'])+'</div><div class="days">'
for w in weeks:
    for d in w:
        if not d: ch+='<div class="day"></div>'; continue
        iso=f'{y:04d}-{m:02d}-{d:02d}'; cl='day'+(' today' if iso==today.isoformat() else '')+(' event' if iso in eds else ''); ch+=f"<div class='{cl}'>{d}</div>"
ch+='</div></div>'
future=[e for e in events if str(e.get('event_end_date') or e.get('event_date',''))>=today.isoformat()][:10]
eh="<div class='events-card'><div style='font-weight:850;margin-bottom:5px'>Próximos eventos</div>"
for e in future:
    try: d0=date.fromisoformat(e['event_date']); d1=date.fromisoformat(e.get('event_end_date') or e['event_date']); db=f"{d0.day:02d}<br><small>{month_names[d0.month-1][:3].upper()}</small>"
    except: d0=d1=today; db='—'
    period=d0.strftime('%d/%m/%Y') if d0==d1 else f"{d0.strftime('%d/%m')} → {d1.strftime('%d/%m/%Y')}"
    eh+=f"<div class='event-row'><div class='date-block'>{db}</div><div><div class='ename'>{html.escape(e.get('title') or 'Evento')}</div><div class='eloc'>{html.escape(e.get('location') or 'Local não informado')} • {html.escape(e.get('event_type') or '')}</div><div class='period'>{period}</div></div></div>"
if not future: eh+="<div class='eloc'>Nenhum próximo evento cadastrado.</div>"
eh+='</div>'; st.markdown(f"<div class='cal-wrap'>{ch}{eh}</div>",unsafe_allow_html=True)
