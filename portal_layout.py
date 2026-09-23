import streamlit as st
from nav_v472 import render_top_nav

def _mobile_request():
    try:
        ua=str(st.context.headers.get("User-Agent", "")).lower()
    except Exception:
        ua=""
    return any(x in ua for x in ("iphone","ipad","ipod","android","mobile"))

def render_new_shell(me, user, active=""):
    mobile=_mobile_request()
    st.markdown('''<style>
    /* V4.67 new portal shell: top navigation replaces the legacy sidebar on redesigned pages */
    section[data-testid="stSidebar"]{display:none!important}
    [data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"],button[aria-label="Open sidebar"]{display:none!important}
    .block-container{max-width:1560px!important;padding:18px 28px 44px!important;margin:0 auto!important}
    [data-testid="stAppViewContainer"]>.main{margin-left:0!important}
    .np-head{padding:22px 4px 18px;border-bottom:1px solid rgba(74,166,230,.18);margin-bottom:20px}
    .np-kicker{font-size:11px;letter-spacing:.19em;text-transform:uppercase;color:#22d8ff;font-weight:900;margin-bottom:7px}
    .np-title{font-size:36px;line-height:1.05;color:#f6fbff;font-weight:950;letter-spacing:-.035em}
    .np-sub{font-size:14px;color:#86a3ba;margin-top:8px;max-width:820px;line-height:1.55}
    .np-panel{background:linear-gradient(145deg,rgba(8,29,48,.96),rgba(3,16,28,.98));border:1px solid rgba(61,149,213,.23);border-radius:18px;padding:18px;box-shadow:0 16px 38px rgba(0,0,0,.17)}
    .np-section{font-size:20px;font-weight:900;color:#f3f9ff;margin:7px 0 14px}
    @media(max-width:900px){.block-container{padding:10px 12px 32px!important}.np-title{font-size:29px}}
    html,body,#root,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"]{min-height:100vh!important;min-height:100dvh!important;background:#03111E!important;overflow-x:hidden!important}
    </style>''', unsafe_allow_html=True)
    if mobile:
        st.markdown("""<style>
        [data-testid='stMainBlockContainer'],.main .block-container,.block-container{box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;margin:0!important;padding:8px 10px 28px!important;overflow-x:hidden!important}
        [data-testid='stMain'],section.main,.main{width:100%!important;max-width:100%!important;overflow-x:hidden!important}
        .np-title{font-size:28px!important}.np-sub{font-size:13px!important}.np-panel{padding:14px!important;border-radius:14px!important}
        </style>""", unsafe_allow_html=True)
    render_top_nav(nav_name=me.get('full_name') or getattr(user,'email','Usuário'), nav_role=me.get('role') or 'membro', nav_photo=me.get('photo_url'), active=active, key='nav_new_'+active)

def page_head(kicker,title,subtitle):
    st.markdown(f"<div class='np-head'><div class='np-kicker'>{kicker}</div><div class='np-title'>{title}</div><div class='np-sub'>{subtitle}</div></div>", unsafe_allow_html=True)
