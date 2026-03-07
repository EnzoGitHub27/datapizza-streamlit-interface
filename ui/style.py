# ui/style.py
# DeepAiUG v1.12.2 - Theme System (Matrix + Business Modern)
# ============================================================================


def inject_theme() -> None:
    """Inietta il tema configurato (Matrix o Business Modern)."""
    from config.branding import THEME, MATRIX_RAIN_ENABLED, MATRIX_RAIN_INTENSITY

    if THEME == "matrix":
        inject_matrix_style()
    else:  # business_modern (default)
        from ui.business_style import inject_business_style
        inject_business_style()


def inject_matrix_style() -> None:
    """Inietta il tema Matrix nell'app Streamlit."""
    _inject_matrix_css()
    if MATRIX_RAIN_ENABLED:
        _inject_matrix_rain(MATRIX_RAIN_INTENSITY)


def _inject_matrix_css() -> None:
    """Inject Matrix CSS variables, scanlines, and component styles."""
    import streamlit as st

    st.markdown("""<style>
    /* === FONT IMPORT === */
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Cinzel:wght@700;900&family=Exo+2:wght@300;400;600&display=swap');

    /* === VARIABILI === */
    :root {
      --matrix-green: #00ff41;
      --teal: #00d4aa;
      --teal-dark: #009977;
      --bg: #020c06;
      --bg-card: rgba(0, 20, 12, 0.92);
      --text: #c8ffd4;
      --text-dim: #4a8a5a;
      --border: rgba(0, 212, 170, 0.2);
    }

    /* === APP BACKGROUND === */
    .stApp { background: #020c06 !important; color: #c8ffd4 !important; }

    /* === SCANLINES OVERLAY === */
    .stApp::before {
      content: '';
      position: fixed; top: 0; left: 0; right: 0; bottom: 0;
      background: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,0,0,0.025) 2px, rgba(0,0,0,0.025) 4px
      );
      pointer-events: none; z-index: 9998;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
      background: rgba(0, 15, 8, 0.97) !important;
      border-right: 1px solid rgba(0, 212, 170, 0.2) !important;
    }

    /* === TITOLO H1 con GLITCH === */
    .stApp h1 {
      font-family: 'Cinzel', serif !important;
      color: #00d4aa !important;
      position: relative;
      animation: glitch 4s infinite;
    }
    @keyframes glitch {
      0%, 89%, 100% { transform: translate(0); }
      90% { transform: translate(-2px, 1px); color: #ff0040; }
      92% { transform: translate(2px, -1px); color: #00ffff; }
      94% { transform: translate(0); color: #00d4aa; }
    }

    /* === H2, H3 === */
    .stApp h2, .stApp h3 {
      font-family: 'Exo 2', sans-serif !important;
      color: #00d4aa !important;
    }

    /* === CHAT BUBBLES === */
    [data-testid="stChatMessage"] {
      background: rgba(0, 20, 12, 0.92) !important;
      border: 1px solid rgba(0, 212, 170, 0.2) !important;
      border-radius: 4px !important;
      font-family: 'Exo 2', sans-serif !important;
    }

    /* === BOTTONI === */
    .stButton > button {
      background: transparent !important;
      border: 1px solid #00d4aa !important;
      color: #00d4aa !important;
      font-family: 'Share Tech Mono', monospace !important;
      border-radius: 2px !important;
      transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
      background: rgba(0, 212, 170, 0.12) !important;
      border-color: #00ff41 !important;
      color: #00ff41 !important;
      box-shadow: 0 0 8px rgba(0, 212, 170, 0.4) !important;
    }

    /* === INPUT / TEXTAREA === */
    .stTextArea textarea, .stTextInput input {
      background: rgba(0, 20, 12, 0.85) !important;
      border: 1px solid rgba(0, 212, 170, 0.3) !important;
      color: #c8ffd4 !important;
      font-family: 'Share Tech Mono', monospace !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
      border-color: #00d4aa !important;
      box-shadow: 0 0 6px rgba(0, 212, 170, 0.3) !important;
    }

    /* === SELECTBOX === */
    [data-testid="stSelectbox"] > div {
      background: rgba(0, 20, 12, 0.85) !important;
      border: 1px solid rgba(0, 212, 170, 0.3) !important;
      color: #c8ffd4 !important;
      font-family: 'Share Tech Mono', monospace !important;
    }

    /* === EXPANDER === */
    .streamlit-expanderHeader, [data-testid="stExpanderToggleIcon"] {
      font-family: 'Share Tech Mono', monospace !important;
      color: #00d4aa !important;
    }

    /* === METRIC === */
    [data-testid="stMetric"] {
      font-family: 'Share Tech Mono', monospace !important;
      color: #00d4aa !important;
    }

    /* === CAPTION === */
    [data-testid="stCaptionContainer"] {
      font-family: 'Share Tech Mono', monospace !important;
      color: #4a8a5a !important;
    }

    /* === ALERT / INFO BANNER === */
    .stAlert {
      background: rgba(0, 20, 12, 0.85) !important;
      border: 1px solid rgba(0, 212, 170, 0.2) !important;
      color: #c8ffd4 !important;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar { width: 3px; height: 3px; }
    ::-webkit-scrollbar-track { background: #020c06; }
    ::-webkit-scrollbar-thumb { background: #00d4aa; border-radius: 2px; }

    /* === RIDUCE SPAZIO SOPRA IL TITOLO === */
    .block-container {
      padding-top: 1.5rem !important;
    }

    </style>""", unsafe_allow_html=True)


def _inject_matrix_rain(intensity: float = 0.055) -> None:
    """Inietta il canvas Matrix rain nel documento parent (escape dall'iframe)."""
    import streamlit.components.v1 as components

    components.html(f"""
    <script>
    (function() {{
        const existing = window.parent.document.getElementById('matrix-rain');
        if (existing) existing.remove();
        const canvas = window.parent.document.createElement('canvas');
        canvas.id = 'matrix-rain';
        canvas.style.cssText = [
            'position:fixed', 'top:0', 'left:0',
            'width:100vw', 'height:100vh',
            'z-index:0', 'opacity:{intensity}',
            'pointer-events:none'
        ].join(';');
        window.parent.document.body.appendChild(canvas);
        const ctx = canvas.getContext('2d');
        canvas.width = window.parent.innerWidth;
        canvas.height = window.parent.innerHeight;
        const chars = 'アイウエオカキクケコ0123456789ABCDEF∑∏∫φψω'.split('');
        const fs = 13;
        let drops = Array(Math.floor(canvas.width / fs)).fill(1);
        setInterval(() => {{
            ctx.fillStyle = 'rgba(2, 12, 6, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.font = fs + 'px monospace';
            drops.forEach((y, i) => {{
                const char = chars[Math.floor(Math.random() * chars.length)];
                ctx.fillStyle = Math.random() > 0.95 ? '#00d4aa' : '#00ff41';
                ctx.fillText(char, i * fs, y * fs);
                if (y * fs > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }});
        }}, 60);
        window.parent.addEventListener('resize', () => {{
            canvas.width = window.parent.innerWidth;
            canvas.height = window.parent.innerHeight;
        }});
    }})();
    </script>
    """, height=0)
