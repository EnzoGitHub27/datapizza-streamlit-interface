# ui/socratic/buttons.py
# Datapizza v1.7.0 - Bottoni Socratici
# ============================================================================
# UI per le funzionalità socratiche.
# I bottoni appaiono sotto le risposte AI per stimolare riflessione.
# ============================================================================

import streamlit as st
from typing import Optional, Callable

from .prompts import get_alternatives_prompt, get_assumptions_prompt, get_limits_prompt


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


def generate_assumptions(
    response: str,
    llm_invoke_fn: Callable,
    msg_index: int
) -> Optional[str]:
    """
    Genera analisi delle assunzioni implicite per una risposta usando l'LLM.

    Args:
        response: La risposta originale dell'AI
        llm_invoke_fn: Funzione per invocare l'LLM (es. client.invoke)
        msg_index: Indice del messaggio per la cache

    Returns:
        L'analisi delle assunzioni generata, o None se errore
    """
    cache_key = _get_socratic_cache_key(msg_index, "assumptions")

    # Controlla se già in cache
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    try:
        prompt = get_assumptions_prompt(response)
        result = llm_invoke_fn(prompt)

        # Estrai il testo dalla risposta
        if hasattr(result, 'text'):
            assumptions_text = result.text
        elif hasattr(result, 'content'):
            assumptions_text = result.content
        else:
            assumptions_text = str(result)

        # Salva in cache
        st.session_state[cache_key] = assumptions_text
        return assumptions_text

    except Exception as e:
        return f"❌ Errore nella generazione: {str(e)}"


def generate_limits(
    response: str,
    llm_invoke_fn: Callable,
    msg_index: int
) -> Optional[str]:
    """
    Genera analisi dei limiti di validità per una risposta usando l'LLM.

    Args:
        response: La risposta originale dell'AI
        llm_invoke_fn: Funzione per invocare l'LLM (es. client.invoke)
        msg_index: Indice del messaggio per la cache

    Returns:
        L'analisi dei limiti generata, o None se errore
    """
    cache_key = _get_socratic_cache_key(msg_index, "limits")

    # Controlla se già in cache
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    try:
        prompt = get_limits_prompt(response)
        result = llm_invoke_fn(prompt)

        # Estrai il testo dalla risposta
        if hasattr(result, 'text'):
            limits_text = result.text
        elif hasattr(result, 'content'):
            limits_text = result.content
        else:
            limits_text = str(result)

        # Salva in cache
        st.session_state[cache_key] = limits_text
        return limits_text

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
    # Cache e loading keys per tutti i bottoni
    alt_cache_key = _get_socratic_cache_key(msg_index, "alternatives")
    alt_loading_key = _get_loading_key(msg_index, "alternatives")
    assum_cache_key = _get_socratic_cache_key(msg_index, "assumptions")
    assum_loading_key = _get_loading_key(msg_index, "assumptions")
    limits_cache_key = _get_socratic_cache_key(msg_index, "limits")
    limits_loading_key = _get_loading_key(msg_index, "limits")

    # Verifica stati cache e loading
    has_alt_cached = alt_cache_key in st.session_state
    is_alt_loading = st.session_state.get(alt_loading_key, False)
    has_assum_cached = assum_cache_key in st.session_state
    is_assum_loading = st.session_state.get(assum_loading_key, False)
    has_limits_cached = limits_cache_key in st.session_state
    is_limits_loading = st.session_state.get(limits_loading_key, False)

    # Layout per 3 bottoni
    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
    
    # Bottone 1: Alternative
    with col1:
        button_label = "✅ Alternative generate" if has_alt_cached else "🔄 Genera alternative"
        button_disabled = is_alt_loading or client is None

        if st.button(
            button_label,
            key=f"btn_alternatives_{msg_index}",
            disabled=button_disabled,
            help="Genera 3 interpretazioni alternative di questa risposta"
        ):
            if not has_alt_cached:
                st.session_state[alt_loading_key] = True
                st.rerun()

    # Bottone 2: Assunzioni
    with col2:
        button_label = "✅ Assunzioni trovate" if has_assum_cached else "🤔 Assunzioni"
        button_disabled = is_assum_loading or client is None

        if st.button(
            button_label,
            key=f"btn_assumptions_{msg_index}",
            disabled=button_disabled,
            help="Mostra le assunzioni implicite di questa risposta"
        ):
            if not has_assum_cached:
                st.session_state[assum_loading_key] = True
                st.rerun()

    # Bottone 3: Limiti
    with col3:
        button_label = "✅ Limiti trovati" if has_limits_cached else "⚠️ Limiti"
        button_disabled = is_limits_loading or client is None

        if st.button(
            button_label,
            key=f"btn_limits_{msg_index}",
            disabled=button_disabled,
            help="Mostra quando questa risposta non funziona"
        ):
            if not has_limits_cached:
                st.session_state[limits_loading_key] = True
                st.rerun()
    
    # Generazione alternative se in loading
    if is_alt_loading and client is not None:
        with st.spinner("🧠 Generando alternative..."):
            try:
                alternatives = generate_alternatives(
                    response=message_content,
                    llm_invoke_fn=client.invoke,
                    msg_index=msg_index
                )
                st.session_state[alt_loading_key] = False
                st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")
                st.session_state[alt_loading_key] = False

    # Generazione assunzioni se in loading
    if is_assum_loading and client is not None:
        with st.spinner("🤔 Analizzando assunzioni..."):
            try:
                assumptions = generate_assumptions(
                    response=message_content,
                    llm_invoke_fn=client.invoke,
                    msg_index=msg_index
                )
                st.session_state[assum_loading_key] = False
                st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")
                st.session_state[assum_loading_key] = False

    # Generazione limiti se in loading
    if is_limits_loading and client is not None:
        with st.spinner("⚠️ Identificando limiti..."):
            try:
                limits = generate_limits(
                    response=message_content,
                    llm_invoke_fn=client.invoke,
                    msg_index=msg_index
                )
                st.session_state[limits_loading_key] = False
                st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")
                st.session_state[limits_loading_key] = False
    
    # Mostra le alternative se presenti
    if has_alt_cached:
        with st.expander("🔄 **Alternative generate** - Esplora prospettive diverse", expanded=False):
            st.markdown(st.session_state[alt_cache_key])
            st.caption("💡 *Queste alternative ti aiutano a vedere il problema da angolazioni diverse. Quale prospettiva ti sembra più utile?*")

    # Mostra le assunzioni se presenti
    if has_assum_cached:
        with st.expander("🤔 **Assunzioni implicite** - Cosa si dà per scontato?", expanded=False):
            st.markdown(st.session_state[assum_cache_key])
            st.caption("💭 *Queste assunzioni potrebbero non essere valide nel tuo contesto specifico. Quali si applicano davvero alla tua situazione?*")

    # Mostra i limiti se presenti
    if has_limits_cached:
        with st.expander("⚠️ **Limiti di validità** - Quando NON funziona", expanded=False):
            st.markdown(st.session_state[limits_cache_key])
            st.caption("🔍 *Conoscere i limiti è importante quanto conoscere le soluzioni. La tua situazione rientra in questi casi limite?*")


def clear_socratic_cache():
    """Pulisce la cache delle risposte socratiche."""
    keys_to_remove = [
        key for key in st.session_state.keys() 
        if key.startswith("socratic_")
    ]
    for key in keys_to_remove:
        del st.session_state[key]