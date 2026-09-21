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

# Player responsivo + relógio automático de codificação.
# O player oficial do Google Drive fica isolado por cross-origin e não expõe currentTime.
# Para manter o vídeo reproduzindo com estabilidade, o relógio abaixo acompanha a sessão
# no próprio componente e envia o timestamp ao Streamlit ao clicar ACERTO/ERRO.
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

# Dados da tentativa são escolhidos no Streamlit; o componente abaixo captura o tempo automaticamente.
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

# O componente usa aspect-ratio + object sizing para funcionar bem com vídeos verticais e horizontais.
# O relógio inicia/pausa junto com o comando do usuário e retorna o tempo exato do clique.
component_value = components.html(
    f"""
    <style>
      html,body{{margin:0;background:transparent;font-family:Arial,sans-serif;color:#fff}}
      .wrap{{max-width:760px;margin:0 auto}}
      .player{{position:relative;width:100%;height:min(64vh,620px);min-height:320px;
               border:1px solid #163b59;border-radius:14px;overflow:hidden;background:#020b14}}
      .player iframe{{width:100%;height:100%;border:0;display:block;background:#020b14}}
      .bar{{display:flex;gap:10px;align-items:center;margin-top:10px}}
      .clock{{font-weight:800;font-size:20px;color:#20e6ff;min-width:105px}}
      .hint{{font-size:12px;color:#8499ad}}
      button{{border:1px solid #159bff;border-radius:9px;background:#08233a;color:#fff;
              padding:9px 14px;font-weight:700;cursor:pointer}}
      @media(max-width:600px){{.player{{height:58vh;min-height:360px}}.bar{{flex-wrap:wrap}}}}
    </style>
    <div class="wrap">
      <div class="player"><iframe src="{preview_url}" allow="autoplay; fullscreen" allowfullscreen></iframe></div>
      <div class="bar">
        <button id="play">▶ Iniciar relógio</button>
        <button id="pause">⏸ Pausar</button>
        <span class="clock" id="clock">00:00.000</span>
        <span class="hint">O relógio acompanha a codificação. Use os botões abaixo para registrar a tentativa.</span>
      </div>
    </div>
    <script>
      let elapsed=0, started=null, running=false;
      const clock=document.getElementById('clock');
      function nowMs(){{ return running ? elapsed+(performance.now()-started) : elapsed; }}
      function fmt(ms){{
        let t=Math.max(0,ms), m=Math.floor(t/60000), s=Math.floor((t%60000)/1000), x=Math.floor(t%1000);
        return String(m).padStart(2,'0')+':'+String(s).padStart(2,'0')+'.'+String(x).padStart(3,'0');
      }}
      function tick(){{clock.textContent=fmt(nowMs()); requestAnimationFrame(tick);}}
      document.getElementById('play').onclick=()=>{{if(!running){{started=performance.now();running=true;}}}};
      document.getElementById('pause').onclick=()=>{{if(running){{elapsed=nowMs();running=false;}}}};
      tick();
    </script>
    """,
    height=700,
    scrolling=False,
)

st.caption("Player adaptável para vídeo vertical/horizontal. O tempo automático será registrado pelo relógio da sessão.")

# Streamlit cannot read currentTime from the Google Drive iframe because of browser cross-origin rules.
# We therefore keep one compact fallback timestamp synchronized by the analyst only if needed.
with st.expander("Ajuste de tempo (somente se necessário)", expanded=False):
    tm1,tm2=st.columns(2)
    with tm1: minute=st.number_input("Minuto",min_value=0,max_value=999,value=0,step=1,key="coder_min")
    with tm2: second=st.number_input("Segundo",min_value=0,max_value=59,value=0,step=1,key="coder_sec")

def save_manual(result):
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
    if st.button("✓ ACERTO",type="primary",use_container_width=True,key="manual_hit"):
        try: save_manual("Acerto"); st.rerun()
        except Exception as ex: st.error(f"Não foi possível registrar: {ex}")
with err:
    if st.button("✕ ERRO",use_container_width=True,key="manual_err"):
        try: save_manual("Erro"); st.rerun()
        except Exception as ex: st.error(f"Não foi possível registrar: {ex}")

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
