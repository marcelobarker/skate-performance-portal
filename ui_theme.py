import streamlit as st

def apply_ui_theme():
    role=(st.session_state.get('profile') or {}).get('role','')
    hide=['03_Analise_de_Treino','08_Livro_de_Manobras','10_Codificar_Sessao','07_Perfil_do_Atleta']
    if role in ('skatista','familiar'): hide.append('12_Central_do_Treinador')
    hide_css=','.join(f'[data-testid="stSidebarNav"] a[href*="{x}"]' for x in hide)
    st.markdown(f'''<style>
    :root{{--bg:#f4f8fc;--surface:#fff;--ink:#10263b;--muted:#71879b;--line:#d9e7f2;--blue:#087cff;--cyan:#00bfe8}}
    html,body,#root,[data-testid="stApp"],[data-testid="stAppViewContainer"]{{background:#f4f8fc!important;color:#10263b!important;font-family:Inter,Roboto,Arial,sans-serif!important}}
    .stApp,[data-testid="stAppViewContainer"]{{background:radial-gradient(circle at 12% 0%,rgba(8,124,255,.08),transparent 28%),linear-gradient(180deg,#fbfdff,#f3f8fc)!important}}
    [data-testid="stHeader"]{{background:rgba(255,255,255,.9)!important;border-bottom:1px solid #e3edf5!important;backdrop-filter:blur(12px)}}
    [data-testid="stToolbar"],[data-testid="stDecoration"],header [data-testid="stStatusWidget"]{{display:none!important}}
    .block-container{{max-width:1480px!important;padding-top:1.15rem!important;padding-left:1.45rem!important;padding-right:1.45rem!important;padding-bottom:2rem!important}}
    [data-testid="stSidebar"]{{background:#fff!important;border-right:1px solid #dbe8f2!important;box-shadow:8px 0 30px rgba(22,72,110,.05)!important}}
    [data-testid="stSidebar"] *{{color:#35516a!important}}
    [data-testid="stSidebarNav"] a{{border-radius:10px!important;margin:3px 8px!important;padding:10px 12px 10px 40px!important;position:relative!important;font-weight:700!important}}
    [data-testid="stSidebarNav"] a:before{{content:"◆";position:absolute;left:14px;top:50%;transform:translateY(-50%);font-size:11px;color:#1497ff;filter:drop-shadow(0 0 4px rgba(8,124,255,.25))}}
    [data-testid="stSidebarNav"] a:hover{{background:#eef7ff!important;color:#087cff!important}}
    [data-testid="stSidebarNav"] a[aria-current="page"]{{background:linear-gradient(90deg,#e7f4ff,#f2f9ff)!important;color:#087cff!important;border:1px solid #c8e6ff!important;box-shadow:0 6px 18px rgba(8,124,255,.08)!important}}
    {hide_css}{{display:none!important}}
    [data-testid="stSidebarCollapsedControl"],button[data-testid="stSidebarCollapsedControl"],[data-testid="stSidebarCollapseButton"]{{display:flex!important;z-index:999999!important;background:#fff!important;color:#087cff!important;border:1px solid #c8e2f5!important;border-radius:10px!important;box-shadow:0 5px 18px rgba(22,72,110,.12)!important}}
    h1,h2,h3,h4,h5,h6{{color:#10263b!important;letter-spacing:-.025em}} small,.stCaption{{color:#71879b!important}}
    [data-testid="stVerticalBlockBorderWrapper"]>div{{background:#fff!important;border-color:#d9e7f2!important;border-radius:16px!important;box-shadow:0 10px 30px rgba(31,78,116,.07)!important}}
    [data-testid="stMetric"]{{background:linear-gradient(145deg,#fff,#f8fbff)!important;border:1px solid #d9e7f2!important;border-radius:14px!important;padding:15px 17px!important;box-shadow:0 8px 24px rgba(31,78,116,.06)!important}}
    [data-testid="stMetricLabel"] p{{color:#71879b!important}} [data-testid="stMetricValue"],[data-testid="stMetricValue"] div{{color:#10263b!important}}
    [data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button,[data-testid="stFileUploaderDropzone"] button,[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-minimal"],[data-testid="stPageLink"] a{{min-height:42px;background:#fff!important;color:#087cff!important;border:1px solid #bcdcf4!important;border-radius:10px!important;box-shadow:0 5px 15px rgba(31,78,116,.06)!important;font-weight:800!important;transition:.18s ease!important}}
    [data-testid="stFormSubmitButton"] button[kind="primary"],[data-testid="stButton"] button[kind="primary"]{{background:linear-gradient(135deg,#1497ff,#006aff)!important;border-color:#087cff!important;color:#fff!important;box-shadow:0 8px 22px rgba(8,124,255,.22)!important}}
    [data-testid="stButton"] button:hover,[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover,[data-testid="stPageLink"] a:hover{{transform:translateY(-1px)!important;border-color:#29a8ff!important;box-shadow:0 8px 22px rgba(8,124,255,.14)!important}}
    [data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input,[data-testid="stTimeInput"] input,[data-testid="stSelectbox"] [role="combobox"],[data-testid="stMultiSelect"] [role="combobox"],textarea,[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{{background:#fff!important;color:#10263b!important;border-color:#d4e3ee!important;border-radius:10px!important}}
    [data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"],[data-baseweb="calendar"]{{background:#fff!important;color:#10263b!important;border-color:#d9e7f2!important}}
    [data-baseweb="menu"] li,[role="option"],[data-baseweb="calendar"] button{{background:#fff!important;color:#10263b!important}}
    [data-baseweb="menu"] li:hover,[role="option"]:hover,[data-baseweb="calendar"] button:hover{{background:#eef7ff!important;color:#087cff!important}}
    [data-testid="stFileUploader"] section,[data-testid="stFileUploaderDropzone"],[data-testid="stFileUploaderFile"]{{background:#f8fbff!important;color:#10263b!important;border:1px dashed #9fcbea!important;border-radius:12px!important}}
    [data-testid="stTabs"] [role="tablist"]{{border-bottom:1px solid #d9e7f2!important}} [data-testid="stTabs"] button{{color:#60798e!important}} [data-testid="stTabs"] button[aria-selected="true"]{{color:#087cff!important;border-bottom-color:#087cff!important}}
    [data-testid="stDialog"]>div{{background:#fff!important;border:1px solid #d9e7f2!important;border-radius:16px!important;box-shadow:0 18px 60px rgba(31,78,116,.18)!important}}
    @media(max-width:768px){{.block-container{{padding-left:.75rem!important;padding-right:.75rem!important}}[data-testid="stSidebar"]{{border-right:none!important}}}}
    </style>''',unsafe_allow_html=True)
