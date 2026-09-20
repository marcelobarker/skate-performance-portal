from datetime import date, datetime
import calendar
import streamlit as st
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme

st.set_page_config(page_title='Calendário • Skate Performance', page_icon='📅', layout='wide')
apply_ui_theme()
user, profile = require_login(); sb=get_supabase()
st.title('📅 Calendário de Eventos')
st.caption('Treinos, campeonatos, viagens e compromissos da equipe.')

with st.expander('＋ Adicionar evento', expanded=False):
    with st.form('event_form'):
        c1,c2=st.columns([2,1]); title=c1.text_input('Evento'); event_date=c2.date_input('Data', value=date.today(), format='DD/MM/YYYY')
        c3,c4=st.columns(2); location=c3.text_input('Local'); kind=c4.selectbox('Tipo',['Treino','Campeonato','Viagem','Reunião','Outro'])
        notes=st.text_area('Observações')
        add=st.form_submit_button('Adicionar evento',use_container_width=True)
    if add and title.strip():
        try:
            sb.table('calendar_events').insert({'title':title.strip(),'event_date':event_date.isoformat(),'location':location.strip() or None,'event_type':kind,'notes':notes.strip() or None,'created_by':user.id}).execute()
            st.success('Evento adicionado.'); st.rerun()
        except Exception as e: st.error(f'Não foi possível adicionar: {e}')

try: events=sb.table('calendar_events').select('*').order('event_date').execute().data or []
except Exception as e: events=[]; st.warning(f'Calendário ainda não disponível: {e}')

today=date.today(); month=st.selectbox('Mês',[f'{m:02d}/{today.year}' for m in range(1,13)],index=today.month-1)
m,y=map(int,month.split('/'))
month_events=[e for e in events if str(e.get('event_date','')).startswith(f'{y:04d}-{m:02d}')]
st.markdown("<div style='background:#0b1d31;border:1px solid #245274;border-radius:18px;padding:18px'>",unsafe_allow_html=True)
st.markdown(f'### {calendar.month_name[m]} {y}')
weeks=calendar.monthcalendar(y,m)
heads=st.columns(7)
for c,n in zip(heads,['SEG','TER','QUA','QUI','SEX','SÁB','DOM']): c.markdown(f'**{n}**')
for week in weeks:
    cols=st.columns(7)
    for col,d in zip(cols,week):
        if not d: col.markdown('&nbsp;',unsafe_allow_html=True); continue
        has=[e for e in month_events if int(str(e['event_date'])[-2:])==d]
        badge=' 🔵' if has else ''
        col.markdown(f"<div style='min-height:58px;background:#091827;border:1px solid #173b5a;border-radius:10px;padding:8px'><b>{d}</b>{badge}</div>",unsafe_allow_html=True)
st.markdown('</div>',unsafe_allow_html=True)
st.markdown('### Próximos eventos')
future=[e for e in events if str(e.get('event_date','')) >= today.isoformat()][:12]
if not future: st.info('Nenhum evento futuro cadastrado.')
for e in future:
    dt=datetime.strptime(e['event_date'],'%Y-%m-%d').strftime('%d/%m/%Y')
    st.markdown(f"<div style='background:#0b1d31;border:1px solid #173b5a;border-radius:14px;padding:14px;margin:8px 0'><b style='color:#eef8ff'>{dt} • {e.get('title','')}</b><div style='color:#9bb2c8'>{e.get('event_type','')} {'• '+e.get('location') if e.get('location') else ''}</div></div>",unsafe_allow_html=True)
