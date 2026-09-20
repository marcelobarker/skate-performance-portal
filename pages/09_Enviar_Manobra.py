import uuid, mimetypes
import streamlit as st
from auth_utils import require_login,get_supabase
from ui_theme import apply_ui_theme
st.set_page_config(page_title='Enviar Manobra • Skate Performance',page_icon='🎥',layout='wide'); apply_ui_theme(); user,profile=require_login(); sb=get_supabase()
st.title('🎥 Enviar Manobra'); st.caption('Escolha a manobra, grave ou selecione o vídeo no celular e envie para análise.')
if profile.get('role')!='skatista': st.info('O envio direto é destinado aos atletas. Staff pode acompanhar os vídeos pelo perfil dos atletas.'); st.stop()
try: cats=sb.table('trick_categories').select('*').order('sort_order').execute().data or []; tricks=sb.table('tricks').select('*').eq('active',True).order('name').execute().data or []
except Exception as e: st.error(f'Execute a migration V3.2 primeiro. Detalhes: {e}'); st.stop()
if not tricks: st.warning('O Livro de Manobras ainda está vazio.'); st.page_link('pages/08_Livro_de_Manobras.py',label='Abrir Livro de Manobras'); st.stop()
cmap={c['name']:c['id'] for c in cats}; cat=st.selectbox('Categoria',list(cmap)); available=[t for t in tricks if t.get('category_id')==cmap[cat]]; tmap={t['name']:t['id'] for t in available}; trick=st.selectbox('Manobra',list(tmap)) if tmap else None
video=st.file_uploader('Vídeo da tentativa',type=['mp4','mov','webm'],help='No celular você pode gravar o vídeo e selecionar aqui. Limite recomendado: 150 MB.')
caption=st.text_area('Legenda / observação',placeholder='Ex.: tentando melhorar a saída do corrimão…',height=90)
if st.button('Enviar para análise',type='primary',width='stretch',disabled=not(video and trick)):
    if video.size>150*1024*1024: st.error('O vídeo ultrapassa 150 MB.')
    else:
        ext=video.name.rsplit('.',1)[-1].lower() if '.' in video.name else 'mp4'; path=f'{user.id}/{uuid.uuid4().hex}.{ext}'; ct=video.type or mimetypes.guess_type(video.name)[0] or 'video/mp4'
        try:
            sb.storage.from_('trick-videos').upload(path,video.getvalue(),{'content-type':ct,'upsert':'false'})
            sb.table('athlete_posts').insert({'athlete_id':user.id,'trick_id':tmap[trick],'video_path':path,'caption':caption.strip() or None}).execute(); st.success('Vídeo enviado! Ele já está no seu feed e aguardando análise.'); st.session_state['selected_athlete_id']=user.id; st.switch_page('pages/07_Perfil_do_Atleta.py')
        except Exception as e: st.error(f'Não foi possível enviar: {e}')
