import html
import streamlit as st
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme
from drive_utils import is_drive_path, drive_stream_url, drive_preview_url
try:
    from drive_utils import drive_player_geometry
except ImportError:
    def drive_player_geometry(path_or_id):
        return {'max_width':525,'aspect':'16/9','orientation':'unknown'}
from video_utils import can_delete_post, delete_video_post

st.set_page_config(initial_sidebar_state="collapsed", page_title="Feed • Skate Performance", page_icon="▶", layout="wide")
apply_ui_theme(); user, me = require_login(); sb=get_supabase()
st.markdown('''<style>
.feed-head{font-size:32px;font-weight:950;color:#f5f8fc}.feed-sub{color:#8499ad;margin-bottom:18px}
.feed-card{max-width:680px;margin:0 auto}.feed-video{max-width:460px;margin:12px auto}.feed-video [data-testid="stVideo"]{max-width:460px!important;width:100%!important}.feed-video video{max-height:520px!important;object-fit:contain!important}
.post-title{font-weight:900;font-size:17px}.pill{display:inline-block;padding:3px 8px;border:1px solid #087cff66;background:#087cff18;color:#29a8ff;border-radius:999px;font-size:10px;font-weight:800}
@media(max-width:700px){.feed-video,.feed-video [data-testid="stVideo"]{max-width:100%!important}.feed-card{max-width:100%}}
</style>''',unsafe_allow_html=True)
st.markdown("<div class='feed-head'>Feed da equipe</div><div class='feed-sub'>Últimos vídeos enviados pelos atletas.</div>",unsafe_allow_html=True)
try:
    posts=sb.table('athlete_posts').select('*').order('created_at',desc=True).limit(60).execute().data or []
    ids=list({p.get('athlete_id') for p in posts if p.get('athlete_id')})
    profs=sb.table('profiles').select('id,full_name,photo_url,modality').in_('id',ids).execute().data if ids else []
    pm={p['id']:p for p in (profs or [])}
except Exception as e:
    st.error(f"Não foi possível carregar o feed: {e}"); st.stop()
if not posts: st.info("Ainda não há vídeos no feed."); st.stop()
for post in posts:
    a=pm.get(post.get('athlete_id'),{}); name=a.get('full_name') or 'Atleta'
    with st.container(border=True):
        photo=a.get('photo_url')
        if photo:
            st.markdown(
                f"""<div style='display:flex;align-items:center;gap:11px;margin-bottom:5px'>
                <img src='{html.escape(photo, quote=True)}'
                     style='width:46px;height:46px;border-radius:50%;object-fit:cover;border:1px solid #163b59'>
                <div><div class='post-title'>{html.escape(name)}</div>
                <span class='pill'>{html.escape(post.get('session_title') or 'VÍDEO DE TREINO')}</span></div>
                </div>""",
                unsafe_allow_html=True
            )
        else:
            initials=''.join(x[0].upper() for x in name.split()[:2]) or 'A'
            st.markdown(
                f"""<div style='display:flex;align-items:center;gap:11px;margin-bottom:5px'>
                <div style='width:46px;height:46px;border-radius:50%;display:flex;align-items:center;
                            justify-content:center;background:#0b2136;border:1px solid #163b59;
                            color:#20e6ff;font-weight:900'>{html.escape(initials)}</div>
                <div><div class='post-title'>{html.escape(name)}</div>
                <span class='pill'>{html.escape(post.get('session_title') or 'VÍDEO DE TREINO')}</span></div>
                </div>""",
                unsafe_allow_html=True
            )
        if post.get('caption'): st.caption(post['caption'])
        try:
            if is_drive_path(post.get('video_path')):
                # No feed usamos o player nativo do Google Drive: ele reproduz o mesmo
                # arquivo que já funciona no Drive e não depende do endpoint de download.
                preview=drive_preview_url(post['video_path'])
                geo=drive_player_geometry(post['video_path'])
                st.markdown(f"""<div style='width:min(100%,{geo["max_width"]}px);margin:12px auto;border-radius:14px;overflow:hidden;background:#020b14;aspect-ratio:{geo["aspect"]};border:1px solid #163b59'>
                <iframe src='{preview}' style='width:100%;height:100%;border:0;display:block' allow='autoplay; fullscreen' allowfullscreen></iframe>
                </div>""",unsafe_allow_html=True)
            else:
                signed=sb.storage.from_('trick-videos').create_signed_url(post['video_path'],3600); url=signed.get('signedURL') or signed.get('signedUrl') or signed.get('signed_url')
                st.markdown("<div class='feed-video'>",unsafe_allow_html=True); st.video(url); st.markdown("</div>",unsafe_allow_html=True)
        except Exception: st.caption("Vídeo indisponível temporariamente.")
        if can_delete_post(me, user.id, post):
            if st.button('🗑 Excluir vídeo', key='del_feed_'+post['id'], use_container_width=False):
                try:
                    delete_video_post(sb,post); st.success('Vídeo excluído.'); st.rerun()
                except Exception as e:
                    st.error(f'Não foi possível excluir o vídeo. Detalhes: {e}')
        c1,c2=st.columns([1,5]); likes=sb.table('post_likes').select('user_id').eq('post_id',post['id']).execute().data or []; mine=any(x['user_id']==user.id for x in likes)
        if c1.button(('♥' if mine else '♡')+f' {len(likes)}',key='feed_like_'+post['id'],use_container_width=True):
            if mine: sb.table('post_likes').delete().eq('post_id',post['id']).eq('user_id',user.id).execute()
            else: sb.table('post_likes').insert({'post_id':post['id'],'user_id':user.id}).execute()
            st.rerun()
        if c2.button('Ver perfil e comentários',key='feed_open_'+post['id'],use_container_width=True):
            st.session_state['selected_athlete_id']=post['athlete_id']; st.switch_page('pages/07_Perfil_do_Atleta.py')
