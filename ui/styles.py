# ui/styles.py
# DeepAiUG v1.4.0 - Stili CSS
# ============================================================================

# CSS principale dell'applicazione
MAIN_CSS = """
<style>
.user-bubble {
    background-color: #E3F2FD !important;
    padding: 0.75rem 1rem !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    margin-bottom: 0.5rem !important;
    color: #1a1a1a !important;
}

.assistant-bubble {
    background-color: #F5F5F5 !important;
    padding: 0.75rem 1rem !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    margin-bottom: 0.5rem !important;
    color: #1a1a1a !important;
}

.kb-enabled {
    border-left: 4px solid #4CAF50 !important;
    padding-left: 10px !important;
}

@media (prefers-color-scheme: dark) {
    .user-bubble { 
        background-color: #1E3A5F !important; 
        color: #E8E8E8 !important; 
    }
    .assistant-bubble { 
        background-color: #2D2D2D !important; 
        color: #E8E8E8 !important; 
    }
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
