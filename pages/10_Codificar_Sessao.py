import html
from collections import Counter
import streamlit as st
from auth_utils import require_login, get_supabase
from ui_theme import apply_ui_theme
from drive_utils import is_drive_path, drive_preview_url

st.set_page_config(page_title="Codificar Sessão • Skate Performance", page_icon="🎬", layout="wide")
apply_ui_theme(); user, me = require_login(); sb = get_supabase()
STAFF = {"admin","tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica"}
if me.get("role") not in STAFF:
    st.error("Área exclusiva da equipe técnica."); st.stop()
post_id = st.session_state.get("selected_video_post_id")
if not post_id:
    st.info("Abra o feed de um atleta e escolha um vídeo para analisar."); st.stop()

try:
    post = sb.table("athlete_posts").select("*").eq("id",post_id).single().execute().data
    athlete = sb.table("profiles").select("id,full_name").eq("id",post["athlete_id"]).single().execute().data
    tricks = sb.table("tricks").select("id,name,category_id").eq("active",True).order("name").execute().data or []
    cats = sb.table("trick_categories").select("id,name,sort_order").order("sort_order").execute().data or []
    if is_drive_path(post.get("video_path")):
        video_url = drive_preview_url(post["video_path"])
        video_is_drive = True
    else:
        signed = sb.storage.from_("trick-videos").create_signed_url(post["video_path"], 7200)
        video_url = signed.get("signedURL") or signed.get("signedUrl") or signed.get("signed_url")
        video_is_drive = False
except Exception as e:
    st.error(f"Não foi possível abrir a sessão: {e}"); st.stop()

st.markdown("""<style>
.code-title{font-size:30px;font-weight:900;color:#f5f8fc}.code-sub{color:#8499ad;margin-bottom:12px}
.video-wrap{max-width:760px;margin:0 auto}.video-wrap [data-testid='stVideo']{max-width:760px!important}
.event-card{background:#071a2b;border:1px solid #163b59;border-radius:10px;padding:8px 11px;margin:5px 0}
.event-time{color:#20e6ff;font-weight:900}.event-hit{color:#00e4a4;font-weight:800}.event-err{color:#ff5c68;font-weight:800}
@media(max-width:700px){.video-wrap,.video-wrap [data-testid='stVideo']{max-width:100%!important}}
</style>""", unsafe_allow_html=True)
st.markdown(f"<div class='code-title'>Codificação de sessão</div><div class='code-sub'>{html.escape(athlete.get('full_name') or 'Atleta')} • {html.escape(post.get('session_title') or 'Vídeo de treino')}</div>", unsafe_allow_html=True)

st.markdown("<div class='video-wrap'>", unsafe_allow_html=True)
if video_is_drive:
    st.iframe(video_url, height=430, scrolling=False)
else:
    st.video(video_url)
st.markdown("</div>", unsafe_allow_html=True)
st.caption("Modo de codificação: assista ao treino, pause na tentativa, selecione a manobra e marque ACERTO ou ERRO. O registro entra imediatamente nas estatísticas. Nesta versão o tempo é informado em Min/Seg; a captura automática do relógio do player exige o player customizado que será a próxima etapa.")

try:
    events = sb.table("trick_video_events").select("*").eq("post_id",post_id).order("timestamp_seconds").execute().data or []
except Exception as e:
    st.error(f"Execute a migration V3.8. Detalhes: {e}"); st.stop()

# Favoritos desta sessão: prioriza manobras já marcadas no próprio vídeo.
used_ids = [x.get("trick_id") for x in events if x.get("trick_id")]
trick_by_id = {t["id"]: t for t in tricks}
used_names = [trick_by_id[x]["name"] for x in used_ids if x in trick_by_id]

with st.container(border=True):
    st.markdown("### ⚡ CODIFICAÇÃO RÁPIDA")
    ctime1, ctime2, ccat = st.columns([1,1,2])
    minute = ctime1.number_input("Min", min_value=0, max_value=999, value=0, step=1)
    second = ctime2.number_input("Seg", min_value=0, max_value=59, value=0, step=1)
    cmap = {c["name"]:c["id"] for c in cats}
    cat_name = ccat.selectbox("Categoria", list(cmap) if cmap else ["Todas"], key="coding_category")
    filtered = [t for t in tricks if not cmap or t.get("category_id") == cmap.get(cat_name)]
    names = [t["name"] for t in filtered]
    if used_names:
        # mantém as mais usadas no topo quando pertencem à categoria atual
        names = list(dict.fromkeys([n for n in used_names[::-1] if n in names] + names))
    chosen = st.selectbox("MANOBRA", names, placeholder="Selecione a manobra", key="coding_trick") if names else None
    chosen_id = next((t["id"] for t in tricks if t["name"] == chosen), None)

    a,b,c,d = st.columns(4)
    evaluation = a.selectbox("Avaliação", ["Bom","Excelente","Ruim"])
    difficulty = b.selectbox("Dificuldade", ["Média","Baixa","Alta"])
    risk = c.selectbox("Risco", ["Médio","Baixo","Alto"])
    speed = d.selectbox("Velocidade", ["Médio","Lento","Rápido"])
    e,f = st.columns(2)
    direction = e.selectbox("Direção", ["—","Frontside","Backside"])
    base = f.selectbox("Base", ["—","Regular","Goofy","Switch","Nollie"])
    notes = st.text_input("Observação rápida", placeholder="Opcional")
    hit, err = st.columns(2)

    def save_event(result):
        if not chosen_id:
            st.error("Selecione uma manobra."); return
        payload = {
            "p_post_id": post_id, "p_athlete_id": post["athlete_id"], "p_trick_id": chosen_id,
            "p_timestamp_seconds": int(minute)*60 + int(second), "p_result": result,
            "p_evaluation": evaluation, "p_difficulty": difficulty, "p_risk": risk, "p_speed": speed,
            "p_direction": None if direction == "—" else direction, "p_base": None if base == "—" else base,
            "p_notes": notes.strip() or None
        }
        try:
            sb.rpc("save_trick_video_event", payload).execute()
            sb.table("athlete_posts").update({"analysis_status":"em_analise"}).eq("id",post_id).execute()
            st.rerun()
        except Exception as ex: st.error(f"Não foi possível registrar a tentativa: {ex}")
    if hit.button("✓ ACERTO", type="primary", use_container_width=True, key="quick_hit"): save_event("Acerto")
    if err.button("✕ ERRO", use_container_width=True, key="quick_err"): save_event("Erro")

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
