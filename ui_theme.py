import streamlit as st

def apply_ui_theme():
    st.markdown(r'''<style>
    :root{--sp-bg:#06111f;--sp-panel:#0b1d31;--sp-panel2:#091827;--sp-line:#245274;--sp-blue:#1398ff;--sp-text:#eef8ff;--sp-muted:#9bb2c8}
    .stApp,[data-testid="stAppViewContainer"]{background:var(--sp-bg)!important;color:var(--sp-text)!important}
    [data-testid="stSidebar"]{background:#081827!important}
    [data-testid="stSidebar"] *{color:#d9eafa!important}
    h1,h2,h3,h4,h5,p,label,span{color:inherit}
    [data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button,
    [data-testid="stFileUploaderDropzone"] button,[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-minimal"]{
      background:#0b1d31!important;color:#eef8ff!important;border:1px solid #245274!important;border-radius:10px!important;box-shadow:none!important
    }
    [data-testid="stButton"] button *,[data-testid="stFormSubmitButton"] button *,[data-testid="stDownloadButton"] button *,
    [data-testid="stFileUploaderDropzone"] button *{color:#eef8ff!important}
    [data-testid="stButton"] button:hover,[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover,
    [data-testid="stFileUploaderDropzone"] button:hover{background:#12304b!important;color:#fff!important;border-color:#1398ff!important}
    [data-testid="stButton"] button:hover *,[data-testid="stFileUploaderDropzone"] button:hover *{color:#fff!important}
    [data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input,[data-testid="stTimeInput"] input,
    [data-testid="stSelectbox"] [role="combobox"],[data-testid="stMultiSelect"] [role="combobox"],textarea,
    [data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{background:#0b1d2d!important;color:#eef8ff!important;border-color:#245274!important}
    [data-testid="stDateInput"] button,[data-testid="stTimeInput"] button{background:#0b1d2d!important;color:#eef8ff!important;border-color:#245274!important}
    [data-testid="stDateInput"] button *{color:#eef8ff!important}
    [data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"],[data-baseweb="calendar"]{background:#081827!important;color:#eef8ff!important}
    [data-baseweb="menu"] li,[role="option"],[data-baseweb="calendar"] button{background:#081827!important;color:#eef8ff!important}
    [data-baseweb="menu"] li:hover,[role="option"]:hover,[data-baseweb="calendar"] button:hover{background:#12304b!important;color:#fff!important}
    [data-testid="stFileUploader"] section,[data-testid="stFileUploaderDropzone"],[data-testid="stFileUploaderFile"]{background:#09192b!important;color:#eef8ff!important;border-color:#245274!important}
    [data-testid="stFileUploader"] *{color:#eef8ff!important}
    /* remove o controle nativo que abre a imagem isolada; o portal usa o botão olho */
    [data-testid="stImage"] button,[data-testid="stImage"] [data-testid="stBaseButton-headerNoPadding"]{display:none!important}
    /* tooltips nunca brancos */
    [role="tooltip"],[data-baseweb="tooltip"]{background:#102b46!important;color:#eef8ff!important;border:1px solid #245274!important}
    [role="tooltip"] *{color:#eef8ff!important}
    @media(max-width:700px){.block-container{padding-left:.8rem!important;padding-right:.8rem!important}.sp-kpi{min-height:128px!important}}
    </style>''', unsafe_allow_html=True)
