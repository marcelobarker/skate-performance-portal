import html
import streamlit as st
PAGES=[("Home","home","/"),("Times","shield","/Times"),("Histórico","history","/Historico_de_Treinos"),("Codificar","code","/Codificar_Sessao"),("Feed","feed","/Feed"),("Central","coach","/Central_do_Treinador"),("Livro","book","/Livro_de_Manobras"),("Administração","admin","/Cadastros")]
SVG={
"home":'<svg viewBox="0 0 24 24"><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5"/><path d="M9.5 20v-6h5v6"/></svg>',
"analytics":'<svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="1.5"/><path d="M8 16v-4M12 16V8M16 16v-6"/></svg>',
"groups":'<svg viewBox="0 0 24 24"><circle cx="9" cy="9" r="3"/><circle cx="17" cy="10" r="2.3"/><path d="M3.5 19c.6-3.1 2.5-4.7 5.5-4.7s4.9 1.6 5.5 4.7M14 15c2.9-.5 5 .8 6 3.4"/></svg>',
"shield":'<svg viewBox="0 0 24 24"><path d="M12 3 19 6v5.3c0 4.5-2.7 7.7-7 9.7-4.3-2-7-5.2-7-9.7V6l7-3Z"/></svg>',
"history":'<svg viewBox="0 0 24 24"><path d="M4 12a8 8 0 1 0 2.3-5.7L4 8.6"/><path d="M4 4v4.6h4.6M12 8v4l3 2"/></svg>',
"code":'<svg viewBox="0 0 24 24"><path d="m8 9-4 3 4 3M16 9l4 3-4 3M14 5l-4 14"/></svg>',
"feed":'<svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="3"/><circle cx="9" cy="9" r="1"/><path d="M8 16c1.2-2 2.6-3 4-3s2.8 1 4 3"/></svg>',
"coach":'<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="3"/><path d="M6 20c.7-4 2.7-6 6-6s5.3 2 6 6M4 5h3M17 5h3"/></svg>',
"book":'<svg viewBox="0 0 24 24"><path d="M4 5.5A3.5 3.5 0 0 1 7.5 2H20v17H7.5A3.5 3.5 0 0 0 4 22z"/><path d="M4 5.5V22M8 6h8M8 10h8"/></svg>',
"admin":'<svg viewBox="0 0 24 24"><path d="M12 3 19 6v5c0 4.5-2.7 7.6-7 9.7C7.7 18.6 5 15.5 5 11V6z"/><path d="M9 12l2 2 4-4"/></svg>'}
def render_top_nav(nav_name="Usuário",nav_role="Membro",nav_photo=None,active="Home",key="top_nav"):
    nav_name=str(nav_name or "Usuário").strip(); nav_role=str(nav_role or "Membro").replace("_"," ").title(); nav_photo=str(nav_photo).strip() if nav_photo else None
    initials="".join(p[:1].upper() for p in nav_name.split()[:2]) or "U"; links=[]
    for label,icon,href in PAGES:
        cls=" sp429-active" if label==active else ""; links.append(f'<a class="sp429-item{cls}" href="{href}" target="_self">{SVG[icon]}<span>{html.escape(label)}</span></a>')
    avatar=f'<img class="sp429-avatar" src="{html.escape(nav_photo,quote=True)}" alt="">' if nav_photo else f'<div class="sp429-avatar sp429-initials">{html.escape(initials)}</div>'
    css='''<style>
.sp429-shell{box-sizing:border-box;width:100%;max-width:none;margin:0 0 16px 0;padding:0;background:linear-gradient(180deg,#071827 0%,#05131f 100%);border:1px solid #163b59;border-radius:0 0 14px 14px;min-height:78px;font-family:"Segoe UI Variable",Inter,Manrope,Arial,sans-serif;box-shadow:0 8px 28px rgba(0,0,0,.16)}
.sp429-row{min-height:78px;padding:0 18px;display:flex;align-items:center;gap:10px;box-sizing:border-box;width:100%;overflow:visible}
.sp429-brand{display:flex;align-items:center;gap:10px;flex:0 0 auto;margin-right:4px;white-space:nowrap}.sp429-star{font-size:27px;color:#20e6ff;line-height:1;text-shadow:0 0 16px rgba(32,230,255,.52)}.sp429-title{color:#f5f8fc;font-weight:950;font-size:12px;letter-spacing:.55px;line-height:1.2}.sp429-sub{color:#20e6ff;font-weight:850;font-size:7px;letter-spacing:1.55px;line-height:1.2;margin-top:4px}
.sp429-menu{display:flex;align-items:center;gap:2px;flex:1 1 auto;min-width:0;padding:6px;background:rgba(4,17,29,.55);border:1px solid rgba(83,132,166,.14);border-radius:14px}
.sp429-item{position:relative;height:46px;padding:0 7px;display:flex;align-items:center;justify-content:center;gap:8px;color:#9fb4c7!important;text-decoration:none!important;font-size:9.8px;font-weight:850;white-space:nowrap;box-sizing:border-box;border:1px solid transparent;border-radius:10px;transition:transform .16s ease,color .16s ease,background .16s ease,border-color .16s ease,box-shadow .16s ease}
.sp429-item svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none;transition:filter .16s ease,transform .16s ease}
.sp429-item:hover{color:#f4fbff!important;background:rgba(23,68,98,.42);border-color:rgba(119,174,209,.20);transform:translateY(-1px)}.sp429-item:hover svg{transform:scale(1.04)}
.sp429-item.sp429-active{color:#ffffff!important;background:linear-gradient(135deg,rgba(0,157,255,.28),rgba(32,230,255,.11));border-color:rgba(32,230,255,.68);box-shadow:inset 0 1px 0 rgba(255,255,255,.08),0 0 0 1px rgba(32,230,255,.08),0 7px 22px rgba(0,154,255,.16),0 0 18px rgba(32,230,255,.10);padding:0 9px;text-shadow:0 0 10px rgba(255,255,255,.08)}
.sp429-item.sp429-active:after{content:"";position:absolute;left:18%;right:18%;bottom:-8px;height:3px;border-radius:99px;background:linear-gradient(90deg,transparent,#20e6ff,transparent);box-shadow:0 0 9px rgba(32,230,255,.85)}
.sp429-item.sp429-active svg{color:#20e6ff;filter:drop-shadow(0 0 5px rgba(32,230,255,.60));stroke-width:2}
.sp429-user{margin-left:auto;display:flex;align-items:center;gap:10px;flex:0 0 auto;padding-left:8px}.sp429-usertext{text-align:right;line-height:1.05;max-width:145px}.sp429-name{color:#f5f8fc;font-size:12px;font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sp429-role{color:#20e6ff;font-size:10px;font-weight:800;letter-spacing:.45px;margin-top:3px}.sp429-avatar{box-sizing:border-box;width:40px;height:40px;border-radius:50%;object-fit:cover;border:1.5px solid #20e6ff;box-shadow:0 0 12px rgba(32,230,255,.22)}.sp429-initials{display:flex;align-items:center;justify-content:center;background:#0c3554;color:#20e6ff;font-size:12px;font-weight:950}
@media(max-width:1350px){.sp429-row{gap:10px;padding:0 12px}.sp429-brand{margin-right:4px}.sp429-menu{gap:3px;padding:5px}.sp429-item{padding:0 9px}.sp429-usertext{display:none}}

@media(max-width:700px){
 .sp429-shell{margin-bottom:12px;border-radius:0 0 12px 12px;min-height:auto;overflow:hidden}
 .sp429-row{min-height:auto;padding:12px 12px 10px;display:grid;grid-template-columns:1fr;gap:10px}
 .sp429-brand{width:100%;margin:0;padding:0 2px}
 .sp429-star{font-size:22px}.sp429-title{font-size:10px}.sp429-sub{font-size:6px;letter-spacing:1.2px}
 .sp429-menu{width:100%;max-width:100%;overflow-x:auto;overflow-y:hidden;justify-content:flex-start;gap:5px;padding:5px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
 .sp429-menu::-webkit-scrollbar{display:none}
 .sp429-item{height:42px;min-width:max-content;padding:0 12px;font-size:10px;border-radius:10px}
 .sp429-item svg{width:15px;height:15px}
 .sp429-item.sp429-active{padding:0 13px}
 .sp429-item.sp429-active:after{bottom:-5px}
 .sp429-user{display:none}
}
</style>''' 
    body=f'<nav class="sp429-shell" data-key="{html.escape(str(key),quote=True)}"><div class="sp429-row"><div class="sp429-brand"><div class="sp429-star">✦</div><div><div class="sp429-title">ANÁLISE • EVOLUÇÃO • PERFORMANCE</div><div class="sp429-sub">SKATEBOARDING PERFORMANCE SYSTEM</div></div></div><div class="sp429-menu">{"".join(links)}</div><div class="sp429-user"><div class="sp429-usertext"><div class="sp429-name">{html.escape(nav_name)}</div><div class="sp429-role">{html.escape(nav_role)}</div></div>{avatar}</div></div></nav>'
    st.markdown(css+body,unsafe_allow_html=True)
