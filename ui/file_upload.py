# ui/file_upload.py
# DeepAiUG v1.5.0 - Componente File Upload per Chat
# ============================================================================
#
# Widget per upload file nella chat con:
# - Controllo privacy (blocco su Cloud provider)
# - Rilevamento automatico modelli Vision
# - Anteprima file caricati
# - Supporto documenti e immagini
# - 🆕 Tracciamento documenti per warning privacy
#
# ============================================================================

import streamlit as st
from typing import List, Optional, Tuple

from config import (
    ALLOWED_UPLOAD_TYPES,
    VISION_MODEL_PATTERNS,
    MAX_FILE_SIZE_MB,
)
from core.file_processors import (
    ProcessedFile,
    process_multiple_files,
    build_document_context,
    get_images_for_vision,
    get_attachment_names,
)


# ============================================================================
# VISION MODEL DETECTION
# ============================================================================

def is_vision_model(model_name: str) -> bool:
    """
    Verifica se il modello supporta input visivi (immagini).
    
    Usa pattern matching sui nomi comuni di modelli Vision.
    
    Args:
        model_name: Nome del modello Ollama/LLM
        
    Returns:
        True se il modello supporta immagini
    """
    if not model_name:
        return False
    
    model_lower = model_name.lower()
    return any(pattern in model_lower for pattern in VISION_MODEL_PATTERNS)


# ============================================================================
# FORMATTING HELPERS
# ============================================================================

