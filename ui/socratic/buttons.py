# ui/socratic/buttons.py
# Datapizza v1.6.1 - Bottoni Socratici
# ============================================================================
# UI per le funzionalità socratiche.
# I bottoni appaiono sotto le risposte AI per stimolare riflessione.
# ============================================================================

import streamlit as st
from typing import Optional, Callable

from .prompts import get_alternatives_prompt


def _get_socratic_cache_key(msg_index: int, action: str) -> str:
    """Genera la chiave per la cache delle risposte socratiche."""
    return f"socratic_{action}_{msg_index}"


def _get_loading_key(msg_index: int, action: str) -> str:
    """Genera la chiave per lo stato di loading."""
    return f"socratic_loading_{action}_{msg_index}"


def generate_alternatives(
    response: str,
    llm_invoke_fn: Callable,
    msg_index: int
) -> Optional[str]:
    """
    Genera alternative per una risposta usando l'LLM.
    
    Args:
        response: La risposta originale dell'AI
        llm_invoke_fn: Funzione per invocare l'LLM (es. client.invoke)
        msg_index: Indice del messaggio per la cache
        
    Returns:
        Le alternative generate, o None se errore
    """
    cache_key = _get_socratic_cache_key(msg_index, "alternatives")
    
    # Controlla se già in cache
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    try:
        prompt = get_alternatives_prompt(response)
        result = llm_invoke_fn(prompt)
        
        # Estrai il testo dalla risposta
        if hasattr(result, 'text'):
            alternatives_text = result.text
        elif hasattr(result, 'content'):
            alternatives_text = result.content
        else:
            alternatives_text = str(result)
        
        # Salva in cache
        st.session_state[cache_key] = alternatives_text
        return alternatives_text
        
    except Exception as e:
        return f"❌ Errore nella generazione: {str(e)}"


def render_socratic_buttons(
    message_content: str,
    msg_index: int,
    client: Optional[object] = None
):
    """
    Renderizza i bottoni socratici sotto una risposta AI.
    
    Args:
        message_content: Il contenuto della risposta AI
        msg_index: Indice del messaggio nella conversazione
        client: Client LLM per generare le alternative (opzionale)
    """
    cache_key = _get_socratic_cache_key(msg_index, "alternatives")
    loading_key = _get_loading_key(msg_index, "alternatives")
    
    # Verifica se abbiamo già le alternative in cache
    has_cached = cache_key in st.session_state
    is_loading = st.session_state.get(loading_key, False)
    
    # Bottone per generare alternative
    col1, col2, col3 = st.columns([2, 2, 6])
    
    with col1:
        button_label = "✅ Alternative generate" if has_cached else "🔄 Genera alternative"
        button_disabled = is_loading or client is None
        
        if st.button(
            button_label,
            key=f"btn_alternatives_{msg_index}",
            disabled=button_disabled,
            help="Genera 3 interpretazioni alternative di questa risposta"
        ):
            if not has_cached:
                st.session_state[loading_key] = True
                st.rerun()
    
    # Se in loading, genera le alternative
    if is_loading and client is not None:
        with st.spinner("🧠 Generando alternative..."):
            try:
                alternatives = generate_alternatives(
                    response=message_content,
                    llm_invoke_fn=client.invoke,
                    msg_index=msg_index
                )
                st.session_state[loading_key] = False
                st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")
                st.session_state[loading_key] = False
    
    # Mostra le alternative se presenti
    if has_cached:
        with st.expander("🔄 **Alternative generate** - Esplora prospettive diverse", expanded=False):
            st.markdown(st.session_state[cache_key])
            st.caption("💡 *Queste alternative ti aiutano a vedere il problema da angolazioni diverse. Quale prospettiva ti sembra più utile?*")


def clear_socratic_cache():
    """Pulisce la cache delle risposte socratiche."""
    keys_to_remove = [
        key for key in st.session_state.keys() 
        if key.startswith("socratic_")
    ]
    for key in keys_to_remove:
        del st.session_state[key]