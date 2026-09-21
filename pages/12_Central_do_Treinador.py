import streamlit as st
from auth_utils import require_login
from ui_theme import apply_ui_theme
st.set_page_config(page_title='Central de Performance • Skate Performance',page_icon='⚡',layout='wide')
apply_ui_theme(); user,me=require_login()
if me.get('role') in ('skatista','familiar'):
    st.error('Área da comissão técnica.'); st.stop()
st.markdown('''<style>
.work-title{font-size:36px;font-weight:950;color:#10263b}.work-sub{color:#71879b;margin-bottom:22px}
.work-card{min-height:168px;border:1px solid #cce5f7;border-radius:18px;padding:20px;background:radial-gradient(circle at 92% 8%,rgba(8,124,255,.12),transparent 36%),linear-gradient(145deg,#fff,#f7fbff);box-shadow:0 12px 32px rgba(31,78,116,.08),0 0 22px rgba(8,124,255,.06);transition:.18s}.work-icon{font-size:31px;color:#087cff}.work-name{font-size:20px;font-weight:950;color:#10263b;margin-top:14px}.work-desc{color:#71879b;font-size:13px;margin-top:7px}
[class*='st-key-work_']{margin-top:-168px!important;height:168px!important;position:relative!important;z-index:20!important}[class*='st-key-work_'] [data-testid='stButton']{height:100%!important}[class*='st-key-work_'] button{height:168px!important;width:100%!important;opacity:0!important;border:0!important;background:transparent!important;box-shadow:none!important;font-size:0!important;padding:0!important}
</style>''',unsafe_allow_html=True)
st.markdown("<div class='work-title'>Central de Performance</div><div class='work-sub'>Seu espaço de trabalho para análise, biblioteca e vídeo.</div>",unsafe_allow_html=True)
items=[('◉','Análise de treino','CSV, dashboard completo, gráficos e relatórios.','pages/03_Analise_de_Treino.py','analysis'),('▦','Livro de manobras','Categorias, manobras e organização da biblioteca.','pages/08_Livro_de_Manobras.py','book')]
if me.get('role')=='admin': items.append(('▶','Codificação de vídeo','Video coding experimental com marcações e análise.','pages/10_Codificar_Sessao.py','coding'))
else: items.append(('＋','Enviar vídeo','Envie sessões e tentativas para o feed dos atletas.','pages/09_Enviar_Manobra.py','upload'))
cols=st.columns(3,gap='medium')
for col,(ic,name,desc,page,key) in zip(cols,items):
    with col:
        st.markdown(f"<div class='work-card'><div class='work-icon'>{ic}</div><div class='work-name'>{name}</div><div class='work-desc'>{desc}</div></div>",unsafe_allow_html=True)
        if st.button('abrir',key='work_'+key,use_container_width=True): st.switch_page(page)
