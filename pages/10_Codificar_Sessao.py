import html
from collections import Counter
import streamlit as st
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme
from drive_utils import is_drive_path, drive_stream_url

st.set_page_config(page_title="Codificar Sessão • Skate Performance", page_icon="🎬", layout="wide")
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

# Player profissional: captura o currentTime no próprio navegador.
# O componente recebe a biblioteca de manobras e envia para Python um único evento
# contendo timestamp + manobra + resultado + atributos técnicos.
try:
    video_coder = st.components.v2.component(
        name="skate_video_coder_v314",
        html="""
        <div class="coder-shell">
          <div class="player-box"><video id="coderVideo" controls playsinline preload="metadata"></video></div>
          <div class="time-row"><span id="clock">00:00.000</span><span class="hint">Pause ou clique durante o vídeo. O tempo é capturado automaticamente.</span></div>
          <div class="grid two">
            <label>Categoria<select id="category"></select></label>
            <label>Manobra<select id="trick"></select></label>
          </div>
          <div class="grid four">
            <label>Avaliação<select id="evaluation"><option>Bom</option><option>Excelente</option><option>Ruim</option></select></label>
            <label>Dificuldade<select id="difficulty"><option>Média</option><option>Baixa</option><option>Alta</option></select></label>
            <label>Risco<select id="risk"><option>Médio</option><option>Baixo</option><option>Alto</option></select></label>
            <label>Velocidade<select id="speed"><option>Médio</option><option>Lento</option><option>Rápido</option></select></label>
          </div>
          <div class="grid two">
            <label>Direção<select id="direction"><option>—</option><option>Frontside</option><option>Backside</option></select></label>
            <label>Base<select id="base"><option>—</option><option>Regular</option><option>Goofy</option><option>Switch</option><option>Nollie</option></select></label>
          </div>
          <label>Observação<input id="notes" placeholder="Opcional" /></label>
          <div class="actions"><button id="hit" class="hit">✓ ACERTO</button><button id="err" class="err">✕ ERRO</button></div>
          <div class="shortcuts">Atalhos: <b>A</b> = acerto &nbsp; <b>E</b> = erro &nbsp; <b>Espaço</b> = play/pause</div>
        </div>
        """,
        css="""
        .coder-shell{font-family:var(--st-font);color:#f5f8fc;background:#061727;border:1px solid #163b59;border-radius:14px;padding:14px;box-sizing:border-box}
        .player-box{max-width:460px;margin:0 auto 8px;background:#020b14;border-radius:12px;overflow:hidden;border:1px solid #163b59}
        video{display:block;width:100%;max-height:290px;background:#000;object-fit:contain}
        .time-row{max-width:460px;margin:0 auto 14px;display:flex;align-items:center;justify-content:space-between;gap:12px}
        #clock{font-size:20px;font-weight:900;color:#20e6ff;font-variant-numeric:tabular-nums}.hint{font-size:12px;color:#8499ad;text-align:right}
        .grid{display:grid;gap:10px;margin:9px 0}.two{grid-template-columns:1fr 2fr}.four{grid-template-columns:repeat(4,1fr)}
        label{display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:800;color:#c4d1df}
        select,input{width:100%;box-sizing:border-box;background:#10263b;color:#f5f8fc;border:1px solid #245274;border-radius:9px;padding:10px;font:inherit;outline:none}
        select:focus,input:focus{border-color:#20e6ff;box-shadow:0 0 0 2px rgba(32,230,255,.12)}
        .actions{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:13px}.actions button{border:0;border-radius:11px;padding:15px 10px;font-weight:950;font-size:16px;color:white;cursor:pointer}
        .hit{background:linear-gradient(135deg,#00a967,#00e4a4);box-shadow:0 0 18px rgba(0,228,164,.18)}.err{background:linear-gradient(135deg,#d62f48,#ff5c68);box-shadow:0 0 18px rgba(255,92,104,.16)}
        .actions button:active{transform:scale(.99)}.shortcuts{text-align:center;color:#8499ad;font-size:11px;margin-top:9px}
        @media(max-width:700px){.four,.two{grid-template-columns:1fr 1fr}.player-box{max-width:100%}video{max-height:250px}.time-row{max-width:100%;align-items:flex-start;flex-direction:column}.hint{text-align:left}.actions{position:sticky;bottom:4px}.actions button{padding:14px 8px}}
        """,
        js="""
        export default function({ parentElement, data, setTriggerValue }) {
          const v=parentElement.querySelector('#coderVideo');
          const clock=parentElement.querySelector('#clock');
          const cat=parentElement.querySelector('#category');
          const trick=parentElement.querySelector('#trick');
          if(v.dataset.src !== data.video_url){v.src=data.video_url;v.dataset.src=data.video_url;v.load();}
          v.playsInline=true;
          if(!v.dataset.initialized){
            v.dataset.initialized='1';
            v.addEventListener('loadedmetadata',()=>{ if(data.resume_time>0){v.currentTime=data.resume_time;} });
          }
          function fmt(t){const m=Math.floor(t/60),s=Math.floor(t%60),ms=Math.floor((t-Math.floor(t))*1000);return String(m).padStart(2,'0')+':'+String(s).padStart(2,'0')+'.'+String(ms).padStart(3,'0');}
          const updateClock=()=>clock.textContent=fmt(v.currentTime||0);v.ontimeupdate=updateClock;v.onseeked=updateClock;v.onpause=updateClock;
          const cats=data.categories||[], tricks=data.tricks||[];
          const previousCat=cat.value||data.defaults.category||'';
          cat.innerHTML=cats.map(c=>`<option value="${c.id}">${c.name}</option>`).join('');
          if([...cat.options].some(o=>o.value===previousCat))cat.value=previousCat;
          function fillTricks(){const previous=trick.value||data.defaults.trick_id||'';const list=tricks.filter(t=>!cat.value||t.category_id===cat.value);trick.innerHTML=list.map(t=>`<option value="${t.id}">${t.name}</option>`).join('');if([...trick.options].some(o=>o.value===previous))trick.value=previous;}
          cat.onchange=fillTricks;fillTricks();
          const ids=['evaluation','difficulty','risk','speed','direction','base'];
          ids.forEach(id=>{const el=parentElement.querySelector('#'+id);const val=data.defaults[id];if(val && [...el.options].some(o=>o.value===val))el.value=val;});
          parentElement.querySelector('#notes').value=data.defaults.notes||'';
          function mark(result){
            if(!trick.value)return;
            v.pause();
            const selected=tricks.find(t=>t.id===trick.value)||{};
            setTriggerValue('mark_event',{
              nonce:Date.now(), timestamp_seconds:v.currentTime||0, result:result,
              trick_id:trick.value, trick_name:selected.name||'', category:cat.value,
              evaluation:parentElement.querySelector('#evaluation').value,
              difficulty:parentElement.querySelector('#difficulty').value,
              risk:parentElement.querySelector('#risk').value,
              speed:parentElement.querySelector('#speed').value,
              direction:parentElement.querySelector('#direction').value,
              base:parentElement.querySelector('#base').value,
              notes:parentElement.querySelector('#notes').value
            });
          }
          parentElement.querySelector('#hit').onclick=()=>mark('Acerto');
          parentElement.querySelector('#err').onclick=()=>mark('Erro');
          parentElement.onkeydown=(e)=>{
            if(e.target.tagName==='INPUT'||e.target.tagName==='SELECT')return;
            if(e.code==='Space'){e.preventDefault();v.paused?v.play():v.pause();}
            if(e.key.toLowerCase()==='a')mark('Acerto');
            if(e.key.toLowerCase()==='e')mark('Erro');
          };
          parentElement.tabIndex=0;
        }
        """
    )
