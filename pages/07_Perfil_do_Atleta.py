import html
from datetime import datetime,date
import streamlit as st
from auth_utils import require_login,get_supabase
from ui_theme import apply_ui_theme
from drive_utils import is_drive_path, drive_stream_url, drive_preview_url
try:
    from drive_utils import drive_player_geometry
except ImportError:
    def drive_player_geometry(path_or_id):
        return {'max_width':525,'aspect':'16/9','orientation':'unknown'}
from video_utils import can_delete_post, delete_video_post
st.set_page_config(initial_sidebar_state="collapsed", page_title='Perfil do Atleta • Skate Performance',page_icon='🛹',layout='wide'); apply_ui_theme(); user,me=require_login(); sb=get_supabase()
STAFF_ROLES=('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica')
is_staff=True
from portal_layout import render_new_shell
render_new_shell(me,user,active='Atletas')
athlete_id=st.session_state.get('selected_athlete_id') or (user.id if me.get('role')=='skatista' else None)

# Central de atletas — nova estrutura visual do portal.
if not athlete_id:
    st.markdown('''
    <style>
    .ath-page-head{padding:26px 4px 18px;border-bottom:1px solid rgba(73,168,255,.16);margin-bottom:18px}
    .ath-kicker{font-size:11px;letter-spacing:.18em;font-weight:900;color:#28d9ff;text-transform:uppercase;margin-bottom:7px}
    .ath-title{font-size:34px;line-height:1.05;font-weight:950;color:#f4f9ff;margin:0}
    .ath-sub{color:#86a2b9;font-size:14px;margin-top:8px;max-width:720px}
    .ath-stat{background:linear-gradient(145deg,rgba(8,31,51,.96),rgba(4,18,31,.96));border:1px solid rgba(64,151,220,.22);border-radius:16px;padding:16px 18px;min-height:92px;box-shadow:0 14px 34px rgba(0,0,0,.15)}
    .ath-stat-v{font-size:27px;font-weight:950;color:#f6fbff;line-height:1}.ath-stat-l{font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:#7895ac;margin-top:9px;font-weight:800}
    .ath-card{max-width:420px;background:linear-gradient(150deg,rgba(8,31,51,.98),rgba(3,16,28,.98));border:1px solid rgba(52,140,205,.24);border-radius:18px;padding:18px;min-height:350px;position:relative;overflow:hidden;box-shadow:0 16px 38px rgba(0,0,0,.18);transition:.2s ease}
    .ath-card:before{content:'';position:absolute;inset:-80px -70px auto auto;width:180px;height:180px;background:radial-gradient(circle,rgba(0,207,255,.13),transparent 68%);pointer-events:none}
    .ath-card:hover{border-color:rgba(40,217,255,.55);transform:translateY(-2px);box-shadow:0 18px 42px rgba(0,0,0,.26),0 0 28px rgba(0,194,255,.07)}
    .ath-card-photo{width:100%;height:220px;object-fit:cover;border-radius:13px;border:1px solid rgba(79,166,228,.22);background:#071725}
    .ath-card-ph{height:220px;border-radius:13px;border:1px solid rgba(79,166,228,.22);display:grid;place-items:center;background:radial-gradient(circle at 50% 30%,#123b5d,#071725 65%);font-size:46px}
    .ath-card-name{font-size:20px;font-weight:900;color:#f4f9ff;margin-top:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .ath-card-meta{font-size:13px;color:#7897af;margin-top:5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .ath-chip{display:inline-block;margin-top:10px;margin-right:5px;padding:4px 8px;border-radius:999px;background:rgba(23,160,220,.10);border:1px solid rgba(40,217,255,.20);font-size:9px;letter-spacing:.07em;text-transform:uppercase;font-weight:850;color:#63dff5}
    div[data-testid='stTextInput'] input,div[data-testid='stSelectbox']>div>div{background:#071a2b!important;border-color:#173e5d!important;color:#eaf6ff!important}
    div.stButton>button[kind='secondary']{border-radius:11px!important;background:linear-gradient(180deg,#0a2941,#071d30)!important;border:1px solid #1d557b!important;color:#d9efff!important;font-weight:800!important;min-height:39px!important}
    div.stButton>button[kind='secondary']:hover{border-color:#25c9ef!important;color:#fff!important;box-shadow:0 0 0 1px rgba(37,201,239,.12),0 0 20px rgba(0,193,255,.08)!important}
    </style>
    <div class='ath-page-head'><div class='ath-kicker'>Time Brasil • Performance Center</div><div class='ath-title'>Atletas</div><div class='ath-sub'>Perfis, modalidade, base e acesso rápido ao histórico e ao feed técnico de cada skatista.</div></div>
    ''', unsafe_allow_html=True)
    try:
        athletes=sb.table('profiles').select('*').eq('role','skatista').execute().data or []
    except Exception as e:
        st.error(f'Não foi possível carregar os atletas: {e}'); st.stop()
    active_ath=[a for a in athletes if str(a.get('status') or '').lower() in ('ativo','active','aprovado','approved','')]
    street=sum(1 for a in athletes if 'street' in str(a.get('modality') or '').lower())
    park=sum(1 for a in athletes if 'park' in str(a.get('modality') or '').lower())
    s1,s2,s3,s4=st.columns(4)
    for col,val,label in [(s1,len(athletes),'Atletas cadastrados'),(s2,len(active_ath),'Ativos'),(s3,street,'Street'),(s4,park,'Park')]:
        col.markdown(f"<div class='ath-stat'><div class='ath-stat-v'>{val}</div><div class='ath-stat-l'>{label}</div></div>",unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
    f1,f2=st.columns([2.2,1])
    search=f1.text_input('Buscar atleta',placeholder='Buscar por nome, cidade ou estado…',label_visibility='collapsed')
    mods=sorted({str(a.get('modality')).strip() for a in athletes if a.get('modality')})
    mod=f2.selectbox('Modalidade',['Todas']+mods,label_visibility='collapsed')
    q=search.strip().lower()
    filtered=[]
    for a in athletes:
        hay=' '.join(str(a.get(k) or '') for k in ('full_name','city','state','modality','stance')).lower()
        if q and q not in hay: continue
        if mod!='Todas' and str(a.get('modality') or '')!=mod: continue
        filtered.append(a)
    if not filtered:
        st.info('Nenhum atleta encontrado com esses filtros.')
    else:
        for start in range(0,len(filtered),4):
            cols=st.columns(3)
            for col,a in zip(cols,filtered[start:start+4]):
                aid=a.get('id'); name=a.get('full_name') or 'Atleta'; photo=a.get('photo_url'); city=' / '.join(x for x in [a.get('city'),a.get('state')] if x) or 'Local não informado'; modality=a.get('modality') or 'Modalidade —'; stance=a.get('stance') or 'Base —'
                pic=(f"<img class='ath-card-photo' src='{html.escape(str(photo), quote=True)}'>" if photo else "<div class='ath-card-ph'>🛹</div>")
                with col:
                    st.markdown(f"<div class='ath-card'>{pic}<div class='ath-card-name'>{html.escape(str(name))}</div><div class='ath-card-meta'>{html.escape(str(city))}</div><span class='ath-chip'>{html.escape(str(modality))}</span><span class='ath-chip'>{html.escape(str(stance))}</span></div>",unsafe_allow_html=True)
                    if st.button('Abrir perfil  →',key=f'open_ath_{aid}',use_container_width=True):
                        st.session_state['selected_athlete_id']=aid
                        st.rerun()
    st.stop()
try: athlete=sb.table('profiles').select('*').eq('id',athlete_id).single().execute().data
except Exception as e: st.error(f'Atleta não encontrado: {e}'); st.stop()
if athlete.get('role')!='skatista': st.warning('Este perfil não é de atleta.'); st.stop()
photo=athlete.get('photo_url'); loc=' / '.join(x for x in [athlete.get('city'),athlete.get('state')] if x) or '—'
st.markdown('''<style>.ath-hero{background:radial-gradient(circle at 80% 10%,#087cff35,transparent 30%),linear-gradient(145deg,#0a2137,#03101c);border:1px solid #174b70;border-radius:16px;padding:20px;display:flex;gap:20px;align-items:center;margin-bottom:16px}.ath-photo{width:118px;height:118px;border-radius:14px;object-fit:cover;border:1px solid #29a8ff}.ath-ph{width:118px;height:118px;border-radius:14px;display:grid;place-items:center;background:#0a2945;font-size:42px}.ath-name{font-size:28px;font-weight:900;color:#fff}.ath-meta{color:#9bb2c7;margin-top:6px}.status{display:inline-block;padding:4px 9px;border-radius:99px;background:#087cff22;border:1px solid #087cff66;color:#29a8ff;font-size:10px;font-weight:800}.post-head{display:flex;gap:10px;align-items:center}.mini{width:38px;height:38px;border-radius:50%;object-fit:cover}.feed-video{max-width:460px;margin:10px auto 8px}.feed-video [data-testid='stVideo']{max-width:460px!important;width:100%!important}.feed-video video{max-height:520px!important;object-fit:contain!important}.analysis-box{background:#061727;border:1px solid #163b59;border-radius:12px;padding:12px;margin-top:10px}.comment{background:#071827;border:1px solid #153b58;border-radius:9px;padding:8px 10px;margin:5px 0;color:#c4d1df;font-size:12px}@media(max-width:600px){.feed-video,.feed-video [data-testid='stVideo']{max-width:100%!important}.ath-hero{align-items:flex-start}.ath-photo,.ath-ph{width:84px;height:84px}.ath-name{font-size:22px}}</style>''',unsafe_allow_html=True)
pic=f"<img class='ath-photo' src='{html.escape(photo)}'>" if photo else "<div class='ath-ph'>🛹</div>"
st.markdown(f"<div class='ath-hero'>{pic}<div><div class='ath-name'>{html.escape(athlete.get('full_name') or 'Atleta')}</div><div class='ath-meta'>{html.escape(athlete.get('modality') or '—')} • {html.escape(athlete.get('stance') or '—')} • {html.escape(loc)}</div><div style='margin-top:10px'><span class='status'>FEED DO ATLETA</span></div></div></div>",unsafe_allow_html=True)
act1,act2=st.columns(2)
if act1.button('📚 Histórico de treinos', key='ath_history', use_container_width=True):
    st.session_state['history_athlete_id']=athlete_id
    st.switch_page('pages/04_Historico_de_Treinos.py')
if athlete_id==user.id and act2.button('🎥 Enviar novo vídeo', key='ath_upload', use_container_width=True):
    st.switch_page('pages/09_Enviar_Manobra.py')

try:
    posts=sb.table('athlete_posts').select('*').eq('athlete_id',athlete_id).order('created_at',desc=True).execute().data or []; tricks=sb.table('tricks').select('id,name').execute().data or []; tnames={x['id']:x['name'] for x in tricks}
except Exception as e: st.error(f'Feed ainda não disponível. Execute a migration V3.2. Detalhes: {e}'); st.stop()
if not posts: st.info('Nenhum vídeo publicado ainda. Quando o atleta enviar uma manobra, ela aparecerá aqui.')
for post in posts:
    with st.container(border=True):
        st.markdown(f"<div class='post-head'>{('<img class=mini src='+repr(photo)+'>') if photo else '🛹'}<div><b>{html.escape(athlete.get('full_name') or 'Atleta')}</b><br><span class='status'>{html.escape(post.get('session_title') or tnames.get(post.get('trick_id'),'SESSÃO DE TREINO'))}</span> <span class='status'>{html.escape((post.get('analysis_status') or 'aguardando').upper())}</span></div></div>",unsafe_allow_html=True)
        if post.get('caption'): st.write(post['caption'])
        try:
            if is_drive_path(post.get('video_path')):
                preview=drive_preview_url(post['video_path'])
                geo=drive_player_geometry(post['video_path'])
                st.markdown(f"""<div style='width:min(100%,{geo["max_width"]}px);margin:12px auto;border-radius:14px;overflow:hidden;background:#020b14;aspect-ratio:{geo["aspect"]};border:1px solid #163b59'>
                <iframe src='{preview}' style='width:100%;height:100%;border:0;display:block' allow='autoplay; fullscreen' allowfullscreen></iframe></div>""",unsafe_allow_html=True)
            else:
                signed=sb.storage.from_('trick-videos').create_signed_url(post['video_path'],3600); url=signed.get('signedURL') or signed.get('signedUrl') or signed.get('signed_url')
                st.markdown("<div class='feed-video'>",unsafe_allow_html=True); st.video(url); st.markdown("</div>",unsafe_allow_html=True)
        except Exception: st.caption('Vídeo privado indisponível temporariamente.')
        if can_delete_post(me, user.id, post):
            if st.button('🗑 Excluir vídeo', key='profile_del_'+post['id'], use_container_width=False):
                try:
                    delete_video_post(sb,post); st.success('Vídeo excluído.'); st.rerun()
                except Exception as e:
                    st.error(f'Não foi possível excluir o vídeo. Detalhes: {e}')
        if True:
            if st.button('🎬 Codificar sessão / várias tentativas', key='code_session_'+post['id'], use_container_width=True):
                st.session_state['selected_video_post_id']=post['id']
                st.switch_page('pages/10_Codificar_Sessao.py')
        # Avaliação técnica antiga: mantida para vídeos de tentativa isolada.
        try:
            ar=sb.table('trick_video_analyses').select('*').eq('post_id',post['id']).maybe_single().execute(); analysis=(ar.data or {}) if ar else {}
        except Exception:
            analysis={}
        if is_staff and post.get('upload_kind','single') == 'single':
            with st.expander('📊 Analisar esta tentativa', expanded=False):
                c1,c2,c3=st.columns(3)
                result=c1.selectbox('Resultado',['Acerto','Erro'],index=0 if analysis.get('result')!='Erro' else 1,key='res_'+post['id'])
                evaluation=c2.selectbox('Avaliação',['Excelente','Bom','Ruim'],index=['Excelente','Bom','Ruim'].index(analysis.get('evaluation')) if analysis.get('evaluation') in ['Excelente','Bom','Ruim'] else 1,key='eval_'+post['id'])
                difficulty=c3.selectbox('Dificuldade',['Baixa','Média','Alta'],index=['Baixa','Média','Alta'].index(analysis.get('difficulty')) if analysis.get('difficulty') in ['Baixa','Média','Alta'] else 1,key='dif_'+post['id'])
                c4,c5,c6=st.columns(3)
                risk=c4.selectbox('Risco',['Baixo','Médio','Alto'],index=['Baixo','Médio','Alto'].index(analysis.get('risk')) if analysis.get('risk') in ['Baixo','Médio','Alto'] else 1,key='risk_'+post['id'])
                speed=c5.selectbox('Velocidade',['Lento','Médio','Rápido'],index=['Lento','Médio','Rápido'].index(analysis.get('speed')) if analysis.get('speed') in ['Lento','Médio','Rápido'] else 1,key='spd_'+post['id'])
                direction=c6.selectbox('Direção',['Frontside','Backside','—'],index=['Frontside','Backside','—'].index(analysis.get('direction')) if analysis.get('direction') in ['Frontside','Backside','—'] else 2,key='dir_'+post['id'])
                base=st.selectbox('Base',['Regular','Goofy','Switch','Nollie','—'],index=['Regular','Goofy','Switch','Nollie','—'].index(analysis.get('base')) if analysis.get('base') in ['Regular','Goofy','Switch','Nollie','—'] else 4,key='base_'+post['id'])
                notes=st.text_area('Observação técnica',value=analysis.get('notes') or '',key='notes_'+post['id'])
                if st.button('✓ Salvar análise',key='save_analysis_'+post['id'],use_container_width=True):
                    payload={'post_id':post['id'],'athlete_id':athlete_id,'trick_id':post.get('trick_id'),'result':result,'evaluation':evaluation,'difficulty':difficulty,'risk':risk,'speed':speed,'direction':None if direction=='—' else direction,'base':None if base=='—' else base,'notes':notes.strip() or None,'analyzed_by':user.id}
                    try:
                        sb.table('trick_video_analyses').upsert(payload,on_conflict='post_id').execute(); sb.table('athlete_posts').update({'analysis_status':'analisado'}).eq('id',post['id']).execute(); st.success('Análise salva e somada aos resultados do atleta.'); st.rerun()
                    except Exception as e: st.error(f'Não foi possível salvar a análise: {e}')
        elif analysis:
            st.caption(f"Análise: {analysis.get('result','—')} • {analysis.get('evaluation','—')} • Dificuldade {analysis.get('difficulty','—')} • Risco {analysis.get('risk','—')} • {analysis.get('speed','—')}")
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
