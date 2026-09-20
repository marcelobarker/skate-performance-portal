import streamlit as st
from auth_utils import require_login,get_supabase
from ui_theme import apply_ui_theme
st.set_page_config(page_title="Livro de Manobras • Skate Performance",page_icon="📚",layout="wide")
apply_ui_theme(); user,profile=require_login(); sb=get_supabase()
STAFF={"admin","tecnico","presidente","vice_presidente","chefe_equipe","comissao_tecnica"}; can_edit=profile.get("role") in STAFF
st.markdown("""<style>
.trick-row{display:flex;align-items:center;min-height:42px;padding:7px 11px;background:#071a2b;border:1px solid #163b59;border-radius:9px;margin:5px 0}.trick-name{font-weight:750;color:#f5f8fc;font-size:13px}.trick-desc{font-size:10px;color:#8499ad;margin-top:2px}.st-key-trick_actions button{min-height:34px!important}
</style>""",unsafe_allow_html=True)
st.title("📚 Livro de Manobras"); st.caption("Biblioteca oficial usada na seleção de vídeos para análise.")
try:
    cats=sb.table("trick_categories").select("*").order("sort_order").execute().data or []
    tricks=sb.table("tricks").select("*").eq("active",True).order("name").execute().data or []
except Exception as e: st.error(f"Execute a migration V3.2 no Supabase. Detalhes: {e}"); st.stop()
if can_edit:
    with st.expander("＋ Cadastrar categoria ou manobra"):
        t1,t2=st.tabs(["Nova manobra","Nova categoria"])
        with t1:
            with st.form("new_trick"):
                cmap={c["name"]:c["id"] for c in cats}; cn=st.selectbox("Categoria",list(cmap)); name=st.text_input("Nome da manobra"); desc=st.text_input("Descrição / observação"); ok=st.form_submit_button("Adicionar manobra",type="primary",width="stretch")
            if ok and name.strip():
                try:
                    sb.rpc('manage_trick',{'p_action':'insert','p_category_id':cmap[cn],'p_name':name.strip(),'p_description':desc.strip() or None}).execute()
                    st.success("Manobra adicionada ao livro.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Não foi possível adicionar a manobra. Detalhes: {e}")
        with t2:
            with st.form("new_cat"):
                cname=st.text_input("Nome da categoria"); order=st.number_input("Ordem",0,999,100); ok2=st.form_submit_button("Adicionar categoria",width="stretch")
            if ok2 and cname.strip():
                try:
                    sb.rpc('add_trick_category',{'p_name':cname.strip(),'p_sort_order':int(order)}).execute()
                    st.success("Categoria adicionada.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Não foi possível adicionar a categoria. Detalhes: {e}")
edit_id=st.session_state.get("edit_trick_id")
if edit_id and can_edit:
    t=next((x for x in tricks if x["id"]==edit_id),None)
    if t:
        st.markdown("### Editar manobra")
        cmap={c["name"]:c["id"] for c in cats}; names=list(cmap); current=next((n for n,i in cmap.items() if i==t.get("category_id")),names[0])
        with st.form("edit_trick_form"):
            a,b=st.columns(2); newname=a.text_input("Nome",value=t["name"]); newcat=b.selectbox("Categoria",names,index=names.index(current)); newdesc=st.text_input("Descrição",value=t.get("description") or ""); save=st.form_submit_button("Salvar alterações",type="primary",width="stretch")
        if save and newname.strip():
            try:
                sb.rpc('manage_trick',{'p_action':'update','p_trick_id':edit_id,'p_category_id':cmap[newcat],'p_name':newname.strip(),'p_description':newdesc.strip() or None}).execute()
                st.session_state.pop("edit_trick_id",None)
                st.success("Manobra atualizada.")
                st.rerun()
            except Exception as e:
                st.error(f"Não foi possível editar a manobra. Detalhes: {e}")
if not cats: st.info("Nenhuma categoria cadastrada."); st.stop()
tabs=st.tabs([c["name"] for c in cats])
for tab,c in zip(tabs,cats):
    with tab:
        group=[t for t in tricks if t.get("category_id")==c["id"]]
        if not group: st.caption("Nenhuma manobra nesta categoria.")
        for t in group:
            ncol,ecol,dcol=st.columns([7.2,1.2,1.2],vertical_alignment="center")
            with ncol: st.markdown(f"<div class='trick-row'><div><div class='trick-name'>{t['name']}</div><div class='trick-desc'>{t.get('description') or 'Disponível para envio de vídeo'}</div></div></div>",unsafe_allow_html=True)
            if can_edit:
                with ecol:
                    if st.button("Editar",key="edit_"+t["id"],width="stretch"): st.session_state["edit_trick_id"]=t["id"]; st.rerun()
                with dcol:
                    if st.button("Excluir",key="del_"+t["id"],width="stretch"):
                        try:
                            sb.rpc('manage_trick',{'p_action':'delete','p_trick_id':t['id']}).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Não foi possível excluir a manobra. Detalhes: {e}")
