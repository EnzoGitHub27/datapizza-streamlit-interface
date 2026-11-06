# ui/styles.py
# DeepAiUG v1.14.3 - Stili CSS
# ============================================================================
# 🆕 v1.9.1: Bubble colors use Streamlit CSS variables for automatic theming
# 🆕 v1.9.1: Typography rules for HTML content rendered inside bubbles
# 🆕 v1.14.3: Typing indicator animato (bounce teal)
# 🆕 v1.15.4: Bolle sui contenitori con key (classe st-key-<ruolo>-bubble-N),
#             i blocchi di codice usano lo stile nativo di Streamlit
# ============================================================================

# CSS principale dell'applicazione
MAIN_CSS = """
<style>
/* ── Chat bubbles ──────────────────────────────────────────────────────── */
/* DARK is the DEFAULT — no class or detection needed.                     */
/* Light overrides via @media (prefers-color-scheme: light).               */

[class*="st-key-user-bubble-"] {
    background-color: #1a3a5c !important;
    border: 1px solid #254d7a !important;
    color: #f0f0f0 !important;
    padding: 14px 18px !important;
    border-radius: 12px !important;
    margin-bottom: 0.5rem !important;
}

[class*="st-key-assistant-bubble-"] {
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

[class*="st-key-user-bubble-"] p,
[class*="st-key-assistant-bubble-"] p {
    margin: 0.4rem 0;
    line-height: 1.55;
}

[class*="st-key-user-bubble-"] p:first-child,
[class*="st-key-assistant-bubble-"] p:first-child { margin-top: 0; }

[class*="st-key-user-bubble-"] p:last-child,
[class*="st-key-assistant-bubble-"] p:last-child { margin-bottom: 0; }

[class*="st-key-user-bubble-"] strong,
[class*="st-key-assistant-bubble-"] strong { color: #ffffff; }

[class*="st-key-user-bubble-"] a,
[class*="st-key-assistant-bubble-"] a { color: #6db3f2; }

/* solo il codice in linea: i blocchi (stCode) hanno lo stile nativo di Streamlit */
[class*="st-key-user-bubble-"] code:not([data-testid="stCode"] code),
[class*="st-key-assistant-bubble-"] code:not([data-testid="stCode"] code) {
    background-color: rgba(255,255,255,0.1);
    padding: 0.15rem 0.35rem;
    border-radius: 4px;
    font-size: 0.88em;
}

[class*="st-key-user-bubble-"] ul, [class*="st-key-user-bubble-"] ol,
[class*="st-key-assistant-bubble-"] ul, [class*="st-key-assistant-bubble-"] ol {
    padding-left: 1.5rem;
    margin: 0.4rem 0;
}

[class*="st-key-user-bubble-"] table,
[class*="st-key-assistant-bubble-"] table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.5rem 0;
}

[class*="st-key-user-bubble-"] th, [class*="st-key-user-bubble-"] td,
[class*="st-key-assistant-bubble-"] th, [class*="st-key-assistant-bubble-"] td {
    border: 1px solid rgba(255,255,255,0.15);
    padding: 0.35rem 0.6rem;
    text-align: left;
}

[class*="st-key-user-bubble-"] th,
[class*="st-key-assistant-bubble-"] th {
    background-color: rgba(255,255,255,0.08);
    font-weight: 600;
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
    [class*="st-key-user-bubble-"] {
        background-color: #e3f2fd !important;
        border-color: #bbdefb !important;
        color: #1a1a1a !important;
    }
    [class*="st-key-assistant-bubble-"] {
        background-color: #f5f5f5 !important;
        border-color: #e0e0e0 !important;
        color: #1a1a1a !important;
    }
    [class*="st-key-user-bubble-"] strong,
    [class*="st-key-assistant-bubble-"] strong { color: inherit; }
    [class*="st-key-user-bubble-"] a,
    [class*="st-key-assistant-bubble-"] a { color: #1976d2; }
    [class*="st-key-user-bubble-"] code:not([data-testid="stCode"] code),
    [class*="st-key-assistant-bubble-"] code:not([data-testid="stCode"] code) { background-color: rgba(0,0,0,0.07); }
    [class*="st-key-user-bubble-"] th, [class*="st-key-user-bubble-"] td,
    [class*="st-key-assistant-bubble-"] th, [class*="st-key-assistant-bubble-"] td {
        border-color: rgba(0,0,0,0.12);
    }
    [class*="st-key-user-bubble-"] th,
    [class*="st-key-assistant-bubble-"] th { background-color: rgba(0,0,0,0.04); }
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


def get_connection_indicator_css(connection_type: str, use_kb: bool, outside: bool = None) -> str:
    """
    Ritorna il CSS appropriato per l'indicatore di connessione.
    
    Args:
        connection_type: Tipo di connessione
        use_kb: Se Knowledge Base è attiva
        
    Returns:
        Stringa CSS
    """
    # v1.16.0: la destinazione reale se nota, altrimenti l'etichetta
    if outside is None:
        outside = connection_type == "Cloud provider"
    if outside:
        return CLOUD_INDICATOR_CSS
    elif use_kb:
        return KB_INDICATOR_CSS
    return ""
