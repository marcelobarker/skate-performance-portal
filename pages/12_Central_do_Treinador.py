import streamlit as st
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme
from portal_layout import render_new_shell, page_head
st.set_page_config(initial_sidebar_state="collapsed", page_title="Central do Treinador • Skate Performance",page_icon="⌁",layout="wide")
apply_ui_theme(); user,me=require_login(); sb=get_supabase()
render_new_shell(me,user,active="Central do Treinador")
# V4.43: acesso temporariamente liberado.
st.markdown('''<style>
.work-title{font-size:34px;font-weight:950}.work-sub{color:#8499ad;margin-bottom:18px}.work-card{min-height:220px;border:1px solid #16496e;border-radius:16px;padding:26px;background:radial-gradient(circle at 90% 10%,#087cff25,transparent 35%),linear-gradient(145deg,#081b2d,#061727);box-shadow:0 0 24px #087cff12;transition:.18s}.work-card:hover{border-color:#20e6ff;box-shadow:0 0 30px #087cff28;transform:translateY(-2px)}.work-icon{font-size:36px;color:#20e6ff}.work-name{font-size:22px;font-weight:900;margin-top:12px}.work-desc{color:#8499ad;font-size:14px;margin-top:6px}
[class*='st-key-central_']{margin-top:-220px!important;height:220px!important;position:relative!important;z-index:30!important}[class*='st-key-central_'] [data-testid='stButton']{height:100%!important}[class*='st-key-central_'] button{height:220px!important;width:100%!important;opacity:0!important;border:0!important;background:transparent!important;box-shadow:none!important;font-size:0!important;padding:0!important}
</style>''',unsafe_allow_html=True)
page_head('TIME BRASIL • COACH HUB','Central de Performance','Ferramentas da comissão técnica organizadas em um único ambiente de trabalho.')
items=[('◉','Análise de treino','CSV, dashboard completo, gráficos e relatórios.','pages/03_Analise_de_Treino.py','analysis'),('▦','Livro de manobras','Categorias, manobras e organização da biblioteca.','pages/08_Livro_de_Manobras.py','book')]
items.append(('▶','Codificação de vídeo','Codificação e revisão de vídeo.','pages/10_Codificar_Sessao.py','coding'))
items.append(('＋','Enviar vídeo','Envie sessões e tentativas para o feed dos atletas.','pages/09_Enviar_Manobra.py','upload'))
for col,item in zip(st.columns(3),items):
    ic,name,desc,page,key=item
    with col:
        st.markdown(f"<div class='work-card'><div class='work-icon'>{ic}</div><div class='work-name'>{name}</div><div class='work-desc'>{desc}</div></div>",unsafe_allow_html=True)
        if st.button('abrir',key='central_'+key,use_container_width=True): st.switch_page(page)
