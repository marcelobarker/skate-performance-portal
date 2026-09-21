import streamlit as st
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme
st.set_page_config(page_title="Central do Treinador • Skate Performance",page_icon="⌁",layout="wide")
apply_ui_theme(); user,me=require_login(); sb=get_supabase()
if me.get('role') in ('skatista','familiar'):
    st.error('Área da comissão técnica.'); st.stop()
st.markdown('''<style>
.work-title{font-size:34px;font-weight:950}.work-sub{color:#8499ad;margin-bottom:18px}.work-card{min-height:150px;border:1px solid #16496e;border-radius:16px;padding:18px;background:radial-gradient(circle at 90% 10%,#087cff25,transparent 35%),linear-gradient(145deg,#081b2d,#061727);box-shadow:0 0 24px #087cff12}.work-icon{font-size:28px;color:#20e6ff}.work-name{font-size:18px;font-weight:900;margin-top:12px}.work-desc{color:#8499ad;font-size:12px;margin-top:6px}
</style>''',unsafe_allow_html=True)
st.markdown("<div class='work-title'>Central de Performance</div><div class='work-sub'>Ferramentas de trabalho da comissão técnica em um único lugar.</div>",unsafe_allow_html=True)
c1,c2,c3=st.columns(3)
with c1:
    st.markdown("<div class='work-card'><div class='work-icon'>◉</div><div class='work-name'>Análise de treino</div><div class='work-desc'>CSV, dashboard completo, gráficos e relatórios.</div></div>",unsafe_allow_html=True)
    st.page_link('pages/03_Analise_de_Treino.py',label='ABRIR ANÁLISE',use_container_width=True)
with c2:
    st.markdown("<div class='work-card'><div class='work-icon'>▦</div><div class='work-name'>Livro de manobras</div><div class='work-desc'>Categorias, manobras e organização da biblioteca.</div></div>",unsafe_allow_html=True)
    st.page_link('pages/08_Livro_de_Manobras.py',label='ABRIR LIVRO',use_container_width=True)
with c3:
    if me.get('role')=='admin':
        st.markdown("<div class='work-card'><div class='work-icon'>▶</div><div class='work-name'>Codificação de vídeo</div><div class='work-desc'>Ferramenta experimental de video coding. Visível somente para Admin.</div></div>",unsafe_allow_html=True)
        st.page_link('pages/03_Analise_de_Treino.py',label='ABRIR CODIFICAÇÃO',use_container_width=True)
    else:
        st.markdown("<div class='work-card'><div class='work-icon'>＋</div><div class='work-name'>Enviar vídeo</div><div class='work-desc'>Envie sessões e tentativas para o feed dos atletas.</div></div>",unsafe_allow_html=True)
        st.page_link('pages/09_Enviar_Manobra.py',label='ENVIAR VÍDEO',use_container_width=True)
