import mimetypes
import uuid
from datetime import date
import streamlit as st
from auth_utils import require_login, get_supabase

from ui_theme import apply_ui_theme

st.set_page_config(initial_sidebar_state="expanded", page_title="Cadastros • Skate Performance", page_icon="👥", layout="wide")
apply_ui_theme()

st.markdown("""<style>
/* V2.0 — controles globais escuros */
[data-testid="stButton"] button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stDownloadButton"] button {
  background:#0b1d31!important;color:#eef8ff!important;border:1px solid #245274!important;border-radius:10px!important;
}
[data-testid="stButton"] button:hover,[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover{
  background:#102b46!important;color:#fff!important;border-color:#1398ff!important;
}
[data-testid="stButton"] button:disabled,[data-testid="stFormSubmitButton"] button:disabled{
  background:#0a1725!important;color:#668097!important;border-color:#18354d!important;opacity:.8!important;
}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input,[data-testid="stTimeInput"] input,
[data-testid="stSelectbox"] [role="combobox"],[data-testid="stMultiSelect"] [role="combobox"],textarea{
  background:#0b1d2d!important;color:#eef8ff!important;border-color:#245274!important;
}
[data-testid="stDateInput"] button,[data-testid="stTimeInput"] button{background:#0b1d2d!important;color:#eef8ff!important;}
[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{background:#0b1d2d!important;color:#eef8ff!important;}
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"],[data-baseweb="calendar"]{background:#081827!important;color:#eef8ff!important}[role="option"]{background:#081827!important;color:#eef8ff!important}
</style>""", unsafe_allow_html=True)
st.markdown("""<style>
[data-testid="stToolbar"]{display:none!important}
.stApp,[data-testid="stAppViewContainer"]{background:#06111f!important;color:#eef8ff!important}
[data-testid="stSidebar"]{background:#081827!important}[data-testid="stSidebar"] *{color:#d9eafa!important}
.block-container{padding-top:1.2rem!important} h1,h2,h3,p,label{color:#eef8ff!important}
[data-testid="stTextInput"] input,[data-testid="stSelectbox"]>div>div,[data-testid="stFileUploader"] section{
  background:#0b1d2d!important;color:#eef8ff!important;border-color:#24445d!important
}
[data-testid="stFileUploader"] small,[data-testid="stFileUploader"] span{color:#b8cede!important}
div[data-testid="stButton"] button{border-radius:10px!important}
.profile-card{padding:.75rem 0 .15rem 0}
</style>""", unsafe_allow_html=True)

user, me = require_login(admin=True)
sb = get_supabase()

st.title("👥 Cadastros e permissões")
st.caption("Aqui você altera o cargo/função de cada pessoa. Para colocar ou remover pessoas de um time, use Gerenciar Times.")
st.page_link("pages/02_Times.py", label="🛹 Abrir gerenciamento de times", use_container_width=True)


def fetch_profiles():
    try:
        return sb.table("profiles").select("*").order("created_at", desc=True).execute().data or []
    except Exception as exc:
        st.error(f"Não foi possível carregar os cadastros: {exc}")
        return []


def upload_photo(profile_id, uploaded):
    if uploaded is None:
        return None
    ext = (uploaded.name.rsplit(".", 1)[-1] if "." in uploaded.name else "jpg").lower()
    if ext not in ("jpg", "jpeg", "png", "webp"):
        ext = "jpg"
    path = f"{profile_id}/{uuid.uuid4().hex}.{ext}"
    content_type = uploaded.type or mimetypes.guess_type(uploaded.name)[0] or "image/jpeg"
    sb.storage.from_("profile-photos").upload(
        path,
        uploaded.getvalue(),
        {"content-type": content_type, "upsert": "false"},
    )
    return sb.storage.from_("profile-photos").get_public_url(path)


