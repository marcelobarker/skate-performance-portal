import html
import streamlit as st

PAGES = [
    ("Home", "home", "/"),
    ("Times", "shield", "/Times"),
    ("Histórico", "history", "/Historico_de_Treinos"),
    ("Codificar", "code", "/Codificar_Sessao"),
    ("Feed", "feed", "/Feed"),
    ("Central", "coach", "/Central_do_Treinador"),
    ("Livro", "book", "/Livro_de_Manobras"),
    ("Administração", "admin", "/Cadastros"),
]

SVG = {
    "home": '<svg viewBox="0 0 24 24"><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5"/><path d="M9.5 20v-6h5v6"/></svg>',
    "shield": '<svg viewBox="0 0 24 24"><path d="M12 3 19 6v5.3c0 4.5-2.7 7.7-7 9.7-4.3-2-7-5.2-7-9.7V6l7-3Z"/></svg>',
    "history": '<svg viewBox="0 0 24 24"><path d="M4 12a8 8 0 1 0 2.3-5.7L4 8.6"/><path d="M4 4v4.6h4.6M12 8v4l3 2"/></svg>',
    "code": '<svg viewBox="0 0 24 24"><path d="m8 9-4 3 4 3M16 9l4 3-4 3M14 5l-4 14"/></svg>',
    "feed": '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="3"/><circle cx="9" cy="9" r="1"/><path d="M8 16c1.2-2 2.6-3 4-3s2.8 1 4 3"/></svg>',
    "coach": '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="3"/><path d="M6 20c.7-4 2.7-6 6-6s5.3 2 6 6M4 5h3M17 5h3"/></svg>',
    "book": '<svg viewBox="0 0 24 24"><path d="M4 5.5A3.5 3.5 0 0 1 7.5 2H20v17H7.5A3.5 3.5 0 0 0 4 22z"/><path d="M4 5.5V22M8 6h8M8 10h8"/></svg>',
    "admin": '<svg viewBox="0 0 24 24"><path d="M12 3 19 6v5c0 4.5-2.7 7.6-7 9.7C7.7 18.6 5 15.5 5 11V6z"/><path d="M9 12l2 2 4-4"/></svg>',
    "menu": '<svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "profile": '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
}


def _mobile_request():
    try:
        ua = str(st.context.headers.get("User-Agent", "")).lower()
    except Exception:
        ua = ""
    return any(x in ua for x in ("iphone", "ipad", "ipod", "android", "mobile"))


