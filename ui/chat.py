# ui/chat.py
# DeepAiUG v1.14.3 - Rendering Chat + Socratic Buttons
# ============================================================================
# 🆕 v1.5.0: Aggiunto supporto per visualizzazione allegati nei messaggi
# 🆕 v1.6.1: Aggiunto bottone "Genera alternative" (approccio socratico)
# 🆕 v1.8.0: Passaggio user_question e socratic_mode ai bottoni socratici
# 🆕 v1.9.1: Fix bubble rendering - singola st.markdown() per wrappare contenuto
# 🆕 v1.14.3: Typing indicator animato + scroll automatico durante streaming
# 🆕 v1.15.4: Bolla = contenitore Streamlit con key + st.markdown nativo.
#   Prima il Markdown diventava HTML (markdown_it) e st.markdown lo rileggeva
#   come Markdown: alla prima riga vuota di un blocco di codice il blocco HTML
#   si chiudeva, il resto diventava un blocco annidato e il frontend scriveva
#   "[object Object]" (anche negli appunti). Vedi docs/AUDIT_pre_v1.16.0.md §3.
# ============================================================================

from datetime import datetime
from typing import Dict, Any, List, Optional

import streamlit as st

import streamlit.components.v1 as components

from ui.socratic import render_socratic_buttons


def bubble_key(role: str, index: int) -> str:
    """Key del contenitore della bolla: Streamlit la espone come classe CSS
    `st-key-<key>`, che ui/styles.py usa per lo stile (user-bubble-N /
    assistant-bubble-N)."""
    kind = "user" if role == "user" else "assistant"
    return f"{kind}-bubble-{index}"


def _escape_md(text: str) -> str:
    """Neutralizza i caratteri Markdown in un testo da mostrare così com'è
    (i nomi dei file allegati)."""
    out = []
    for ch in text:
        if ch in "\\`*_{}[]()<>#+-.!|~":
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


def render_chat_message(
    message: Dict[str, Any],
    index: int,
    llm_client: Optional[object] = None,
    messages_list: Optional[List[Dict[str, Any]]] = None,
    socratic_mode: str = "standard"
):
    """
    Renderizza un singolo messaggio della chat con stile bubble.

    Args:
        message: Dizionario con role, content, timestamp, model, sources, attachments
        index: Indice del messaggio nella conversazione
        llm_client: Client LLM per le funzionalità socratiche (opzionale)
        messages_list: Lista completa messaggi per estrarre user_question (v1.8.0)
        socratic_mode: Modalità socratica per controllare i bottoni (v1.8.0)
    """
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    model_used = message.get("model", "")
    sources = message.get("sources", [])
    attachments = message.get("attachments", [])  # v1.5.0

    # Format timestamp
    time_str = ""
    if timestamp:
        try:
            time_str = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
        except:
            pass

    # Configure styling based on role
    if role == "user":
        avatar, label = "👤", "Tu"
        col_config = [3, 7, 0.5]
    else:
        avatar = "🤖"
        label = f"AI{f' ({model_used})' if model_used else ''}"
        col_config = [0.5, 7, 3]

    # Render message
    cols = st.columns(col_config)
    with cols[1]:
        st.caption(f"{avatar} **{label}** • {time_str}")

        # v1.15.4 — Bolla: contenitore con key (stile in ui/styles.py) e
        # Markdown nativo di Streamlit, lo stesso usato durante lo streaming.
        # Niente HTML grezzo: i blocchi di codice si vedono e si copiano interi.
        with st.container(key=bubble_key(role, index)):
            # v1.5.0 - Attachments line (user messages only)
            if attachments and role == "user":
                st.caption("📎 **Allegati:** " + _escape_md(", ".join(attachments)))

            st.markdown(content)

        # v1.16.0 P9 (decisione 9) — badge e «cosa ha visto il modello»
        if role == "assistant" and message.get("pii_removed") is not None:
            n = int(message.get("pii_removed") or 0)
            st.caption(f"🛡️ {n} {'dato tolto' if n == 1 else 'dati tolti'} prima dell'invio")
        if role == "assistant":
            egress = (st.session_state.get("egress_views") or {}).get(index)
            if egress:
                with st.expander("👁️ Cosa ha visto il modello", expanded=False):
                    st.text(egress)
                    st.caption("Solo in questa sessione: non si salva nella conversazione.")

        # v1.16.0 P7 (decisione 6) — invio fuori casa non registrato in Annona
        if role == "assistant" and message.get("annona_recorded") is False:
            st.caption("📒 non registrato in Annona")
        # v1.16.0 P8 — risposta arrivata dal gateway sperimentale di Annona
        if role == "assistant" and message.get("annona_gateway"):
            p = message.get("annona_placement") or {}
            bits = " · ".join(v for v in (p.get("class"), p.get("outcome"), p.get("substrate")) if v)
            st.caption(f"🧭 via Annona (sperimentale){' · ' + bits if bits else ''} · registrato in Annona")

        # v1.16.0 (decisione 11) — la domanda senza risposta porta il suo errore
        send_status = message.get("send_status") if role == "user" else None
        if send_status:
            detail = message.get("send_error", "")
            if send_status == "rifiutata":
                st.error(f"⛔ **Rifiutata** dal fornitore — {detail}")
            elif send_status == "senza_risposta":  # giro 7b: gateway di Annona senza testo
                if detail.startswith("EmptyModelAnswer"):  # v1.16.2: il modello, senza testo
                    st.warning(f"🧠 **Senza risposta** — {detail.split(': ', 1)[-1]}")
                else:
                    st.warning(f"🧭 **Senza risposta** — {detail}")
            else:
                st.warning(f"⚠️ **Non inviata** — {detail}")

        # Show sources if present (RAG) — kept outside bubble as native expander
        if sources:
            with st.expander(f"📎 Fonti ({len(sources)})"):
                for src in sources:
                    st.caption(f"• {src}")

        # v1.8.0 - Bottoni socratici (solo per risposte AI)
        if role == "assistant" and content:
            # v1.8.0 - Estrai user_question dal messaggio precedente
            user_question = None
            if messages_list and index > 0:
                prev_msg = messages_list[index - 1]
                if prev_msg.get("role") == "user":
                    user_question = prev_msg.get("content")

            render_socratic_buttons(
                message_content=content,
                msg_index=index,
                client=llm_client,
                user_question=user_question,
                socratic_mode=socratic_mode,
                model_used=model_used
            )

        st.write("")