def editor(r):
    is_self = r.get("id") == user.id
    role_value = r.get("role") or "skatista"
    modality_value = r.get("modality") or "Street"
    stance_value = r.get("stance") or "Regular"

    role_opts = ["skatista","tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica","familiar"]
    if role_value == "admin": role_opts = ["admin"] + role_opts

    with st.expander("✏️ Editar cadastro"):
        with st.form(f"edit_{r['id']}"):
            c1, c2 = st.columns(2)
            full_name = c1.text_input("Nome completo", value=r.get("full_name") or "")
            email = c2.text_input("E-mail", value=r.get("email") or "", disabled=True,
                                  help="O e-mail de acesso é gerenciado pelo Supabase Auth.")

            c3, c4, c5 = st.columns(3)
            role = c3.selectbox("Perfil", role_opts,
                                index=role_opts.index(role_value) if role_value in role_opts else 0,
                                disabled=is_self)
            modality_opts = ["Street", "Park", "Vert", "Outro"]
            modality = c4.selectbox("Modalidade", modality_opts,
                                    index=modality_opts.index(modality_value) if modality_value in modality_opts else 0)
            stance_opts = ["Regular", "Goofy", "Não informado"]
            stance = c5.selectbox("Base", stance_opts,
                                  index=stance_opts.index(stance_value) if stance_value in stance_opts else 2)

            c6,c7,c8 = st.columns([1.3,2,1])
            try: birth_value=date.fromisoformat(r.get("birth_date")) if r.get("birth_date") else None
            except Exception: birth_value=None
            birth_text=c6.text_input("Data de nascimento", value=birth_value.strftime("%d/%m/%Y") if birth_value else "", placeholder="DD/MM/AAAA")
            city=c7.text_input("Cidade",value=r.get("city") or "")
            states=["","AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO","EXTERIOR"]
            sv=(r.get("state") or "").upper(); state=c8.selectbox("Estado/UF",states,index=states.index(sv) if sv in states else 0)
            photo = st.file_uploader("Foto do perfil", type=["jpg", "jpeg", "png", "webp"], key=f"photo_{r['id']}")
            family_athlete_id = None
            if role == "familiar":
                athletes = sb.table("profiles").select("id,full_name,email").eq("role","skatista").eq("status","ativo").order("full_name").execute().data or []
                links = sb.table("family_athletes").select("athlete_id").eq("family_id",r["id"]).execute().data or []
                linked = links[0]["athlete_id"] if links else None
                labels={f"{a.get('full_name') or 'Sem nome'} • {a.get('email') or ''}":a["id"] for a in athletes}
                keys=list(labels); current=next((i for i,k in enumerate(keys) if labels[k]==linked),0) if keys else 0
                if keys: family_athlete_id=labels[st.selectbox("Atleta vinculado ao familiar",keys,index=current)]
                else: st.caption("Cadastre/aprove um skatista antes de vincular este familiar.")
            submitted = st.form_submit_button("💾 Salvar alterações", use_container_width=True)

        if submitted:
            try:
                payload = {
                    "full_name": full_name.strip() or r.get("full_name") or "Sem nome",
                    "modality": modality,
                    "stance": None if stance == "Não informado" else stance,
                    "birth_date": (date(int(birth_text[6:10]),int(birth_text[3:5]),int(birth_text[0:2])).isoformat() if birth_text.strip() else None), "city": city.strip() or None, "state": state or None,
                }
                if not is_self:
                    payload["role"] = role
                if photo is not None:
                    payload["photo_url"] = upload_photo(r["id"], photo)
                sb.table("profiles").update(payload).eq("id", r["id"]).execute()
                sb.table("family_athletes").delete().eq("family_id",r["id"]).execute()
                if role == "familiar" and family_athlete_id:
                    sb.table("family_athletes").insert({"family_id":r["id"],"athlete_id":family_athlete_id}).execute()
                st.success("Cadastro atualizado.")
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível salvar: {exc}")


def render_people(items, mode):
    if not items:
        st.info("Nenhum cadastro nesta categoria.")
        return
    for r in items:
        with st.container(border=True):
            photo_col, info_col, sport_col, action_col = st.columns([1, 3.2, 2.2, 1.8])
            if r.get("photo_url"):
                photo_col.image(r["photo_url"], width=88)
            else:
                photo_col.markdown("### 👤")

            info_col.markdown(f"**{r.get('full_name','—')}**")
            info_col.caption(r.get("email") or "Sem e-mail")
            role_label = (r.get("role") or "—").upper()
            if r.get("id") == user.id:
                role_label += " • VOCÊ"
            info_col.write(role_label)

            sport_col.write(f"**Modalidade:** {r.get('modality') or '—'}")
            sport_col.caption(f"Base: {r.get('stance') or '—'}  •  {r.get('city') or '—'}{'/'+r.get('state') if r.get('state') else ''}")

            if mode == "pending":
                if action_col.button("✅ Aprovar", key=f"ap_{r['id']}", use_container_width=True):
                    sb.table("profiles").update({"status": "ativo"}).eq("id", r["id"]).execute()
                    st.rerun()
                if action_col.button("⛔ Bloquear", key=f"bl_{r['id']}", use_container_width=True):
                    sb.table("profiles").update({"status": "bloqueado"}).eq("id", r["id"]).execute()
                    st.rerun()
            elif mode == "active":
                if r.get("id") == user.id:
                    action_col.info("🔐 Sua conta admin")
                    action_col.caption("Autobloqueio desativado.")
                elif action_col.button("⛔ Bloquear", key=f"bla_{r['id']}", use_container_width=True):
                    sb.table("profiles").update({"status": "bloqueado"}).eq("id", r["id"]).execute()
                    st.rerun()
            else:
                if action_col.button("♻️ Reativar", key=f"re_{r['id']}", use_container_width=True):
                    sb.table("profiles").update({"status": "ativo"}).eq("id", r["id"]).execute()
                    st.rerun()

            editor(r)


rows = fetch_profiles()
pending = [r for r in rows if r.get("status") == "pendente"]
active = [r for r in rows if r.get("status") == "ativo"]
blocked = [r for r in rows if r.get("status") == "bloqueado"]

t1, t2, t3 = st.tabs([
    f"PENDENTES ({len(pending)})",
    f"ATIVOS ({len(active)})",
    f"BLOQUEADOS ({len(blocked)})",
])
with t1:
    render_people(pending, "pending")
with t2:
    render_people(active, "active")
with t3:
    render_people(blocked, "blocked")