def _format_file_size(size_bytes: int) -> str:
    """Formatta dimensione file in formato leggibile."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def _get_file_icon(processed_file: ProcessedFile) -> str:
    """Ritorna emoji appropriata per tipo file."""
    if processed_file.file_type == "image":
        return "🖼️"
    
    ext = processed_file.filename.split(".")[-1].lower()
    icons = {
        "pdf": "📕",
        "docx": "📘",
        "txt": "📄",
        "md": "📝",
    }
    return icons.get(ext, "📎")


# ============================================================================
# PRIVACY TRACKING - v1.5.0
# ============================================================================

def _mark_documents_uploaded(filenames: List[str]):
    """
    Segna che sono stati caricati documenti nella sessione.
    
    Questo flag viene usato per mostrare il warning privacy
    quando l'utente tenta di passare a Cloud provider.
    
    Args:
        filenames: Lista dei nomi file caricati
    """
    if not filenames:
        return
    
    # Segna che ci sono documenti in sessione
    st.session_state["documents_uploaded_this_session"] = True
    
    # Mantieni storico dei file (per mostrare nel warning)
    history = st.session_state.get("uploaded_files_history", [])
    for name in filenames:
        if name not in history:
            history.append(name)
    st.session_state["uploaded_files_history"] = history
    
    # Resetta il consenso precedente (nuovi documenti = nuovo rischio)
    st.session_state["privacy_acknowledged_for_cloud"] = False


# ============================================================================
# PREVIEW COMPONENT
# ============================================================================

def render_file_preview(
    files: List[ProcessedFile], 
    show_images: bool = True,
    key_prefix: str = "preview"
):
    """
    Renderizza anteprima dei file caricati con possibilità di rimozione.
    
    Args:
        files: Lista di ProcessedFile
        show_images: Se mostrare anteprime immagini (False se modello non-Vision)
        key_prefix: Prefisso per chiavi Streamlit (per evitare conflitti)
    """
    if not files:
        return
    
    st.markdown(f"**📎 {len(files)} file allegati:**")
    
    for i, f in enumerate(files):
        icon = _get_file_icon(f)
        size = _format_file_size(f.size_bytes)
        
        with st.expander(f"{icon} {f.filename} ({size})", expanded=False):
            # Mostra errore se presente
            if f.error:
                st.error(f.error)
            
            # Immagine con anteprima
            elif f.file_type == "image":
                if show_images and f.preview:
                    st.image(
                        f"data:image/png;base64,{f.preview}",
                        caption=f.filename,
                        width=200
                    )
                elif show_images and f.content:
                    # Fallback: mostra immagine originale ridotta
                    st.image(
                        f"data:{f.mime_type};base64,{f.content}",
                        caption=f.filename,
                        width=200
                    )
                else:
                    st.info("🖼️ Immagine caricata (anteprima non disponibile)")
            
            # Documento con anteprima testo
            elif f.file_type == "document":
                st.text_area(
                    "Anteprima contenuto",
                    f.preview,
                    height=120,
                    disabled=True,
                    key=f"{key_prefix}_{i}_{f.filename}"
                )


# ============================================================================
# MAIN UPLOAD WIDGET
# ============================================================================

def render_file_upload_widget(
    connection_type: str,
    current_model: str,
    key: str = "chat_file_upload"
) -> Tuple[List[ProcessedFile], bool, Optional[str]]:
    """
    Renderizza il widget di upload file con controlli privacy.
    
    IMPORTANTE: Questo widget deve essere posizionato FUORI dal form
    in quanto st.file_uploader non funziona correttamente dentro st.form.
    
    Args:
        connection_type: "Local (Ollama)" | "Remote host" | "Cloud provider"
        current_model: Nome del modello selezionato
        key: Chiave univoca per st.file_uploader
        
    Returns:
        Tuple:
        - processed_files: Lista di file processati pronti per l'uso
        - has_valid_images: True se ci sono immagini valide per Vision
        - warning_message: Messaggio di warning (o None)
    """
    processed_files = []
    has_valid_images = False
    warning_message = None
    
    # ========== BLOCCO CLOUD PROVIDER (PRIVACY) ==========
    if connection_type == "Cloud provider":
        st.warning(
            "📎 **Upload file disabilitato per privacy**\n\n"
            "Stai usando un Cloud provider. Per proteggere i tuoi documenti, "
            "l'upload è disponibile solo con **Ollama locale** o **Remote host**."
        )
        return [], False, "Cloud provider - upload disabilitato per privacy"
    
    # ========== FILE UPLOADER ==========
    st.markdown("##### 📎 Allega file (opzionale)")
    
    uploaded_files = st.file_uploader(
        "Trascina o seleziona file",
        type=ALLOWED_UPLOAD_TYPES,
        accept_multiple_files=True,
        key=key,
        help=(
            f"Max {MAX_FILE_SIZE_MB}MB per file.\n"
            "📄 Documenti: PDF, TXT, MD, DOCX → testo aggiunto al messaggio\n"
            "🖼️ Immagini: PNG, JPG → richiede modello Vision (es. LLaVA)"
        ),
        label_visibility="collapsed"
    )
    
    # Se nessun file caricato, ritorna vuoto
    if not uploaded_files:
        return [], False, None
    
    # ========== PROCESSA FILE ==========
    processed_files = process_multiple_files(uploaded_files)
    
    # Separa documenti e immagini
    documents = [f for f in processed_files if f.file_type == "document"]
    images = [f for f in processed_files if f.file_type == "image"]
    errors = [f for f in processed_files if f.error]
    
    # 🆕 v1.5.0 - Marca i documenti caricati per tracking privacy
    valid_filenames = [f.filename for f in processed_files if not f.error]
    if valid_filenames:
        _mark_documents_uploaded(valid_filenames)
    
    # ========== CONTROLLO MODELLO VISION ==========
    model_is_vision = is_vision_model(current_model)
    
    if images and not model_is_vision:
        st.warning(
            f"⚠️ **Immagini rilevate** ma il modello `{current_model}` non supporta Vision.\n\n"
            "Le immagini verranno **ignorate**. Per analizzare immagini usa un modello Vision:\n"
            "• LLaVA, LLaVA-Llama3\n"
            "• Granite3.2-Vision\n"
            "• Moondream, BakLLaVA"
        )
        # Rimuovi immagini dalla lista
        processed_files = documents + errors
        has_valid_images = False
        warning_message = f"Immagini ignorate - {current_model} non supporta Vision"
    else:
        has_valid_images = len(images) > 0 and model_is_vision
    
    # ========== MOSTRA ERRORI ==========
    if errors:
        for err_file in errors:
            st.error(f"❌ {err_file.filename}: {err_file.error}")
    
    # ========== ANTEPRIMA FILE VALIDI ==========
    valid_files = [f for f in processed_files if not f.error]
    if valid_files:
        render_file_preview(
            valid_files, 
            show_images=has_valid_images,
            key_prefix=key
        )
    
    return processed_files, has_valid_images, warning_message


# ============================================================================
# PROMPT ENRICHMENT
# ============================================================================

def enrich_prompt_with_files(
    user_message: str,
    processed_files: List[ProcessedFile],
    include_images: bool = False
) -> Tuple[str, Optional[List[dict]]]:
    """
    Arricchisce il prompt utente con il contenuto dei file allegati.
    
    Per documenti: aggiunge il testo estratto al prompt
    Per immagini: prepara la lista per API multimodal (se include_images=True)
    
    Args:
        user_message: Messaggio originale dell'utente
        processed_files: File processati dal widget
        include_images: Se True, prepara anche le immagini per Vision
        
    Returns:
        Tuple:
        - enriched_prompt: Prompt con contenuto documenti
        - images_data: Lista dict per immagini (o None se non ci sono/non richieste)
    """
    # Filtra solo file senza errori
    valid_files = [f for f in processed_files if not f.error]
    
    if not valid_files:
        return user_message, None
    
    # ========== AGGIUNGI DOCUMENTI AL PROMPT ==========
    doc_context = build_document_context(valid_files)
    
    if doc_context:
        enriched_prompt = f"""--- FILE ALLEGATI ---
{doc_context}
--- FINE FILE ALLEGATI ---

{user_message}"""
    else:
        enriched_prompt = user_message
    
    # ========== PREPARA IMMAGINI PER VISION ==========
    images_data = None
    if include_images:
        images_list = get_images_for_vision(valid_files)
        if images_list:
            images_data = images_list
    
    return enriched_prompt, images_data


# ============================================================================
# SESSION STATE HELPERS
# ============================================================================

def clear_pending_files():
    """Pulisce i file in attesa dopo l'invio del messaggio."""
    keys_to_clear = [
        "pending_files",
        "pending_has_images", 
        "pending_warning"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def store_pending_files(
    processed_files: List[ProcessedFile],
    has_images: bool,
    warning: Optional[str]
):
    """
    Salva i file processati in session_state per il submit.
    
    Necessario perché file_uploader è fuori dal form.
    """
    st.session_state["pending_files"] = processed_files
    st.session_state["pending_has_images"] = has_images
    st.session_state["pending_warning"] = warning


def get_pending_files() -> Tuple[List[ProcessedFile], bool, Optional[str]]:
    """
    Recupera i file in attesa da session_state.
    
    Returns:
        Tuple (files, has_images, warning)
    """
    return (
        st.session_state.get("pending_files", []),
        st.session_state.get("pending_has_images", False),
        st.session_state.get("pending_warning")
    )
