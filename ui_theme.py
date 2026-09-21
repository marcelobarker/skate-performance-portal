import streamlit as st

def apply_ui_theme():
    st.markdown(r'''<style>
    :root{
      --bg-deep:#020B14;--bg-main:#03111E;--bg-panel:#061727;--bg-card:#081B2D;--bg-elev:#0B2136;--bg-input:#10263B;--bg-hover:#102C46;
      --primary:#087CFF;--primary-bright:#159BFF;--cyan:#00D9FF;--purple:#9B35F5;--green:#00C878;--orange:#F07B00;
      --text:#F5F8FC;--text2:#C4D1DF;--muted:#8499AD;--disabled:#60758A;--border:rgba(50,130,190,.25);--border-active:rgba(0,145,255,.60);
      --r-sm:7px;--r-md:9px;--r-lg:12px;--shadow:0 8px 24px rgba(0,0,0,.20);--blue-shadow:0 0 18px rgba(0,120,255,.25)
    }
    html,body,#root,[data-testid="stApp"],[class*="css"]{font-family:Inter,Roboto,Arial,sans-serif!important;background:#03111E!important;background-color:#03111E!important} html{background:#03111E!important} body{background:#03111E!important}
    .stApp,[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 20% 0%,rgba(0,110,255,.08),transparent 35%),linear-gradient(180deg,var(--bg-main),var(--bg-deep))!important;color:var(--text)!important}
    [data-testid="stHeader"]{background:transparent!important;box-shadow:none!important}
    [data-testid="stToolbar"],[data-testid="stDecoration"],header [data-testid="stStatusWidget"]{display:none!important}
    [data-testid="stSidebarCollapsedControl"],button[data-testid="stSidebarCollapsedControl"],[data-testid="stSidebarCollapseButton"]{display:flex!important;position:relative!important;z-index:999999!important;background:#08233A!important;color:#fff!important;border:1px solid #159BFF!important;border-radius:8px!important;box-shadow:0 0 14px rgba(0,124,255,.18)!important}
    [data-testid="stSidebarCollapsedControl"] *{color:#fff!important}
    .block-container{max-width:1480px!important;padding-top:1.05rem!important;padding-left:1.45rem!important;padding-right:1.45rem!important;padding-bottom:2rem!important}
    [data-testid="stSidebar"]{background:rgba(2,12,23,.98)!important;border-right:1px solid rgba(30,130,200,.28)!important}
    [data-testid="stSidebar"] *{color:var(--text2)!important}
    [data-testid="stSidebarNav"] a{border-radius:8px!important;margin:3px 7px!important;padding:9px 11px!important}
    [data-testid="stSidebarNav"] a{position:relative!important;padding-left:40px!important}
    [data-testid="stSidebarNav"] a:before{content:"◆";position:absolute;left:13px;top:50%;transform:translateY(-50%);font-size:13px;color:#29dfff;filter:drop-shadow(0 0 5px #087cff)}
    [data-testid="stSidebarNav"] a[href*="Times"]:before{content:"●"}
    [data-testid="stSidebarNav"] a[href*="Analise"]:before{content:"●"}
    [data-testid="stSidebarNav"] a[href*="Historico"]:before{content:"●"}
    [data-testid="stSidebarNav"] a[href*="Perfil"]:before{content:"●"}
    [data-testid="stSidebarNav"] a[href*="Calendario"]:before{content:"●"}
    [data-testid="stSidebarNav"] a[href*="Perfil_do_Atleta"]:before{content:"◉"}
    [data-testid="stSidebarNav"] a[href*="Livro_de_Manobras"]:before{content:"●"}
    [data-testid="stSidebarNav"] a[href*="Enviar_Manobra"]:before{content:"●"}
    [data-testid="stSidebarNav"] a:hover{background:rgba(20,80,125,.20)!important;color:#fff!important}
    [data-testid="stSidebarNav"] a[aria-current="page"]{background:linear-gradient(90deg,rgba(0,110,235,.75),rgba(0,70,160,.55))!important;border:1px solid rgba(0,140,255,.40)!important;box-shadow:0 0 12px rgba(0,100,255,.15)!important}
    h1,h2,h3,h4,h5,h6{color:var(--text)!important;letter-spacing:-.02em} p,label,span{color:inherit} small,.stCaption{color:var(--muted)!important}
    [data-testid="stVerticalBlockBorderWrapper"]>div{background:linear-gradient(145deg,rgba(8,27,45,.96),rgba(5,20,34,.96))!important;border-color:var(--border)!important;border-radius:12px!important;box-shadow:var(--shadow)!important}
    [data-testid="stMetric"]{background:linear-gradient(145deg,var(--bg-card),var(--bg-panel))!important;border:1px solid var(--border)!important;border-radius:10px!important;padding:14px 16px!important;box-shadow:var(--shadow)!important}
    [data-testid="stMetricLabel"] p{color:var(--muted)!important}[data-testid="stMetricValue"],[data-testid="stMetricValue"] div{color:var(--text)!important}
    [data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button,[data-testid="stFileUploaderDropzone"] button,[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-minimal"]{
      min-height:40px;background:linear-gradient(180deg,#0d2b46,#08233A)!important;color:#dff6ff!important;border:1px solid #135C91!important;border-radius:8px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.04)!important;font-weight:650!important;transition:.18s ease!important
    }
    [data-testid="stFormSubmitButton"] button[kind="primary"],[data-testid="stButton"] button[kind="primary"]{background:linear-gradient(180deg,#1497FF 0%,#006AFF 55%,#0758EE 100%)!important;border-color:rgba(70,180,255,.70)!important;color:#fff!important;box-shadow:0 4px 15px rgba(0,105,255,.28),inset 0 1px 0 rgba(255,255,255,.18)!important}
    [data-testid="stButton"] button *,[data-testid="stFormSubmitButton"] button *,[data-testid="stDownloadButton"] button *,[data-testid="stFileUploaderDropzone"] button *{color:inherit!important}
    [data-testid="stButton"] button:hover,[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover,[data-testid="stFileUploaderDropzone"] button:hover{filter:brightness(1.08)!important;transform:translateY(-1px)!important;border-color:#00AFFF!important;box-shadow:0 5px 20px rgba(0,125,255,.22)!important;color:#fff!important}
    [data-testid="stButton"] button:disabled{background:#081725!important;color:var(--disabled)!important;border-color:#17344d!important;opacity:.75!important}
    [data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input,[data-testid="stTimeInput"] input,[data-testid="stSelectbox"] [role="combobox"],[data-testid="stMultiSelect"] [role="combobox"],textarea,[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{
      min-height:40px;background:var(--bg-input)!important;color:#EAF3FA!important;border-color:rgba(50,100,145,.32)!important;border-radius:7px!important
    }
    [data-testid="stTextInput"] input:focus,[data-testid="stNumberInput"] input:focus,[data-testid="stDateInput"] input:focus,textarea:focus{border-color:#078EFF!important;box-shadow:0 0 0 2px rgba(0,130,255,.12)!important}
    input::placeholder,textarea::placeholder{color:#70869A!important}
    [data-testid="stDateInput"] button,[data-testid="stTimeInput"] button{background:var(--bg-input)!important;color:#EAF3FA!important;border-color:rgba(50,100,145,.32)!important}
    [data-testid="stDateInput"] button *{color:#EAF3FA!important}
    [data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"],[data-baseweb="calendar"]{background:var(--bg-panel)!important;color:var(--text)!important;border-color:var(--border)!important}
    [data-baseweb="menu"] li,[role="option"],[data-baseweb="calendar"] button{background:var(--bg-panel)!important;color:var(--text)!important}
    [data-baseweb="menu"] li:hover,[role="option"]:hover,[data-baseweb="calendar"] button:hover{background:var(--bg-hover)!important;color:#fff!important}
    [data-testid="stFileUploader"] section,[data-testid="stFileUploaderDropzone"],[data-testid="stFileUploaderFile"]{background:rgba(10,35,55,.55)!important;color:var(--text)!important;border:1px dashed rgba(90,160,210,.65)!important;border-radius:7px!important}
    [data-testid="stFileUploader"] *{color:var(--text)!important}
    [data-testid="stTabs"] [role="tablist"]{gap:8px!important;border-bottom:1px solid var(--border)!important}[data-testid="stTabs"] button{color:#AAB9C8!important}[data-testid="stTabs"] button[aria-selected="true"]{color:var(--cyan)!important;border-bottom-color:#00AFFF!important}
    [data-testid="stImage"] button,[data-testid="stImage"] [data-testid="stBaseButton-headerNoPadding"],[data-testid="stImage"] a,[data-testid="stImage"] [role="button"]{display:none!important}
    [role="tooltip"],[data-baseweb="tooltip"]{background:#102b46!important;color:var(--text)!important;border:1px solid #245274!important}
    [role="tooltip"] *{color:var(--text)!important}
    [data-testid="stDialog"]>div{background:linear-gradient(145deg,rgba(6,25,43,.99),rgba(3,15,27,.99))!important;border:1px solid rgba(0,140,230,.55)!important;border-radius:12px!important;box-shadow:0 16px 50px rgba(0,0,0,.50),0 0 30px rgba(0,120,220,.08)!important}
    [data-testid="stDialog"] button{background:#08233A!important;color:#fff!important;border-color:#135C91!important}
    button:not([data-testid="stSidebarCollapseButton"]){--button-background-color:#08233A!important}
    [data-testid="stPopover"] button,[data-testid="stPageLink"] a{background:#08233A!important;color:#dff6ff!important;border-color:#135C91!important}
    /* V3.2: hard dark rule — no native white controls */
    button,[role="button"],[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-tertiary"],summary,[data-baseweb="select"]>div{background-color:#08233A!important;color:#F5F8FC!important;border-color:#135C91!important}
    button svg,button span,button p,summary span,summary p{color:#F5F8FC!important;fill:currentColor!important}
    [data-baseweb="select"] svg,[data-testid="stSelectbox"] svg{color:#C4D1DF!important;fill:#C4D1DF!important}
    label,legend,[data-testid="stWidgetLabel"] p{color:#C4D1DF!important}
        @media(max-width:768px){html,body,#root,[data-testid="stApp"],[data-testid="stAppViewContainer"]{background:#03111E!important}.block-container{padding-left:.75rem!important;padding-right:.75rem!important}.stColumn{min-width:0!important}[data-testid="stSidebar"]{border-right:none!important}}
    </style>''', unsafe_allow_html=True)
