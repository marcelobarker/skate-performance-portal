import html
from collections import Counter
import streamlit as st
import streamlit.components.v1 as components
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme
from drive_utils import is_drive_path, drive_stream_url, drive_preview_url

st.set_page_config(initial_sidebar_state="expanded", page_title="Codificar Sessão • Skate Performance", page_icon="🎬", layout="wide")
apply_ui_theme(); user, me = require_login(); sb = get_supabase()
if me.get("role") != "admin":
    st.error("Área de desenvolvimento restrita ao administrador."); st.stop()
post_id = st.session_state.get("selected_video_post_id")
if not post_id:
    st.info("Abra o feed de um atleta e escolha um vídeo para analisar."); st.stop()

try:
    post = sb.table("athlete_posts").select("*").eq("id",post_id).single().execute().data
    athlete = sb.table("profiles").select("id,full_name").eq("id",post["athlete_id"]).single().execute().data
    tricks = sb.table("tricks").select("id,name,category_id").eq("active",True).order("name").execute().data or []
    cats = sb.table("trick_categories").select("id,name,sort_order").order("sort_order").execute().data or []
    if is_drive_path(post.get("video_path")):
        video_url = drive_stream_url(post["video_path"])
        video_is_drive = True
    else:
        signed = sb.storage.from_("trick-videos").create_signed_url(post["video_path"], 7200)
        video_url = signed.get("signedURL") or signed.get("signedUrl") or signed.get("signed_url")
        video_is_drive = False
except Exception as e:
    st.error(f"Não foi possível abrir a sessão: {e}"); st.stop()

st.markdown("""<style>
.code-title{font-size:30px;font-weight:900;color:#f5f8fc}.code-sub{color:#8499ad;margin-bottom:12px}
.video-wrap{max-width:460px;margin:0 auto}.video-wrap [data-testid='stVideo']{max-width:460px!important;width:100%!important}
.event-card{background:#071a2b;border:1px solid #163b59;border-radius:10px;padding:8px 11px;margin:5px 0}
.event-time{color:#20e6ff;font-weight:900}.event-hit{color:#00e4a4;font-weight:800}.event-err{color:#ff5c68;font-weight:800}
@media(max-width:700px){.video-wrap,.video-wrap [data-testid='stVideo']{max-width:100%!important}}
</style>""", unsafe_allow_html=True)
st.markdown(f"<div class='code-title'>Codificação de sessão</div><div class='code-sub'>{html.escape(athlete.get('full_name') or 'Atleta')} • {html.escape(post.get('session_title') or 'Vídeo de treino')}</div>", unsafe_allow_html=True)

# Player da sessão.
# IMPORTANTE: o Google Drive reproduz o vídeo dentro de um iframe cross-origin.
# O navegador não permite que o Streamlit leia o currentTime desse iframe.
# Portanto não usamos um segundo relógio independente: ele poderia divergir da timeline real.
if is_drive_path(post.get("video_path")):
    preview_url = drive_preview_url(post["video_path"])
else:
    preview_url = video_url

try:
    events = sb.table("trick_video_events").select("*").eq("post_id",post_id).order("timestamp_seconds").execute().data or []
except Exception as e:
    st.error(f"Execute a migration V3.8. Detalhes: {e}"); st.stop()

trick_by_id = {t["id"]: t for t in tricks}
cat_by_id = {c["id"]: c for c in cats}
if not cats or not tricks:
    st.info("Cadastre categorias e manobras no Livro de Manobras.")
    st.stop()

# Player central, responsivo. A altura maior favorece vertical sem deformar horizontal.
st.markdown(
    f"""
    <div style="width:100%;max-width:760px;height:min(68vh,640px);min-height:390px;
                margin:0 auto 18px;border-radius:14px;overflow:hidden;background:#000;
                border:1px solid #163b59;box-shadow:0 10px 30px rgba(0,0,0,.22)">
      <iframe src="{preview_url}" width="100%" height="100%"
              style="display:block;border:0;background:#000"
              allow="autoplay; fullscreen" allowfullscreen></iframe>
    </div>
    """,
    unsafe_allow_html=True,
)

# Seleção da manobra e atributos.
cat_names=[c["name"] for c in cats]
cat_name=st.selectbox("Categoria",cat_names,key="coder_category")
cat_id=next(c["id"] for c in cats if c["name"]==cat_name)
available=[t for t in tricks if t.get("category_id")==cat_id]
if not available:
    st.warning("Nenhuma manobra ativa nesta categoria."); st.stop()
trick_name=st.selectbox("Manobra",[t["name"] for t in available],key="coder_trick")
trick_id=next(t["id"] for t in available if t["name"]==trick_name)

