# ui/business_style.py
# DeepAiUG v1.12.2 - Business Professional Theme
# ============================================================================
# Tema pulito, moderno e professionale per contesti aziendali.
# Colori: Bianco, grigio neutro, blu moderno.
# Font: Sans-serif professionale (Segoe UI, Roboto, system fonts)
# ============================================================================


def inject_business_style() -> None:
    """Inietta il tema Business Moderno nell'app Streamlit."""
    _inject_css()


def _inject_css() -> None:
    """Inject Business Professional CSS."""
    import streamlit as st

    st.markdown("""<style>
    /* === FONT IMPORT === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* === VARIABILI === */
    :root {
      --primary: #0066cc;
      --primary-dark: #0052a3;
      --primary-light: #e6f2ff;
      --bg: #ffffff;
      --bg-secondary: #f8f9fa;
      --bg-card: #ffffff;
      --text: #1a1a1a;
      --text-secondary: #666666;
      --border: #e0e0e0;
      --border-light: #f0f0f0;
      --success: #27ae60;
      --warning: #f39c12;
      --error: #e74c3c;
    }

    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #1a1a1a;
        --bg-secondary: #242424;
        --bg-card: #2a2a2a;
        --text: #f0f0f0;
        --text-secondary: #999999;
        --border: #404040;
        --border-light: #333333;
      }
    }

    /* === APP BACKGROUND === */
    .stApp {
      background: var(--bg) !important;
      color: var(--text) !important;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
      background: var(--bg-secondary) !important;
      border-right: 1px solid var(--border) !important;
    }

    /* === TITOLI === */
    .stApp h1 {
      font-family: 'Inter', sans-serif !important;
      color: var(--text) !important;
      font-weight: 700 !important;
      letter-spacing: -0.5px;
      margin-bottom: 1.5rem !important;
    }

    .stApp h2 {
      font-family: 'Inter', sans-serif !important;
      color: var(--text) !important;
      font-weight: 600 !important;
      margin-bottom: 1rem !important;
    }

    .stApp h3 {
      font-family: 'Inter', sans-serif !important;
      color: var(--text-secondary) !important;
      font-weight: 600 !important;
    }

    /* === TESTO BODY === */
    .stApp p, .stApp li {
      font-family: 'Inter', sans-serif !important;
      font-size: 0.95rem !important;
      line-height: 1.6 !important;
      color: var(--text) !important;
    }

    /* === CHAT BUBBLES === */
    [data-testid="stChatMessage"] {
      background: var(--bg-card) !important;
      border: 1px solid var(--border-light) !important;
      border-radius: 8px !important;
      font-family: 'Inter', sans-serif !important;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }

    /* === BOTTONI === */
    .stButton > button {
      background: var(--primary) !important;
      border: 1px solid var(--primary) !important;
      color: white !important;
      font-family: 'Inter', sans-serif !important;
      font-weight: 500 !important;
      border-radius: 6px !important;
      transition: all 0.2s ease !important;
      padding: 0.5rem 1rem !important;
    }

    .stButton > button:hover {
      background: var(--primary-dark) !important;
      border-color: var(--primary-dark) !important;
      box-shadow: 0 2px 8px rgba(0, 102, 204, 0.25) !important;
    }

    .stButton > button:active {
      transform: translateY(1px) !important;
    }

    /* Secondary Button Style (per socratic buttons) */
    .stButton > button[data-testid="stButton"]:nth-child(1) {
      background: var(--bg-secondary) !important;
      border: 1px solid var(--border) !important;
      color: var(--text) !important;
    }

    .stButton > button[data-testid="stButton"]:nth-child(1):hover {
      background: var(--primary-light) !important;
      border-color: var(--primary) !important;
      color: var(--primary-dark) !important;
    }

    /* === INPUT / TEXTAREA === */
    .stTextArea textarea, .stTextInput input {
      background: var(--bg-card) !important;
      border: 1px solid var(--border) !important;
      color: var(--text) !important;
      font-family: 'Inter', sans-serif !important;
      border-radius: 6px !important;
      padding: 0.75rem !important;
    }

    .stTextArea textarea:focus, .stTextInput input:focus {
      border-color: var(--primary) !important;
      box-shadow: 0 0 0 3px var(--primary-light) !important;
      outline: none !important;
    }

    /* === SELECTBOX === */
    [data-testid="stSelectbox"] > div {
      background: var(--bg-card) !important;
      border: 1px solid var(--border) !important;
      color: var(--text) !important;
      font-family: 'Inter', sans-serif !important;
      border-radius: 6px !important;
    }

    /* === EXPANDER === */
    .streamlit-expanderHeader {
      font-family: 'Inter', sans-serif !important;
      color: var(--text) !important;
      font-weight: 500 !important;
      background: var(--bg-secondary) !important;
      border-radius: 6px !important;
    }

    [data-testid="stExpanderToggleIcon"] {
      color: var(--primary) !important;
    }

    /* === METRIC === */
    [data-testid="stMetric"] {
      font-family: 'Inter', sans-serif !important;
      color: var(--text) !important;
      background: var(--bg-secondary) !important;
      padding: 1rem !important;
      border-radius: 8px !important;
      border: 1px solid var(--border-light) !important;
    }

    [data-testid="stMetricDeltaValue"] {
      color: var(--success) !important;
    }

    /* === ALERT / INFO BANNER === */
    .stAlert {
      background: var(--bg-secondary) !important;
      border: 1px solid var(--border) !important;
      border-left: 4px solid var(--primary) !important;
      color: var(--text) !important;
      border-radius: 6px !important;
      font-family: 'Inter', sans-serif !important;
    }

    .stAlert.info {
      border-left-color: var(--primary) !important;
    }

    .stAlert.success {
      border-left-color: var(--success) !important;
    }

    .stAlert.warning {
      border-left-color: var(--warning) !important;
    }

    .stAlert.error {
      border-left-color: var(--error) !important;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-secondary); }
    ::-webkit-scrollbar-thumb {
      background: var(--border);
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: var(--text-secondary);
    }

    /* === CODE BLOCKS === */
    .stCode {
      background: var(--bg-secondary) !important;
      border: 1px solid var(--border) !important;
      border-radius: 6px !important;
      font-family: 'JetBrains Mono', monospace !important;
    }

    pre {
      background: var(--bg-secondary) !important;
      border: 1px solid var(--border) !important;
      border-radius: 6px !important;
      padding: 1rem !important;
    }

    code {
      font-family: 'JetBrains Mono', monospace !important;
      font-size: 0.9em !important;
      background: rgba(0, 102, 204, 0.1) !important;
      padding: 0.2rem 0.4rem !important;
      border-radius: 3px !important;
      color: var(--primary-dark) !important;
    }

    pre code {
      background: none !important;
      padding: 0 !important;
      color: var(--text) !important;
    }

    /* === TABELLA === */
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 1rem 0;
    }

    th {
      background: var(--bg-secondary) !important;
      border: 1px solid var(--border) !important;
      padding: 0.75rem !important;
      text-align: left;
      font-weight: 600 !important;
      color: var(--text) !important;
    }

    td {
      border: 1px solid var(--border-light) !important;
      padding: 0.75rem !important;
      color: var(--text) !important;
    }

    tr:hover {
      background: var(--primary-light) !important;
    }

    /* === LINK === */
    a {
      color: var(--primary) !important;
      text-decoration: none !important;
      transition: color 0.2s ease !important;
    }

    a:hover {
      color: var(--primary-dark) !important;
      text-decoration: underline !important;
    }

    /* === RIDUCE SPAZIO SOPRA IL TITOLO === */
    .block-container {
      padding-top: 2rem !important;
      padding-bottom: 2rem !important;
    }

    /* === MARGIN / PADDING UTILITIES === */
    .margin-top-1 { margin-top: 1rem !important; }
    .margin-bottom-2 { margin-bottom: 2rem !important; }

    </style>""", unsafe_allow_html=True)