def render_chat_area(
    messages: List[Dict[str, Any]],
    llm_client: Optional[object] = None,
    socratic_mode: str = "standard"
):
    """
    Renderizza l'intera area chat con tutti i messaggi.

    Args:
        messages: Lista di messaggi della conversazione
        llm_client: Client LLM per le funzionalità socratiche (opzionale)
        socratic_mode: Modalità socratica (v1.8.0)
    """
    st.subheader("💬 Conversazione")

    if not messages:
        if st.session_state.get("use_knowledge_base"):
            st.info("👋 Knowledge Base attiva! Fai una domanda sui tuoi documenti.")
        else:
            st.info("👋 Inizia una conversazione!")
    else:
        for idx, msg in enumerate(messages):
            render_chat_message(
                msg,
                idx,
                llm_client,
                messages_list=messages,
                socratic_mode=socratic_mode
            )


def render_empty_state():
    """Renderizza stato vuoto della chat."""
    if st.session_state.get("use_knowledge_base"):
        st.info("👋 Knowledge Base attiva! Fai una domanda sui tuoi documenti.")
    else:
        st.info("👋 Inizia una conversazione!")


# ── v1.14.3 — Typing indicator + Auto-scroll ────────────────────────────────

def show_typing_indicator():
    """
    Mostra tre pallini animati (typing indicator) nell'area chat.
    Usa il colore teal del tema Matrix DeepAiUG.
    """
    st.markdown("""
    <div class="typing-indicator">
        <span></span><span></span><span></span>
    </div>
    """, unsafe_allow_html=True)


def inject_scroll_to_bottom():
    """
    Inietta JS che scrolla la finestra verso il basso.
    Da chiamare durante lo streaming per seguire il testo in arrivo.
    """
    components.html(
        """
        <script>
            const chatContainer = window.parent.document.querySelector(
                'section.main [data-testid="stVerticalBlock"]'
            );
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            window.parent.scrollTo(0, window.parent.document.body.scrollHeight);
        </script>
        """,
        height=0,
    )