a,b,c,d=st.columns(4)
with a: evaluation=st.selectbox("Avaliação",["Bom","Excelente","Ruim"],key="coder_eval")
with b: difficulty=st.selectbox("Dificuldade",["Média","Baixa","Alta"],key="coder_diff")
with c: risk=st.selectbox("Risco",["Médio","Baixo","Alto"],key="coder_risk")
with d: speed=st.selectbox("Velocidade",["Médio","Lento","Rápido"],key="coder_speed")
a,b=st.columns(2)
with a: direction=st.selectbox("Direção",["—","Frontside","Backside"],key="coder_dir")
with b: base=st.selectbox("Base",["—","Regular","Goofy","Switch","Nollie"],key="coder_base")
notes=st.text_input("Observação",placeholder="Opcional",key="coder_notes")

# O timestamp deve representar a timeline REAL do vídeo.
# Enquanto o vídeo estiver no iframe oficial do Drive, o tempo é informado aqui.
# Assim não salvamos um relógio falso/desincronizado.
t1,t2=st.columns([1,1])
with t1:
    minute=st.number_input("Minuto do vídeo",min_value=0,max_value=999,value=0,step=1,key="coder_min")
with t2:
    second=st.number_input("Segundo do vídeo",min_value=0,max_value=59,value=0,step=1,key="coder_sec")

def save_attempt(result):
    payload={
        "p_post_id":post_id,"p_athlete_id":post["athlete_id"],"p_trick_id":trick_id,
        "p_timestamp_seconds":int(minute)*60+int(second),"p_result":result,
        "p_evaluation":evaluation,"p_difficulty":difficulty,"p_risk":risk,"p_speed":speed,
        "p_direction":None if direction=="—" else direction,
        "p_base":None if base=="—" else base,"p_notes":notes or None
    }
    sb.rpc("save_trick_video_event",payload).execute()
    sb.table("athlete_posts").update({"analysis_status":"em_analise"}).eq("id",post_id).execute()

hit,err=st.columns(2)
with hit:
    if st.button("✓ ACERTO",type="primary",use_container_width=True,key="coder_hit"):
        try:
            save_attempt("Acerto")
            st.success(f"Acerto registrado em {int(minute):02d}:{int(second):02d}.")
            st.rerun()
        except Exception as ex:
            st.error(f"Não foi possível registrar: {ex}")
with err:
    if st.button("✕ ERRO",use_container_width=True,key="coder_err"):
        try:
            save_attempt("Erro")
            st.error(f"Erro registrado em {int(minute):02d}:{int(second):02d}.")
            st.rerun()
        except Exception as ex:
            st.error(f"Não foi possível registrar: {ex}")

st.caption("O timestamp salvo corresponde ao tempo da timeline do vídeo informado acima. O relógio paralelo foi removido para evitar marcações incorretas.")

st.markdown("### Tentativas registradas")
if events:
    hits = sum(1 for x in events if x.get("result") == "Acerto"); total = len(events); rate = hits/total*100
    m1,m2,m3,m4 = st.columns(4); m1.metric("Tentativas",total); m2.metric("Acertos",hits); m3.metric("Erros",total-hits); m4.metric("Taxa",f"{rate:.1f}%")
    for ev in events:
        tname = trick_by_id.get(ev.get("trick_id"),{}).get("name","Manobra")
        mm,ss = divmod(int(ev.get("timestamp_seconds") or 0),60)
        c1,c2 = st.columns([8,1])
        cls = "event-hit" if ev.get("result") == "Acerto" else "event-err"
        c1.markdown(f"<div class='event-card'><span class='event-time'>{mm:02d}:{ss:02d}</span> &nbsp; <b>{html.escape(tname)}</b> &nbsp; <span class='{cls}'>{ev.get('result')}</span> &nbsp; <span style='color:#8499ad'>{ev.get('difficulty') or ''} • {ev.get('risk') or ''} • {ev.get('speed') or ''}</span></div>", unsafe_allow_html=True)
        if c2.button("Excluir", key="del_evt_"+ev["id"]):
            try: sb.rpc("delete_trick_video_event", {"p_event_id":ev["id"]}).execute(); st.rerun()
            except Exception as ex: st.error(str(ex))
else:
    st.info("Nenhuma tentativa registrada ainda.")

if st.button("Finalizar análise da sessão", type="primary", use_container_width=True):
    try:
        sb.table("athlete_posts").update({"analysis_status":"analisado"}).eq("id",post_id).execute()
        st.success("Sessão finalizada. Os resultados já aparecem na página de Análise do atleta.")
    except Exception as e: st.error(str(e))