except Exception:
    video_coder = None

try:
    events = sb.table("trick_video_events").select("*").eq("post_id",post_id).order("timestamp_seconds").execute().data or []
except Exception as e:
    st.error(f"Execute a migration V3.8. Detalhes: {e}"); st.stop()

trick_by_id = {t["id"]: t for t in tricks}
last_time = float(events[-1].get("timestamp_seconds") or 0) if events else 0.0
defaults = st.session_state.get("coder_defaults", {})
if not defaults:
    defaults = {"category": cats[0]["id"] if cats else "", "trick_id":"", "evaluation":"Bom", "difficulty":"Média", "risk":"Médio", "speed":"Médio", "direction":"—", "base":"—", "notes":""}

if video_coder is None:
    st.error("O player profissional requer uma versão atual do Streamlit. Atualize as dependências e reinicie o app.")
    st.video(video_url)
else:
    result = video_coder(
        data={"video_url":video_url,"resume_time":last_time,"tricks":tricks,"categories":cats,"defaults":defaults},
        default={"mark_event":None}, key="sportscode_coder", on_mark_event_change=lambda: None, width="stretch"
    )
    event = getattr(result, "mark_event", None)
    if event:
        # Evita gravar duas vezes o mesmo clique em reruns inesperados.
        nonce = event.get("nonce") if isinstance(event, dict) else None
        if nonce and st.session_state.get("last_coder_nonce") != nonce:
            st.session_state["last_coder_nonce"] = nonce
            st.session_state["coder_defaults"] = {
                "category":event.get("category") or "", "trick_id":event.get("trick_id") or "",
                "evaluation":event.get("evaluation") or "Bom", "difficulty":event.get("difficulty") or "Média",
                "risk":event.get("risk") or "Médio", "speed":event.get("speed") or "Médio",
                "direction":event.get("direction") or "—", "base":event.get("base") or "—", "notes":event.get("notes") or ""
            }
            payload = {
                "p_post_id":post_id,"p_athlete_id":post["athlete_id"],"p_trick_id":event.get("trick_id"),
                "p_timestamp_seconds":int(round(float(event.get("timestamp_seconds") or 0))),"p_result":event.get("result"),
                "p_evaluation":event.get("evaluation"),"p_difficulty":event.get("difficulty"),"p_risk":event.get("risk"),"p_speed":event.get("speed"),
                "p_direction":None if event.get("direction") in (None,"—") else event.get("direction"),
                "p_base":None if event.get("base") in (None,"—") else event.get("base"),"p_notes":event.get("notes") or None
            }
            try:
                sb.rpc("save_trick_video_event",payload).execute()
                sb.table("athlete_posts").update({"analysis_status":"em_analise"}).eq("id",post_id).execute()
                st.toast(f"{event.get('trick_name','Manobra')} • {event.get('result')} • {float(event.get('timestamp_seconds') or 0):.2f}s")
                st.rerun()
            except Exception as ex:
                st.error(f"Não foi possível registrar a tentativa: {ex}")

st.caption("O relógio agora é automático: pause ou clique ACERTO/ERRO enquanto o vídeo roda. O sistema registra o tempo atual do player e mantém a manobra selecionada para a próxima tentativa.")

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
