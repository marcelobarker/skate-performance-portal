from datetime import date,datetime
import calendar,html
import streamlit as st
from auth_utils import require_login,get_supabase
from ui_theme import apply_ui_theme
st.set_page_config(page_title='Calendário • Skate Performance',page_icon='📅',layout='wide');apply_ui_theme();user,profile=require_login();sb=get_supabase()
st.markdown('''<style>.cal-wrap{display:grid;grid-template-columns:1fr 1.05fr;gap:12px}.cal-card,.events-card{background:#061725;border:1px solid rgba(50,130,190,.30);border-radius:10px;padding:14px;box-shadow:0 8px 24px #0005}.cal-head{display:flex;justify-content:space-between;align-items:center;font-weight:800;margin-bottom:12px}.week,.days{display:grid;grid-template-columns:repeat(7,1fr);text-align:center;gap:4px}.week div{font-size:10px;color:#8499ad;padding:4px}.day{height:34px;display:grid;place-items:center;border-radius:50%;font-size:12px;color:#eaf3fa}.day.today{background:#087cff;color:#fff;box-shadow:0 0 12px #087cff80}.day.event{border:1px solid #00d9ff;color:#20e6ff}.event-row{display:grid;grid-template-columns:62px 1fr;gap:10px;padding:8px 0;border-bottom:1px solid #163b5940}.event-row:last-child{border:0}.date-block{background:#0a2945;border-radius:6px;text-align:center;padding:6px;font-weight:800;line-height:1.05}.date-block small{font-size:10px;color:#9dbfff}.ename{font-size:12px;font-weight:800;color:#fff;margin-top:3px}.eloc{font-size:11px;color:#8499ad;margin-top:3px}@media(max-width:700px){.cal-wrap{grid-template-columns:1fr}.day{height:31px}}</style>''',unsafe_allow_html=True)
st.title('Calendário de Eventos')
with st.expander('＋ Adicionar evento'):
    with st.form('ev'):
        a,b=st.columns([2,1]);title=a.text_input('Evento');dt=b.date_input('Data',value=date.today(),format='DD/MM/YYYY');c,d=st.columns(2);loc=c.text_input('Local');kind=d.selectbox('Tipo',['Treino','Campeonato','Viagem','Reunião','Outro']);notes=st.text_area('Observações');ok=st.form_submit_button('Adicionar evento',use_container_width=True)
    if ok and title.strip(): sb.table('calendar_events').insert({'title':title.strip(),'event_date':dt.isoformat(),'location':loc.strip() or None,'event_type':kind,'notes':notes.strip() or None,'created_by':user.id}).execute();st.rerun()
try: events=sb.table('calendar_events').select('*').order('event_date').execute().data or []
except Exception as e: events=[];st.warning(f'Calendário ainda não disponível: {e}')
today=date.today();month_names=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']; sel=st.selectbox('Mês',list(range(1,13)),index=today.month-1,format_func=lambda x:f'{month_names[x-1]} {today.year}',label_visibility='collapsed');m=sel;y=today.year
eds={str(e.get('event_date')) for e in events}; cal=calendar.Calendar(firstweekday=6); weeks=cal.monthdayscalendar(y,m)
ch=f"<div class='cal-card'><div class='cal-head'><span>‹</span><span>{month_names[m-1]} {y}</span><span>›</span></div><div class='week'>"+''.join(f'<div>{x}</div>' for x in ['D','S','T','Q','Q','S','S'])+'</div><div class="days">'
for w in weeks:
    for d in w:
        if d==0: ch+='<div class="day"></div>';continue
        iso=f'{y:04d}-{m:02d}-{d:02d}';cl='day'+(' today' if iso==today.isoformat() else '')+(' event' if iso in eds and iso!=today.isoformat() else '');ch+=f"<div class='{cl}'>{d}</div>"
ch+='</div></div>'
future=[e for e in events if str(e.get('event_date',''))>=today.isoformat()][:8]; eh="<div class='events-card'><div style='font-weight:800;margin-bottom:4px'>Próximos eventos</div>"
for e in future:
    try:d=datetime.strptime(e['event_date'],'%Y-%m-%d');db=f"{d.day:02d}<br><small>{month_names[d.month-1][:3].upper()}</small>"
    except:db='—'
    eh+=f"<div class='event-row'><div class='date-block'>{db}</div><div><div class='ename'>{html.escape(e.get('title') or 'Evento')}</div><div class='eloc'>{html.escape(e.get('location') or 'Local não informado')}</div></div></div>"
if not future:eh+="<div class='eloc'>Nenhum próximo evento cadastrado.</div>"
eh+='</div>';st.markdown(f"<div class='cal-wrap'>{ch}{eh}</div>",unsafe_allow_html=True)
