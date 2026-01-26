# ui/__init__.py
# Datapizza v1.6.1 - UI Components Package
# ============================================================================

from ui.styles import (
    MAIN_CSS,
    CLOUD_INDICATOR_CSS,
    KB_INDICATOR_CSS,
    get_connection_indicator_css,
)

from ui.chat import (
    render_chat_message,
    render_chat_area,
    render_empty_state,
)

from ui.sidebar import (
    render_llm_config,
    render_knowledge_base_config,
    render_conversations_manager,
    render_export_section,
    render_export_preview,
)

# 🆕 v1.5.0 - File Upload
from ui.file_upload import (
    render_file_upload_widget,
    enrich_prompt_with_files,
    is_vision_model,
    store_pending_files,
    get_pending_files,
    clear_pending_files,
)

# 🆕 v1.5.0 - Privacy Warning
from ui.privacy_warning import (
    check_privacy_risk,
    render_privacy_dialog,
    handle_privacy_action,
    render_privacy_warning_banner,
    reset_privacy_flags,
    should_show_privacy_dialog,
    mark_documents_uploaded,
)

# 🆕 v1.6.1 - Socratic Module
from ui.socratic import (
    render_socratic_buttons,
    clear_socratic_cache,
)

__all__ = [
    # Styles
    "MAIN_CSS",
    "CLOUD_INDICATOR_CSS",
    "KB_INDICATOR_CSS",
    "get_connection_indicator_css",
    # Chat
    "render_chat_message",
    "render_chat_area",
    "render_empty_state",
    # Sidebar
    "render_llm_config",
    "render_knowledge_base_config",
    "render_conversations_manager",
    "render_export_section",
    "render_export_preview",
    # 🆕 v1.5.0 - File Upload
    "render_file_upload_widget",
    "enrich_prompt_with_files",
    "is_vision_model",
    "store_pending_files",
    "get_pending_files",
    "clear_pending_files",
    # 🆕 v1.5.0 - Privacy Warning
    "check_privacy_risk",
    "render_privacy_dialog",
    "handle_privacy_action",
    "render_privacy_warning_banner",
    "reset_privacy_flags",
    "should_show_privacy_dialog",
    "mark_documents_uploaded",
    # 🆕 v1.6.1 - Socratic
    "render_socratic_buttons",
    "clear_socratic_cache",
]