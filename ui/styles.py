# ui/styles.py
# DeepAiUG v1.14.3 - Stili CSS
# ============================================================================
# 🆕 v1.9.1: Bubble colors use Streamlit CSS variables for automatic theming
# 🆕 v1.9.1: Typography rules for HTML content rendered inside bubbles
# 🆕 v1.14.3: Typing indicator animato (bounce teal)
# ============================================================================

# CSS principale dell'applicazione
MAIN_CSS = """
<style>
/* ── Chat bubbles ──────────────────────────────────────────────────────── */
/* DARK is the DEFAULT — no class or detection needed.                     */
/* Light overrides via @media (prefers-color-scheme: light).               */

.user-bubble {
    background-color: #1a3a5c !important;
    border: 1px solid #254d7a !important;
    color: #f0f0f0 !important;
    padding: 14px 18px !important;
    border-radius: 12px !important;
    margin-bottom: 0.5rem !important;
}

.assistant-bubble {
    background-color: #1e2a35 !important;
    border: 1px solid #2a3a4a !important;
    color: #f0f0f0 !important;
    padding: 14px 18px !important;
    border-radius: 12px !important;
    margin-bottom: 0.5rem !important;
}

.kb-enabled {
    border-left: 4px solid #4CAF50 !important;
    padding-left: 10px !important;
}

/* ── Typography inside bubbles (dark default) ──────────────────────────── */

.user-bubble p,
.assistant-bubble p {
    margin: 0.4rem 0;
    line-height: 1.55;
}

.user-bubble p:first-child,
.assistant-bubble p:first-child { margin-top: 0; }

.user-bubble p:last-child,
.assistant-bubble p:last-child { margin-bottom: 0; }

.user-bubble strong,
.assistant-bubble strong { color: #ffffff; }

.user-bubble a,
.assistant-bubble a { color: #6db3f2; }

.user-bubble code,
.assistant-bubble code {
    background-color: rgba(255,255,255,0.1);
    padding: 0.15rem 0.35rem;
    border-radius: 4px;
    font-size: 0.88em;
}

.user-bubble pre,
.assistant-bubble pre {
    background-color: rgba(0,0,0,0.25);
    padding: 0.75rem;
    border-radius: 6px;
    overflow-x: auto;
    margin: 0.5rem 0;
}

.user-bubble pre code,
.assistant-bubble pre code {
    background: none !important;
    padding: 0;
    font-size: 0.85em;
}

.user-bubble ul, .user-bubble ol,
.assistant-bubble ul, .assistant-bubble ol {
    padding-left: 1.5rem;
    margin: 0.4rem 0;
}

.user-bubble table,
.assistant-bubble table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.5rem 0;
}

.user-bubble th, .user-bubble td,
.assistant-bubble th, .assistant-bubble td {
    border: 1px solid rgba(255,255,255,0.15);
    padding: 0.35rem 0.6rem;
    text-align: left;
}

.user-bubble th,
.assistant-bubble th {
    background-color: rgba(255,255,255,0.08);
    font-weight: 600;
}

.bubble-attachments {
    font-size: 0.85em;
    opacity: 0.8;
    margin-bottom: 0.3rem !important;
}

/* ── Typing indicator (v1.14.3) ───────────────────────────────────────── */

.typing-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 12px 16px;
    margin: 4px 0;
}
.typing-indicator span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #00d4aa;
    display: inline-block;
    animation: typing-bounce 1.2s infinite ease-in-out;
}
.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30%            { transform: translateY(-6px); opacity: 1; }
}

/* ── Light theme overrides ─────────────────────────────────────────────── */

@media (prefers-color-scheme: light) {
    .user-bubble {
        background-color: #e3f2fd !important;
        border-color: #bbdefb !important;
        color: #1a1a1a !important;
    }
    .assistant-bubble {
        background-color: #f5f5f5 !important;
        border-color: #e0e0e0 !important;
        color: #1a1a1a !important;
    }
    .user-bubble strong,
    .assistant-bubble strong { color: inherit; }
    .user-bubble a,
    .assistant-bubble a { color: #1976d2; }
    .user-bubble code,
    .assistant-bubble code { background-color: rgba(0,0,0,0.07); }
    .user-bubble pre,
    .assistant-bubble pre { background-color: rgba(0,0,0,0.05); }
    .user-bubble th, .user-bubble td,
    .assistant-bubble th, .assistant-bubble td {
        border-color: rgba(0,0,0,0.12);
    }
    .user-bubble th,
    .assistant-bubble th { background-color: rgba(0,0,0,0.04); }
}
</style>
"""

# CSS per indicatore Cloud provider (rosso)
CLOUD_INDICATOR_CSS = """
<style>
.stApp { 
    border-top: 4px solid #ff6b6b !important; 
}
</style>
"""

# CSS per indicatore Knowledge Base attiva (verde)
KB_INDICATOR_CSS = """
<style>
.stApp { 
    border-top: 4px solid #4CAF50 !important; 
}
</style>
"""


def get_connection_indicator_css(connection_type: str, use_kb: bool) -> str:
    """
    Ritorna il CSS appropriato per l'indicatore di connessione.
    
    Args:
        connection_type: Tipo di connessione
        use_kb: Se Knowledge Base è attiva
        
    Returns:
        Stringa CSS
    """
    if connection_type == "Cloud provider":
        return CLOUD_INDICATOR_CSS
    elif use_kb:
        return KB_INDICATOR_CSS
    return ""
