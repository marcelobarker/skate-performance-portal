import html
from datetime import datetime,date
import streamlit as st
from auth_utils import require_login,get_supabase
from ui_theme import apply_ui_theme
st.set_page_config(page_title='Perfil do Atleta • Skate Performance',page_icon='🛹',layout='wide'); apply_ui_theme(); user,me=require_login(); sb=get_supabase()
athlete_id=st.session_state.get('selected_athlete_id') or (user.id if me.get('role')=='skatista' else None)
if not athlete_id: st.info('Selecione um atleta na página Times para abrir o feed.'); st.page_link('pages/02_Times.py',label='Abrir Times'); st.stop()
try: athlete=sb.table('profiles').select('*').eq('id',athlete_id).single().execute().data
except Exception as e: st.error(f'Atleta não encontrado: {e}'); st.stop()
if athlete.get('role')!='skatista': st.warning('Este perfil não é de atleta.'); st.stop()
photo=athlete.get('photo_url'); loc=' / '.join(x for x in [athlete.get('city'),athlete.get('state')] if x) or '—'
st.markdown('''<style>.ath-hero{background:radial-gradient(circle at 80% 10%,#087cff35,transparent 30%),linear-gradient(145deg,#0a2137,#03101c);border:1px solid #174b70;border-radius:16px;padding:20px;display:flex;gap:20px;align-items:center;margin-bottom:16px}.ath-photo{width:118px;height:118px;border-radius:14px;object-fit:cover;border:1px solid #29a8ff}.ath-ph{width:118px;height:118px;border-radius:14px;display:grid;place-items:center;background:#0a2945;font-size:42px}.ath-name{font-size:28px;font-weight:900;color:#fff}.ath-meta{color:#9bb2c7;margin-top:6px}.status{display:inline-block;padding:4px 9px;border-radius:99px;background:#087cff22;border:1px solid #087cff66;color:#29a8ff;font-size:10px;font-weight:800}.post-head{display:flex;gap:10px;align-items:center}.mini{width:38px;height:38px;border-radius:50%;object-fit:cover}.comment{background:#071827;border:1px solid #153b58;border-radius:9px;padding:8px 10px;margin:5px 0;color:#c4d1df;font-size:12px}@media(max-width:600px){.ath-hero{align-items:flex-start}.ath-photo,.ath-ph{width:84px;height:84px}.ath-name{font-size:22px}}</style>''',unsafe_allow_html=True)
pic=f"<img class='ath-photo' src='{html.escape(photo)}'>" if photo else "<div class='ath-ph'>🛹</div>"
st.markdown(f"<div class='ath-hero'>{pic}<div><div class='ath-name'>{html.escape(athlete.get('full_name') or 'Atleta')}</div><div class='ath-meta'>{html.escape(athlete.get('modality') or '—')} • {html.escape(athlete.get('stance') or '—')} • {html.escape(loc)}</div><div style='margin-top:10px'><span class='status'>FEED DO ATLETA</span></div></div></div>",unsafe_allow_html=True)
if athlete_id==user.id: st.page_link('pages/09_Enviar_Manobra.py',label='🎥 Enviar nova manobra',use_container_width=True)
try:
    posts=sb.table('athlete_posts').select('*').eq('athlete_id',athlete_id).order('created_at',desc=True).execute().data or []; tricks=sb.table('tricks').select('id,name').execute().data or []; tnames={x['id']:x['name'] for x in tricks}
except Exception as e: st.error(f'Feed ainda não disponível. Execute a migration V3.2. Detalhes: {e}'); st.stop()
if not posts: st.info('Nenhum vídeo publicado ainda. Quando o atleta enviar uma manobra, ela aparecerá aqui.')
for post in posts:
    with st.container(border=True):
        st.markdown(f"<div class='post-head'>{('<img class=mini src='+repr(photo)+'>') if photo else '🛹'}<div><b>{html.escape(athlete.get('full_name') or 'Atleta')}</b><br><span class='status'>{html.escape(tnames.get(post.get('trick_id'),'MANOBRA'))}</span> <span class='status'>{html.escape((post.get('analysis_status') or 'aguardando').upper())}</span></div></div>",unsafe_allow_html=True)
        if post.get('caption'): st.write(post['caption'])
        try:
            signed=sb.storage.from_('trick-videos').create_signed_url(post['video_path'],3600); url=signed.get('signedURL') or signed.get('signedUrl') or signed.get('signed_url'); st.video(url)
        except Exception: st.caption('Vídeo privado indisponível temporariamente.')
        likes=sb.table('post_likes').select('user_id').eq('post_id',post['id']).execute().data or []; mine=any(x['user_id']==user.id for x in likes)
        c1,c2=st.columns([1,5])
        if c1.button(('♥' if mine else '♡')+f' {len(likes)}',key='like_'+post['id'],width='stretch'):
            if mine: sb.table('post_likes').delete().eq('post_id',post['id']).eq('user_id',user.id).execute()
            else: sb.table('post_likes').insert({'post_id':post['id'],'user_id':user.id}).execute()
            st.rerun()
        comments=sb.table('post_comments').select('*').eq('post_id',post['id']).order('created_at').execute().data or []
        uids=list({x['user_id'] for x in comments}); names={}
        if uids:
            try:
                pp=sb.table('profiles').select('id,full_name').in_('id',uids).execute().data or []; names={x['id']:x.get('full_name') for x in pp}
            except: pass
        for cm in comments: st.markdown(f"<div class='comment'><b>{html.escape(names.get(cm['user_id']) or 'Membro')}</b> &nbsp; {html.escape(cm.get('body') or '')}</div>",unsafe_allow_html=True)
        with st.form('comment_'+post['id'],clear_on_submit=True):
            txt=st.text_input('Comentar',placeholder='Escreva um comentário…',label_visibility='collapsed'); send=st.form_submit_button('Comentar')
        if send and txt.strip(): sb.table('post_comments').insert({'post_id':post['id'],'user_id':user.id,'body':txt.strip()}).execute(); st.rerun()
