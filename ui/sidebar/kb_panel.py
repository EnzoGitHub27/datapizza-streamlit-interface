# ui/sidebar/kb_panel.py
# DeepAiUG v1.14.0 - Pannello gestione Knowledge Base epistemica
# ============================================================================
# Vista tabellare delle chat incluse nella KB, con modifica metadati inline
# e rimozione dalla KB. Posizionato nella sidebar dopo la sezione conversazioni.
# ============================================================================

from datetime import datetime

import streamlit as st

from core import (
    list_saved_conversations,
    load_conversation,
    get_kb_metadata,
    get_kb_chat_stats,
    get_chunks_per_chat,
    load_chat_kb_meta,
    remove_chat_from_kb,
    index_chat_to_kb,
    update_conversation_kb_metadata,
    KB_METADATA_DEFAULT,
)

_TIPO_OPZIONI = ["decisione", "insight", "memoria_aziendale", "riferimento", "sperimentale"]
_RILEVANZA_MAP = {"Bassa": 1, "Media": 2, "Alta": 3}
_RILEVANZA_REV = {1: "Bassa", 2: "Media", 3: "Alta"}
_RILEVANZA_STARS = {1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐"}


def render_kb_panel():
    """Renderizza il pannello gestione KB nella sidebar."""
    with st.sidebar.expander("📚 Gestione Knowledge Base", expanded=False):
        _render_stats_header()
        _render_kb_chat_list()
        _render_bulk_flag_section()


def _render_stats_header():
    """Riga statistiche in cima al pannello."""
    stats = get_kb_chat_stats()
    meta = load_chat_kb_meta()

    n_chats = stats.get("total_chats", 0)
    n_chunks = stats.get("total_chunks", 0)

    last_iso = meta.get("last_indexed", "")
    if last_iso:
        try:
            dt = datetime.fromisoformat(last_iso)
            last_str = dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            last_str = last_iso[:16]
    else:
        last_str = "mai"

    st.caption(
        f"📚 {n_chats} chat indicizzate · {n_chunks} chunk totali · "
        f"Ultima indicizzazione: {last_str}"
    )


def _render_kb_chat_list():
    """Lista delle chat incluse nella KB con azioni inline."""
    conversations = list_saved_conversations()
    kb_convs = [
        c for c in conversations
        if c.get("kb_metadata", {}).get("includi_in_kb")
    ]

    if not kb_convs:
        st.info("Nessuna chat inclusa nella KB.")
        return

    # Chunk counts per chat (single query to ChromaDB)
    chunks_map = get_chunks_per_chat()

    for conv in kb_convs:
        chat_id = conv["id"]
        kb_meta = conv.get("kb_metadata", {})
        rilevanza = kb_meta.get("rilevanza", 1)
        tipo_list = kb_meta.get("tipo", [])
        note = kb_meta.get("note", "")
        n_chunks = chunks_map.get(chat_id, 0)

        # Titolo: data + modello (compatto)
        title = f"{conv.get('last_updated', '')[:10]} · {conv.get('model', '?')[:12]}"
        stars = _RILEVANZA_STARS.get(rilevanza, "⭐")
        tipo_tags = " ".join(f"`{t}`" for t in tipo_list) if tipo_list else "—"
        note_trunc = (note[:40] + "...") if len(note) > 40 else (note or "—")

        st.markdown(
            f"**{title}**  \n"
            f"{stars} · {tipo_tags} · {n_chunks} chunk  \n"
            f"_{note_trunc}_"
        )

        # Azioni: Modifica / Rimuovi
        col_edit, col_del = st.columns(2)

        # Key unici per evitare conflitti Streamlit
        edit_key = f"kb_edit_{chat_id}"
        del_key = f"kb_del_{chat_id}"

        with col_edit:
            if st.button("✏️ Modifica", key=edit_key):
                st.session_state[f"_kb_editing_{chat_id}"] = True

        with col_del:
            if st.button("🗑️ Rimuovi", key=del_key):
                st.session_state[f"_kb_confirm_del_{chat_id}"] = True

        # --- Form modifica inline ---
        if st.session_state.get(f"_kb_editing_{chat_id}"):
            _render_edit_form(chat_id, kb_meta)

        # --- Confirm dialog rimozione ---
        if st.session_state.get(f"_kb_confirm_del_{chat_id}"):
            _render_remove_confirm(chat_id)

        st.markdown("---")


def _render_edit_form(chat_id: str, kb_meta: dict):
    """Form inline per modifica metadati KB di una chat."""
    rilevanza = kb_meta.get("rilevanza", 1)
    tipo_list = kb_meta.get("tipo", [])
    note = kb_meta.get("note", "")

    new_ril_label = st.radio(
        "Rilevanza",
        list(_RILEVANZA_MAP.keys()),
        index=max(0, rilevanza - 1),
        horizontal=True,
        key=f"kb_ril_{chat_id}",
    )

    new_tipo = st.multiselect(
        "Tipo",
        _TIPO_OPZIONI,
        default=[t for t in tipo_list if t in _TIPO_OPZIONI],
        key=f"kb_tipo_{chat_id}",
    )

    new_note = st.text_input(
        "Note",
        value=note,
        key=f"kb_note_{chat_id}",
    )

    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("💾 Salva", key=f"kb_save_{chat_id}"):
            new_meta = {
                "includi_in_kb": True,
                "rilevanza": _RILEVANZA_MAP.get(new_ril_label, 1),
                "tipo": new_tipo,
                "note": new_note,
            }
            # Aggiorna JSON su disco
            update_conversation_kb_metadata(chat_id, new_meta)
            # Re-indicizza (remove + re-index)
            chat_data = load_conversation(chat_id)
            if chat_data:
                # Patch kb_metadata nel dict in-memory prima di indicizzare
                chat_data["kb_metadata"] = new_meta
                index_chat_to_kb(chat_data)
            # Cleanup state
            st.session_state.pop(f"_kb_editing_{chat_id}", None)
            st.rerun()

    with col_cancel:
        if st.button("❌ Annulla", key=f"kb_cancel_{chat_id}"):
            st.session_state.pop(f"_kb_editing_{chat_id}", None)
            st.rerun()


def _render_remove_confirm(chat_id: str):
    """Dialog conferma rimozione dalla KB."""
    st.warning("Rimuovere questa chat dalla KB? La chat non verrà eliminata.")
    col_ok, col_no = st.columns(2)
    with col_ok:
        if st.button("✅ Conferma", key=f"kb_confirm_yes_{chat_id}"):
            # Rimuovi da ChromaDB
            remove_chat_from_kb(chat_id)
            # Aggiorna metadati: includi_in_kb = false
            update_conversation_kb_metadata(chat_id, dict(KB_METADATA_DEFAULT))
            # Cleanup
            st.session_state.pop(f"_kb_confirm_del_{chat_id}", None)
            st.rerun()
    with col_no:
        if st.button("❌ No", key=f"kb_confirm_no_{chat_id}"):
            st.session_state.pop(f"_kb_confirm_del_{chat_id}", None)
            st.rerun()


def _render_bulk_flag_section():
    """Sezione per flaggare chat esistenti non ancora nella KB."""
    conversations = list_saved_conversations()
    non_kb_convs = [
        c for c in conversations
        if not c.get("kb_metadata", {}).get("includi_in_kb")
    ]

    if not non_kb_convs:
        return

    st.markdown("---")
    st.markdown("**Flagga chat esistenti**")
    st.info(
        "Le chat salvate prima di v1.14.0 non sono nella KB. "
        "Selezionale qui per includerle."
    )

    # Checkbox per ogni chat non flaggata
    selected_ids = []
    for conv in non_kb_convs:
        chat_id = conv["id"]
        label = f"{conv.get('last_updated', '')[:10]} · {conv.get('model', '?')[:12]} ({conv.get('message_count', 0)} msg)"
        if st.checkbox(label, key=f"bulk_flag_{chat_id}", value=False):
            selected_ids.append(chat_id)

    # Rilevanza di default per le selezionate
    bulk_ril_label = st.radio(
        "Rilevanza per le selezionate",
        list(_RILEVANZA_MAP.keys()),
        index=0,
        horizontal=True,
        key="bulk_flag_rilevanza",
    )

    if st.button(
        f"➕ Aggiungi alla KB ({len(selected_ids)})",
        key="bulk_flag_submit",
        disabled=len(selected_ids) == 0,
    ):
        bulk_meta = {
            "includi_in_kb": True,
            "rilevanza": _RILEVANZA_MAP.get(bulk_ril_label, 1),
            "tipo": [],
            "note": "",
        }
        count = 0
        for cid in selected_ids:
            if update_conversation_kb_metadata(cid, bulk_meta):
                count += 1
        st.success(
            f"{count} chat aggiunte alla KB — clicca **Aggiorna KB Chat** per indicizzarle"
        )
        st.rerun()
