# ui/socratic/buttons.py
# DeepAiUG v1.8.0 - Bottoni Socratici
# ============================================================================
# UI per le funzionalità socratiche.
# I bottoni appaiono sotto le risposte AI per stimolare riflessione.
# ============================================================================

import streamlit as st
from typing import Optional, Callable

from .prompts import (
    get_alternatives_prompt,
    get_assumptions_prompt,
    get_limits_prompt,
    get_confute_prompt,   # v1.8.0
    get_reflect_prompt,   # v1.8.0
)


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


def generate_confute(
    response: str,
    llm_invoke_fn: Callable,
    msg_index: int
) -> Optional[str]:
    """
    Genera confutazione (avvocato del diavolo) per una risposta usando l'LLM. (v1.8.0)

    Args:
        response: La risposta originale dell'AI
        llm_invoke_fn: Funzione per invocare l'LLM (es. client.invoke)
        msg_index: Indice del messaggio per la cache

    Returns:
        La confutazione generata, o None se errore
    """
    cache_key = _get_socratic_cache_key(msg_index, "confute")

    # Controlla se già in cache
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    try:
        prompt = get_confute_prompt(response)
        result = llm_invoke_fn(prompt)

        # Estrai il testo dalla risposta
        if hasattr(result, 'text'):
            confute_text = result.text
        elif hasattr(result, 'content'):
            confute_text = result.content
        else:
            confute_text = str(result)

        # Salva in cache
        st.session_state[cache_key] = confute_text
        return confute_text

    except Exception as e:
        return f"❌ Errore nella generazione: {str(e)}"


def generate_reflect(
    response: str,
    user_question: str,
    llm_invoke_fn: Callable,
    msg_index: int
) -> Optional[str]:
    """
    Genera riflessione critica sulla DOMANDA dell'utente (non sulla risposta). (v1.8.0)

    Args:
        response: La risposta dell'AI
        user_question: La domanda originale dell'utente
        llm_invoke_fn: Funzione per invocare l'LLM (es. client.invoke)
        msg_index: Indice del messaggio per la cache

    Returns:
        La riflessione generata, o None se errore
    """
    cache_key = _get_socratic_cache_key(msg_index, "reflect")

    # Controlla se già in cache
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    try:
        prompt = get_reflect_prompt(response, user_question)
        result = llm_invoke_fn(prompt)

        # Estrai il testo dalla risposta
        if hasattr(result, 'text'):
            reflect_text = result.text
        elif hasattr(result, 'content'):
            reflect_text = result.content
        else:
            reflect_text = str(result)

        # Salva in cache
        st.session_state[cache_key] = reflect_text
        return reflect_text

    except Exception as e:
        return f"❌ Errore nella generazione: {str(e)}"


