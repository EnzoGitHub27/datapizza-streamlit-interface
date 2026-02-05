# core/__init__.py
# DeepAiUG v1.4.0 - Modulo core
# ============================================================================

from .llm_client import (
    get_local_ollama_models,
    get_remote_ollama_models,
    create_client,
)

from .persistence import (
    ensure_conversations_dir,
    get_conversation_filename,
    save_conversation,
    load_conversation,
    list_saved_conversations,
    delete_conversation,
    get_conversation_preview,
    extract_kb_settings,
)

from .conversation import (
    create_message,
    get_conversation_history,
    estimate_tokens,
    estimate_conversation_tokens,
    generate_conversation_id,
    build_rag_prompt,
    format_time_from_iso,
)

__all__ = [
    # LLM Client
    "get_local_ollama_models",
    "get_remote_ollama_models",
    "create_client",
    # Persistence
    "ensure_conversations_dir",
    "get_conversation_filename",
    "save_conversation",
    "load_conversation",
    "list_saved_conversations",
    "delete_conversation",
    "get_conversation_preview",
    "extract_kb_settings",
    # Conversation
    "create_message",
    "get_conversation_history",
    "estimate_tokens",
    "estimate_conversation_tokens",
    "generate_conversation_id",
    "build_rag_prompt",
    "format_time_from_iso",
]
