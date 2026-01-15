# ui/sidebar/export_ui.py
# Datapizza v1.4.0 - Sidebar: Export conversazioni (Refactored for Layout Agnosticism)
# ============================================================================

from datetime import datetime
import streamlit as st

from config import EXPORT_FORMATS, CONTENT_OPTIONS
from core import list_saved_conversations, estimate_conversation_tokens
from export import (
    get_messages_for_export,
    export_to_markdown,
    export_to_json,
    export_to_txt,
    export_to_pdf,
    create_batch_export_zip,
)


def render_export_section():
    """Renderizza la sezione export."""
    st.markdown("---")
    st.markdown("### 📤 Export Conversazione")
    
    messages = st.session_state.get("messages", [])
    
    if not messages:
        st.info("💡 Inizia una conversazione per abilitare l'export")
        return
    
    # Selezione formato
    export_format = st.selectbox(
        "Formato Export",
        options=list(EXPORT_FORMATS.keys()),
        format_func=lambda x: f"{EXPORT_FORMATS[x]['icon']} {x} ({EXPORT_FORMATS[x]['ext']})"
    )
    
    # Selezione contenuto
    content_option = st.selectbox(
        "Contenuto", 
        options=list(CONTENT_OPTIONS.keys())
    )
    
    # Nome file
    conv_id = st.session_state.get("conversation_id", "unknown")
    default_filename = f"conversation_{conv_id}"
    export_filename = st.text_input(
        "Nome file (senza estensione)", 
        value=default_filename
    )
    
    # Preview button
    def preview_callback():
        st.session_state["show_export_preview"] = True
        st.session_state["preview_content_option"] = content_option
        st.session_state["preview_format"] = export_format

    st.button("👁️ Anteprima Export", use_container_width=True, key="export_preview_btn", on_click=preview_callback)
    
    # Export button
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        if st.button("📥 Download", use_container_width=True, type="primary", key="export_download_btn"):
            _generate_and_download(
                messages, 
                export_format, 
                content_option, 
                export_filename,
                conv_id,
                container=col_exp2 # Pass container for download button
            )
    
    # Batch export
    _render_batch_export()


def _generate_and_download(
    messages, 
    export_format, 
    content_option, 
    export_filename,
    conv_id,
    container=None
):
    """Genera e offre download."""
    # Use provided container or fallback to st (current context)
    target = container if container else st
    
    messages_to_export = get_messages_for_export(messages, content_option)
    
    metadata = {
        "conversation_id": conv_id,
        "created_at": st.session_state.get("conversation_created_at", ""),
        "last_updated": datetime.now().isoformat(),
        "model": st.session_state.get("current_model", ""),
        "provider": st.session_state.get("connection_type", ""),
        "tokens": estimate_conversation_tokens(messages)
    }
    
    # Genera export
    content = None
    if export_format == "Markdown":
        content = export_to_markdown(messages_to_export, metadata)
    elif export_format == "JSON":
        content = export_to_json(messages_to_export, metadata)
    elif export_format == "TXT":
        content = export_to_txt(messages_to_export, metadata)
    elif export_format == "PDF":
        content = export_to_pdf(messages_to_export, metadata)
    
    if content:
        ext = EXPORT_FORMATS[export_format]["ext"]
        mime = EXPORT_FORMATS[export_format]["mime"]
        filename = f"{export_filename}{ext}"
        
        target.download_button(
            label=f"💾 Salva",
            data=content,
            file_name=filename,
            mime=mime,
            use_container_width=True
        )


def _render_batch_export():
    """Renderizza sezione batch export."""
    saved_conversations = list_saved_conversations()
    
    if not saved_conversations:
        return
    
    st.markdown("---")
    st.markdown("### 🗂️ Batch Export")
    st.caption(f"📁 {len(saved_conversations)} conversazioni salvate")
    
    batch_format = st.selectbox(
        "Formato batch",
        options=list(EXPORT_FORMATS.keys()),
        key="batch_format",
        format_func=lambda x: f"{EXPORT_FORMATS[x]['icon']} {x}"
    )
    
    # Pulsante genera ZIP
    if st.button("📦 Genera ZIP", use_container_width=True, key="export_batch_zip_btn"):
        with st.spinner("Creazione ZIP in corso..."):
            zip_data = create_batch_export_zip(saved_conversations, batch_format)
            if zip_data:
                st.session_state["batch_zip_data"] = zip_data
                st.session_state["batch_zip_format"] = batch_format
                st.session_state["batch_zip_count"] = len(saved_conversations)
            else:
                st.session_state["batch_zip_data"] = None
                st.error("❌ Errore generazione ZIP")
    
    # Mostra download se ZIP generato
    if st.session_state.get("batch_zip_data"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"conversations_batch_{timestamp}.zip"
        zip_format = st.session_state.get("batch_zip_format", "Markdown")
        zip_count = st.session_state.get("batch_zip_count", 0)
        
        st.success(f"✅ ZIP pronto ({zip_count} conversazioni, {zip_format})")
        st.download_button(
            label="💾 Download ZIP",
            data=st.session_state["batch_zip_data"],
            file_name=zip_filename,
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )


def render_export_preview():
    """Renderizza anteprima export nel main."""
    if not st.session_state.get("show_export_preview"):
        return False
    
    st.markdown("---")
    st.subheader("👁️ Anteprima Export")
    
    preview_content_option = st.session_state.get("preview_content_option", "Conversazione completa")
    preview_format = st.session_state.get("preview_format", "Markdown")
    
    messages = st.session_state.get("messages", [])
    messages_to_preview = get_messages_for_export(messages, preview_content_option)
    
    conv_id = st.session_state.get("conversation_id", "N/A")
    metadata = {
        "conversation_id": conv_id,
        "created_at": st.session_state.get("conversation_created_at", ""),
        "last_updated": datetime.now().isoformat(),
        "model": st.session_state.get("current_model", ""),
        "provider": st.session_state.get("connection_type", ""),
        "tokens": estimate_conversation_tokens(messages)
    }
    
    if preview_format == "Markdown":
        preview_content = export_to_markdown(messages_to_preview, metadata)
        st.markdown(preview_content)
    elif preview_format == "JSON":
        preview_content = export_to_json(messages_to_preview, metadata)
        st.code(preview_content, language="json")
    elif preview_format == "TXT":
        preview_content = export_to_txt(messages_to_preview, metadata)
        st.text(preview_content)
    else:
        st.info("📕 Preview PDF non disponibile. Clicca 'Download' per generare il PDF.")
    
    def close_preview_callback():
        st.session_state["show_export_preview"] = False
        
    st.button("❌ Chiudi Anteprima", key="export_close_preview", on_click=close_preview_callback)
    
    return True