def render_socratic_buttons(
    message_content: str,
    msg_index: int,
    client: Optional[object] = None,
    user_question: Optional[str] = None,
    socratic_mode: str = "standard"
):
    """
    Renderizza i bottoni socratici sotto una risposta AI. (v1.8.0)

    Args:
        message_content: Il contenuto della risposta AI
        msg_index: Indice del messaggio nella conversazione
        client: Client LLM per generare le alternative (opzionale)
        user_question: La domanda utente precedente (per "Rifletti") - v1.8.0
        socratic_mode: Modalità socratica ("fast", "standard", "socratic") - v1.8.0
    """
    # v1.8.0 - Se modalità "fast", non mostrare bottoni
    if socratic_mode == "fast":
        return

    # Import config per accesso a SOCRATIC_MODES
    from config import SOCRATIC_MODES

    mode_config = SOCRATIC_MODES.get(socratic_mode, SOCRATIC_MODES["standard"])

    # Cache e loading keys per tutti i bottoni
    alt_cache_key = _get_socratic_cache_key(msg_index, "alternatives")
    alt_loading_key = _get_loading_key(msg_index, "alternatives")
    assum_cache_key = _get_socratic_cache_key(msg_index, "assumptions")
    assum_loading_key = _get_loading_key(msg_index, "assumptions")
    limits_cache_key = _get_socratic_cache_key(msg_index, "limits")
    limits_loading_key = _get_loading_key(msg_index, "limits")
    confute_cache_key = _get_socratic_cache_key(msg_index, "confute")      # v1.8.0
    confute_loading_key = _get_loading_key(msg_index, "confute")           # v1.8.0
    reflect_cache_key = _get_socratic_cache_key(msg_index, "reflect")      # v1.8.0
    reflect_loading_key = _get_loading_key(msg_index, "reflect")           # v1.8.0

    # Verifica stati cache e loading
    has_alt_cached = alt_cache_key in st.session_state
    is_alt_loading = st.session_state.get(alt_loading_key, False)
    has_assum_cached = assum_cache_key in st.session_state
    is_assum_loading = st.session_state.get(assum_loading_key, False)
    has_limits_cached = limits_cache_key in st.session_state
    is_limits_loading = st.session_state.get(limits_loading_key, False)
    has_confute_cached = confute_cache_key in st.session_state            # v1.8.0
    is_confute_loading = st.session_state.get(confute_loading_key, False)  # v1.8.0
    has_reflect_cached = reflect_cache_key in st.session_state            # v1.8.0
    is_reflect_loading = st.session_state.get(reflect_loading_key, False)  # v1.8.0

    # ========== SEZIONE 1: ANALIZZA LA RISPOSTA (4 bottoni) ==========
    st.caption("**Analizza la risposta:**")
    col1, col2, col3, col4 = st.columns(4)

    # Bottone 1: Alternative
    with col1:
        button_label = "✅ Alternative" if has_alt_cached else "🔄 Alternative"
        button_disabled = is_alt_loading or client is None

        if st.button(
            button_label,
            key=f"btn_alternatives_{msg_index}",
            disabled=button_disabled,
            help="Genera 3 interpretazioni alternative"
        ):
            if not has_alt_cached:
                st.session_state[alt_loading_key] = True
                st.rerun()

    # Bottone 2: Assunzioni
    with col2:
        button_label = "✅ Assunzioni" if has_assum_cached else "🤔 Assunzioni"
        button_disabled = is_assum_loading or client is None

        if st.button(
            button_label,
            key=f"btn_assumptions_{msg_index}",
            disabled=button_disabled,
            help="Mostra le assunzioni implicite"
        ):
            if not has_assum_cached:
                st.session_state[assum_loading_key] = True
                st.rerun()

    # Bottone 3: Limiti
    with col3:
        button_label = "✅ Limiti" if has_limits_cached else "⚠️ Limiti"
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

    # Bottone 4: Confuta (v1.8.0)
    with col4:
        button_label = "✅ Confutato" if has_confute_cached else "🎭 Confuta"
        button_disabled = is_confute_loading or client is None

        if st.button(
            button_label,
            key=f"btn_confute_{msg_index}",
            disabled=button_disabled,
            help="Avvocato del diavolo: punti deboli e falle logiche"
        ):
            if not has_confute_cached:
                st.session_state[confute_loading_key] = True
                st.rerun()

    # ========== SEZIONE 2: SFIDA LA DOMANDA (1 bottone) - v1.8.0 ==========
    if user_question:  # Solo se abbiamo la domanda utente
        st.caption("**Sfida la domanda:**")
        col_reflect, _, _, _ = st.columns(4)

        with col_reflect:
            button_label = "✅ Riflettuto" if has_reflect_cached else "🪞 Rifletti"
            button_disabled = is_reflect_loading or client is None

            if st.button(
                button_label,
                key=f"btn_reflect_{msg_index}",
                disabled=button_disabled,
                help="Sfida il perimetro della TUA domanda"
            ):
                if not has_reflect_cached:
                    st.session_state[reflect_loading_key] = True
                    st.rerun()

    # ========== GENERAZIONE (loading states) ==========

    # Generazione alternative se in loading
    if is_alt_loading and client is not None:
        with st.spinner("🧠 Generando alternative..."):
            try:
                generate_alternatives(
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
                generate_assumptions(
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
                generate_limits(
                    response=message_content,
                    llm_invoke_fn=client.invoke,
                    msg_index=msg_index
                )
                st.session_state[limits_loading_key] = False
                st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")
                st.session_state[limits_loading_key] = False

    # Generazione confutazione se in loading (v1.8.0)
    if is_confute_loading and client is not None:
        with st.spinner("🎭 Confutando..."):
            try:
                generate_confute(
                    response=message_content,
                    llm_invoke_fn=client.invoke,
                    msg_index=msg_index
                )
                st.session_state[confute_loading_key] = False
                st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")
                st.session_state[confute_loading_key] = False

    # Generazione riflessione se in loading (v1.8.0)
    if is_reflect_loading and client is not None and user_question:
        with st.spinner("🪞 Riflettendo sulla domanda..."):
            try:
                generate_reflect(
                    response=message_content,
                    user_question=user_question,
                    llm_invoke_fn=client.invoke,
                    msg_index=msg_index
                )
                st.session_state[reflect_loading_key] = False
                st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")
                st.session_state[reflect_loading_key] = False

    # ========== EXPANDER CON RISULTATI ==========

    # Mostra le alternative se presenti
    if has_alt_cached:
        with st.expander("🔄 **Alternative generate** - Esplora prospettive diverse", expanded=False):
            st.markdown(st.session_state[alt_cache_key])
            st.caption("💡 *Quale prospettiva ti sembra più utile?*")

    # Mostra le assunzioni se presenti
    if has_assum_cached:
        with st.expander("🤔 **Assunzioni implicite** - Cosa si dà per scontato?", expanded=False):
            st.markdown(st.session_state[assum_cache_key])
            st.caption("💭 *Quali si applicano davvero alla tua situazione?*")

    # Mostra i limiti se presenti
    if has_limits_cached:
        with st.expander("⚠️ **Limiti di validità** - Quando NON funziona", expanded=False):
            st.markdown(st.session_state[limits_cache_key])
            st.caption("🔍 *La tua situazione rientra in questi casi limite?*")

    # Mostra la confutazione se presente (v1.8.0)
    if has_confute_cached:
        with st.expander("🎭 **Confutazione** - Avvocato del diavolo", expanded=False):
            st.markdown(st.session_state[confute_cache_key])
            st.caption("⚔️ *Usa questa critica per rafforzare il tuo ragionamento.*")

    # Mostra la riflessione se presente (v1.8.0)
    if has_reflect_cached:
        with st.expander("🪞 **Riflessione sulla domanda** - Sfida il tuo perimetro", expanded=False):
            st.markdown(st.session_state[reflect_cache_key])
            st.caption("🎯 *Stai facendo la domanda giusta?*")

    # ========== INVITO RIFLESSIONE (solo in modalità socratica) - v1.8.0 ==========
    if mode_config.get("show_reflection_invite", False):
        st.info(
            "🧠 **Modalità Socratica attiva** - "
            "Prima di accettare questa risposta, chiediti: "
            "*Quali alternative non ho considerato? Cosa sto dando per scontato?*"
        )


def clear_socratic_cache():
    """Pulisce la cache delle risposte socratiche."""
    keys_to_remove = [
        key for key in st.session_state.keys() 
        if key.startswith("socratic_")
    ]
    for key in keys_to_remove:
        del st.session_state[key]