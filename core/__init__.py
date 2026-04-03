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
    get_kb_metadata,
    KB_METADATA_DEFAULT,
    update_conversation_kb_metadata,
    get_vault_used,
)

from .kb_chat_indexer import (
    index_chat_to_kb,
    remove_chat_from_kb,
    get_kb_chat_stats,
    search_chat_kb,
    reindex_all_chat_kb,
    get_chunks_per_chat,
    load_chat_kb_meta,
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
    "get_kb_metadata",
    "KB_METADATA_DEFAULT",
    "update_conversation_kb_metadata",
    # KB Chat Indexer (v1.14.0)
    "index_chat_to_kb",
    "remove_chat_from_kb",
    "get_kb_chat_stats",
    "search_chat_kb",
    "reindex_all_chat_kb",
    "get_chunks_per_chat",
    "load_chat_kb_meta",
    # Conversation
    "create_message",
    "get_conversation_history",
    "estimate_tokens",
    "estimate_conversation_tokens",
    "generate_conversation_id",
    "build_rag_prompt",
    "format_time_from_iso",
]