def render_top_nav(nav_name="Usuário", nav_role="Membro", nav_photo=None, active="Home", key="top_nav"):
    # Não dependemos apenas do User-Agent: o CSS também troca para o menu mobile por largura.
    mobile_ua = _mobile_request()
    nav_name = str(nav_name or "Usuário").strip()
    nav_role = str(nav_role or "Membro").replace("_", " ").title()
    nav_photo = str(nav_photo).strip() if nav_photo else None
    initials = "".join(p[:1].upper() for p in nav_name.split()[:2]) or "U"

    desktop_links = []
    mobile_links = []
    for label, icon, href in PAGES:
        cls = " sp429-active" if label == active else ""
        item = f'<a class="sp429-item{cls}" href="{href}" target="_self">{SVG[icon]}<span>{html.escape(label)}</span></a>'
        desktop_links.append(item)
        mitem = f'<a class="sp429-mitem{cls}" href="{href}" target="_self">{SVG[icon]}<span>{html.escape(label)}</span></a>'
        mobile_links.append(mitem)

    if nav_photo:
        avatar = f'<img class="sp429-avatar" src="{html.escape(nav_photo, quote=True)}" alt="Foto de perfil">'
    else:
        avatar = f'<div class="sp429-avatar sp429-initials">{html.escape(initials)}</div>'

    force_mobile = " sp429-force-mobile" if mobile_ua else ""

    css = '''<style>
/* ===== NAV GLOBAL V4.75 ===== */
.sp429-shell{box-sizing:border-box;position:relative;width:100%;max-width:none;margin:0 0 18px 0;padding:0;background:linear-gradient(180deg,#071827 0%,#05131f 100%);border:1px solid #163b59;border-radius:0 0 14px 14px;min-height:78px;font-family:"Segoe UI Variable",Inter,Manrope,Arial,sans-serif;box-shadow:0 8px 28px rgba(0,0,0,.16);overflow:visible!important;z-index:50}
.sp429-row{min-height:78px;padding:0 18px;display:flex;align-items:center;gap:10px;box-sizing:border-box;width:100%;overflow:visible}
.sp429-brand{display:flex;align-items:center;gap:10px;flex:0 0 auto;margin-right:4px;white-space:nowrap;min-width:0}
.sp429-star{font-size:27px;color:#20e6ff;line-height:1;text-shadow:0 0 16px rgba(32,230,255,.52)}
.sp429-title{color:#f5f8fc;font-weight:950;font-size:12px;letter-spacing:.55px;line-height:1.2}
.sp429-sub{color:#20e6ff;font-weight:850;font-size:7px;letter-spacing:1.55px;line-height:1.2;margin-top:4px}
.sp429-menu{display:flex;align-items:center;gap:2px;flex:1 1 auto;min-width:0;padding:6px;background:rgba(4,17,29,.55);border:1px solid rgba(83,132,166,.14);border-radius:14px}
.sp429-item{position:relative;height:46px;padding:0 7px;display:flex;align-items:center;justify-content:center;gap:8px;color:#9fb4c7!important;text-decoration:none!important;font-size:9.8px;font-weight:850;white-space:nowrap;box-sizing:border-box;border:1px solid transparent;border-radius:10px;transition:.16s ease}
.sp429-item svg,.sp429-mitem svg,.sp429-menu-button svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none}
.sp429-item:hover{color:#f4fbff!important;background:rgba(23,68,98,.42);border-color:rgba(119,174,209,.20);transform:translateY(-1px)}
.sp429-item.sp429-active{color:#fff!important;background:linear-gradient(135deg,rgba(0,157,255,.28),rgba(32,230,255,.11));border-color:rgba(32,230,255,.68);box-shadow:inset 0 1px 0 rgba(255,255,255,.08),0 0 0 1px rgba(32,230,255,.08),0 7px 22px rgba(0,154,255,.16),0 0 18px rgba(32,230,255,.10);padding:0 9px}
.sp429-item.sp429-active:after{content:"";position:absolute;left:18%;right:18%;bottom:-8px;height:3px;border-radius:99px;background:linear-gradient(90deg,transparent,#20e6ff,transparent);box-shadow:0 0 9px rgba(32,230,255,.85)}
.sp429-item.sp429-active svg{color:#20e6ff;filter:drop-shadow(0 0 5px rgba(32,230,255,.60));stroke-width:2}
.sp429-user{margin-left:auto;display:flex;align-items:center;gap:10px;flex:0 0 auto;padding-left:8px}
.sp429-usertext{text-align:right;line-height:1.05;max-width:145px}.sp429-name{color:#f5f8fc;font-size:12px;font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sp429-role{color:#20e6ff;font-size:10px;font-weight:800;letter-spacing:.45px;margin-top:3px}
.sp429-avatar{box-sizing:border-box;width:40px;height:40px;border-radius:50%;object-fit:cover;border:1.5px solid #20e6ff;box-shadow:0 0 12px rgba(32,230,255,.22);background:#0c3554}
.sp429-initials{display:flex;align-items:center;justify-content:center;color:#20e6ff;font-size:12px;font-weight:950}
.sp429-profile-link{display:flex;text-decoration:none!important;border-radius:50%}

/* Mobile markup is always rendered but hidden on desktop. */
.sp429-mobilebar{display:none}

@media(max-width:1350px){.sp429-row{gap:10px;padding:0 12px}.sp429-brand{margin-right:4px}.sp429-menu{gap:3px;padding:5px}.sp429-item{padding:0 9px}.sp429-usertext{display:none}}

/* REAL MOBILE NAV: menu button + dropdown + overlapping profile avatar */
@media(max-width:900px){
  .sp429-desktop{display:none!important}
  .sp429-mobilebar{display:block!important;position:relative;padding:12px 68px 11px 12px;min-height:88px;box-sizing:border-box;overflow:visible!important}
  .sp429-shell{min-height:88px;border-radius:0 0 16px 16px;margin-bottom:30px!important;overflow:visible!important}
  .sp429-mobile-brand{display:flex;align-items:center;gap:9px;min-width:0;padding-right:4px;margin-bottom:10px}
  .sp429-mobile-brand .sp429-star{font-size:23px;flex:none}
  .sp429-mobile-brand .sp429-title{font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.38px}
  .sp429-mobile-brand .sp429-sub{font-size:6px;letter-spacing:1.15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .sp429-details{position:relative;width:max-content;max-width:100%;margin:0;padding:0}
  .sp429-details>summary{list-style:none;-webkit-tap-highlight-color:transparent}
  .sp429-details>summary::-webkit-details-marker{display:none}
  .sp429-menu-button{height:37px;min-width:104px;padding:0 13px;display:inline-flex;align-items:center;justify-content:center;gap:8px;cursor:pointer;border-radius:10px;border:1px solid rgba(32,230,255,.58);background:linear-gradient(135deg,rgba(0,157,255,.24),rgba(32,230,255,.10));color:#f6fbff;font-size:10px;font-weight:950;letter-spacing:.08em;box-shadow:0 0 18px rgba(0,169,255,.10)}
  .sp429-menu-button svg{color:#20e6ff;width:18px;height:18px}
  .sp429-details[open] .sp429-menu-button{border-color:#20e6ff;box-shadow:0 0 0 1px rgba(32,230,255,.10),0 0 22px rgba(32,230,255,.15)}
  .sp429-dropdown{position:absolute;left:0;top:44px;width:min(300px,calc(100vw - 28px));padding:8px;display:grid;grid-template-columns:1fr 1fr;gap:6px;background:rgba(4,17,29,.985);border:1px solid rgba(32,230,255,.34);border-radius:13px;box-shadow:0 18px 45px rgba(0,0,0,.50),0 0 28px rgba(0,164,255,.08);z-index:99999}
  .sp429-mitem{min-height:44px;padding:7px 9px;display:flex;align-items:center;gap:8px;color:#a9bfd1!important;text-decoration:none!important;font-size:10px;font-weight:850;border:1px solid rgba(105,153,187,.14);border-radius:9px;background:rgba(9,31,49,.62);box-sizing:border-box}
  .sp429-mitem svg{width:16px;height:16px;color:#65cfff}
  .sp429-mitem.sp429-active{color:#fff!important;border-color:rgba(32,230,255,.60);background:linear-gradient(135deg,rgba(0,157,255,.26),rgba(32,230,255,.09));box-shadow:inset 0 1px 0 rgba(255,255,255,.05)}
  .sp429-mobile-profile{position:absolute!important;right:12px!important;bottom:-24px!important;width:56px!important;height:56px!important;border-radius:50%!important;z-index:100000!important;display:flex!important;align-items:center!important;justify-content:center!important;text-decoration:none!important;filter:none!important}
  .sp429-mobile-profile .sp429-avatar{width:56px!important;height:56px!important;border:2px solid #20e6ff!important;box-shadow:0 0 0 4px #05131f,0 0 20px rgba(32,230,255,.42)!important}
  .sp429-mobile-profile:after{content:"";position:absolute;right:-1px;bottom:1px;width:14px;height:14px;border-radius:50%;background:#20e6ff;border:3px solid #05131f;box-sizing:border-box}
}

/* iPhone/Android UA fallback in case the WebView reports a desktop-like viewport. */
.sp429-force-mobile .sp429-desktop{display:none!important}
.sp429-force-mobile .sp429-mobilebar{display:block!important;position:relative;padding:12px 68px 11px 12px;min-height:88px;box-sizing:border-box;overflow:visible!important}
.sp429-force-mobile.sp429-shell{min-height:88px;border-radius:0 0 16px 16px;margin-bottom:30px!important;overflow:visible!important}
.sp429-force-mobile .sp429-mobile-brand{display:flex;align-items:center;gap:9px;min-width:0;padding-right:4px;margin-bottom:10px}
.sp429-force-mobile .sp429-mobile-brand .sp429-star{font-size:23px;flex:none}
.sp429-force-mobile .sp429-mobile-brand .sp429-title{font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.38px}
.sp429-force-mobile .sp429-mobile-brand .sp429-sub{font-size:6px;letter-spacing:1.15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sp429-force-mobile .sp429-details{position:relative;width:max-content;max-width:100%;margin:0;padding:0}
.sp429-force-mobile .sp429-details>summary{list-style:none;-webkit-tap-highlight-color:transparent}.sp429-force-mobile .sp429-details>summary::-webkit-details-marker{display:none}
.sp429-force-mobile .sp429-menu-button{height:37px;min-width:104px;padding:0 13px;display:inline-flex;align-items:center;justify-content:center;gap:8px;cursor:pointer;border-radius:10px;border:1px solid rgba(32,230,255,.58);background:linear-gradient(135deg,rgba(0,157,255,.24),rgba(32,230,255,.10));color:#f6fbff;font-size:10px;font-weight:950;letter-spacing:.08em;box-shadow:0 0 18px rgba(0,169,255,.10)}
.sp429-force-mobile .sp429-menu-button svg{color:#20e6ff;width:18px;height:18px}
.sp429-force-mobile .sp429-dropdown{position:absolute;left:0;top:44px;width:min(300px,calc(100vw - 28px));padding:8px;display:grid;grid-template-columns:1fr 1fr;gap:6px;background:rgba(4,17,29,.985);border:1px solid rgba(32,230,255,.34);border-radius:13px;box-shadow:0 18px 45px rgba(0,0,0,.50),0 0 28px rgba(0,164,255,.08);z-index:99999}
.sp429-force-mobile .sp429-mitem{min-height:44px;padding:7px 9px;display:flex;align-items:center;gap:8px;color:#a9bfd1!important;text-decoration:none!important;font-size:10px;font-weight:850;border:1px solid rgba(105,153,187,.14);border-radius:9px;background:rgba(9,31,49,.62);box-sizing:border-box}
.sp429-force-mobile .sp429-mitem svg{width:16px;height:16px;color:#65cfff}.sp429-force-mobile .sp429-mitem.sp429-active{color:#fff!important;border-color:rgba(32,230,255,.60);background:linear-gradient(135deg,rgba(0,157,255,.26),rgba(32,230,255,.09))}
.sp429-force-mobile .sp429-mobile-profile{position:absolute!important;right:12px!important;bottom:-24px!important;width:56px!important;height:56px!important;border-radius:50%!important;z-index:100000!important;display:flex!important;align-items:center!important;justify-content:center!important;text-decoration:none!important}
.sp429-force-mobile .sp429-mobile-profile .sp429-avatar{width:56px!important;height:56px!important;border:2px solid #20e6ff!important;box-shadow:0 0 0 4px #05131f,0 0 20px rgba(32,230,255,.42)!important}
.sp429-force-mobile .sp429-mobile-profile:after{content:"";position:absolute;right:-1px;bottom:1px;width:14px;height:14px;border-radius:50%;background:#20e6ff;border:3px solid #05131f;box-sizing:border-box}
</style>'''

    # IMPORTANT: keep the first HTML tag at column 0. Markdown treats lines
    # indented by four spaces as a code block, which would print the navbar HTML.
    desktop = f'''<div class="sp429-row sp429-desktop">
<div class="sp429-brand">
<div class="sp429-star">✦</div>
<div><div class="sp429-title">ANÁLISE • EVOLUÇÃO • PERFORMANCE</div><div class="sp429-sub">SKATEBOARDING PERFORMANCE SYSTEM</div></div>
</div>
<div class="sp429-menu">{"".join(desktop_links)}</div>
<div class="sp429-user">
<div class="sp429-usertext"><div class="sp429-name">{html.escape(nav_name)}</div><div class="sp429-role">{html.escape(nav_role)}</div></div>
<a class="sp429-profile-link" href="/Meu_Perfil" target="_self" aria-label="Meu Perfil">{avatar}</a>
</div>
</div>'''

    mobile = f'''<div class="sp429-mobilebar">
<div class="sp429-mobile-brand">
<div class="sp429-star">✦</div>
<div style="min-width:0"><div class="sp429-title">ANÁLISE • EVOLUÇÃO • PERFORMANCE</div><div class="sp429-sub">SKATEBOARDING PERFORMANCE SYSTEM</div></div>
</div>
<details class="sp429-details">
<summary class="sp429-menu-button">{SVG['menu']}<span>MENU</span></summary>
<div class="sp429-dropdown">{"".join(mobile_links)}</div>
</details>
<a class="sp429-mobile-profile" href="/Meu_Perfil" target="_self" aria-label="Abrir Meu Perfil">{avatar}</a>
</div>'''

    body = f'<nav class="sp429-shell{force_mobile}" data-key="{html.escape(str(key), quote=True)}">{desktop}{mobile}</nav>'
    st.markdown(css + body, unsafe_allow_html=True)
