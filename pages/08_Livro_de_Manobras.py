import streamlit as st
from auth_utils import require_login,get_supabase
from ui_theme import apply_ui_theme
st.set_page_config(page_title='Livro de Manobras • Skate Performance',page_icon='📚',layout='wide'); apply_ui_theme(); user,profile=require_login(); sb=get_supabase()
STAFF={'admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica'}; can_edit=profile.get('role') in STAFF
st.title('📚 Livro de Manobras'); st.caption('Biblioteca oficial usada pelos atletas ao enviar vídeos para análise.')
try: cats=sb.table('trick_categories').select('*').order('sort_order').execute().data or []; tricks=sb.table('tricks').select('*').eq('active',True).order('name').execute().data or []
except Exception as e: st.error(f'Execute a migration V3.2 no Supabase para ativar o Livro de Manobras. Detalhes: {e}'); st.stop()
if can_edit:
    with st.expander('＋ Cadastrar categoria ou manobra'):
        t1,t2=st.tabs(['Nova manobra','Nova categoria'])
        with t1:
            with st.form('new_trick'):
                cmap={c['name']:c['id'] for c in cats}; cn=st.selectbox('Categoria',list(cmap)); name=st.text_input('Nome da manobra'); desc=st.text_area('Descrição / observação',height=80); ok=st.form_submit_button('Adicionar manobra',type='primary',width='stretch')
            if ok and name.strip(): sb.table('tricks').insert({'category_id':cmap[cn],'name':name.strip(),'description':desc.strip() or None,'created_by':user.id}).execute(); st.rerun()
        with t2:
            with st.form('new_cat'):
                cname=st.text_input('Nome da categoria'); order=st.number_input('Ordem',0,999,100); ok2=st.form_submit_button('Adicionar categoria',width='stretch')
            if ok2 and cname.strip(): sb.table('trick_categories').insert({'name':cname.strip(),'sort_order':int(order)}).execute(); st.rerun()
if not cats: st.info('Nenhuma categoria cadastrada.'); st.stop()
tabs=st.tabs([c['name'] for c in cats])
for tab,c in zip(tabs,cats):
    with tab:
        group=[t for t in tricks if t.get('category_id')==c['id']]
        if not group: st.caption('Nenhuma manobra nesta categoria.')
        cols=st.columns(3)
        for i,t in enumerate(group):
            with cols[i%3]:
                with st.container(border=True):
                    st.markdown(f"### {t['name']}"); st.caption(t.get('description') or 'Pronta para selecionar no envio de vídeo.')
                    if can_edit and st.button('Desativar',key='off_'+t['id'],width='stretch'):
                        sb.table('tricks').update({'active':False}).eq('id',t['id']).execute(); st.rerun()
