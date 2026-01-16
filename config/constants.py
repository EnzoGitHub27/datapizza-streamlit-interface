# config/constants.py
# Datapizza v1.5.0 - Costanti globali
# ============================================================================

from pathlib import Path

# ============================================================================
# VERSIONE
# ============================================================================

VERSION = "1.5.1"
VERSION_STRING = f"v{VERSION}"
VERSION_DESCRIPTION = "Wiki Bugfix + Test Sources"

# ============================================================================
# PATHS
# ============================================================================

# Base directory (parent della cartella config)
BASE_DIR = Path(__file__).parent.parent

# Directory per dati
CONVERSATIONS_DIR = BASE_DIR / "conversations"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
WIKI_CACHE_DIR = BASE_DIR / "wiki_cache"
SECRETS_DIR = BASE_DIR / "secrets"

# File di configurazione
WIKI_CONFIG_FILE = BASE_DIR / "wiki_sources.yaml"
WIKI_CONFIG_ALT = BASE_DIR / "config" / "wiki_sources.yaml"

# ============================================================================
# DEFAULTS - CONVERSAZIONE
# ============================================================================

DEFAULT_MAX_MESSAGES = 50
DEFAULT_MAX_TOKENS_ESTIMATE = 8000

# ============================================================================
# DEFAULTS - RAG
# ============================================================================

DEFAULT_CHUNK_SIZE = 1000  # caratteri
DEFAULT_CHUNK_OVERLAP = 200  # caratteri
DEFAULT_TOP_K_RESULTS = 5  # documenti per query

# ============================================================================
# FORMATI FILE SUPPORTATI
# ============================================================================

SUPPORTED_EXTENSIONS = {
    ".md": "Markdown",
    ".txt": "Testo",
    ".html": "HTML",
    ".htm": "HTML",
    ".pdf": "PDF",
}

# ============================================================================
# EXPORT FORMATS
# ============================================================================

EXPORT_FORMATS = {
    "Markdown": {"ext": ".md", "icon": "📝", "mime": "text/markdown"},
    "JSON": {"ext": ".json", "icon": "📋", "mime": "application/json"},
    "TXT": {"ext": ".txt", "icon": "📄", "mime": "text/plain"},
    "PDF": {"ext": ".pdf", "icon": "📕", "mime": "application/pdf"},
}

CONTENT_OPTIONS = {
    "Conversazione completa": None,
    "Ultimi 10 messaggi": 10,
    "Ultimi 20 messaggi": 20,
    "Ultimi 50 messaggi": 50,
}

# ============================================================================
# UI - COLORI
# ============================================================================

USER_MESSAGE_COLOR = "#E3F2FD"
ASSISTANT_MESSAGE_COLOR = "#F5F5F5"
USER_MESSAGE_COLOR_DARK = "#1E3A5F"
ASSISTANT_MESSAGE_COLOR_DARK = "#2D2D2D"

# ============================================================================
# PROVIDERS CLOUD
# ============================================================================

CLOUD_PROVIDERS = {
    "OpenAI": {
        "key_name": "openai",
        "env_var": "OPENAI_API_KEY",
        "default_model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
    },
    "Anthropic (Claude)": {
        "key_name": "anthropic",
        "env_var": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-20250514",
        "base_url": "https://api.anthropic.com",
    },
    "Google Gemini": {
        "key_name": "google",
        "env_var": "GOOGLE_API_KEY",
        "default_model": "gemini-1.5-pro",
        "base_url": "https://generativelanguage.googleapis.com",
    },
    "Custom": {
        "key_name": "custom",
        "env_var": "CUSTOM_API_KEY",
        "default_model": "",
        "base_url": "",
    },
}

# ============================================================================
# MEDIAWIKI DEFAULTS
# ============================================================================

MEDIAWIKI_DEFAULT_USER_AGENT = f"DatapizzaBot/{VERSION}"
MEDIAWIKI_DEFAULT_REQUEST_DELAY = 0.5
MEDIAWIKI_DEFAULT_BATCH_SIZE = 50
MEDIAWIKI_DEFAULT_TIMEOUT = 30

# ============================================================================
# WIKI TYPES SUPPORTATI
# ============================================================================

WIKI_TYPES = {
    "mediawiki": {
        "name": "MediaWiki",
        "icon": "🌐",
        "description": "Wikipedia, wiki aziendali (mwclient)",
        "package": "mwclient",
    },
    "dokuwiki": {
        "name": "DokuWiki",
        "icon": "📘",
        "description": "Wiki leggera per documentazione tecnica",
        "package": "dokuwiki",
    },
    "local": {
        "name": "Cartella Locale",
        "icon": "📁",
        "description": "File locali (MD, TXT, HTML, PDF)",
        "package": None,
    },
}

# ============================================================================
# FILE UPLOAD IN CHAT - v1.5.0
# ============================================================================

# Estensioni per st.file_uploader (senza punto)
ALLOWED_UPLOAD_TYPES = ["pdf", "txt", "md", "docx", "png", "jpg", "jpeg", "gif", "webp"]

# Pattern per rilevare modelli Vision (case-insensitive)
VISION_MODEL_PATTERNS = [
    "llava",
    "llava-llama3",
    "llava-phi3",
    "llava-v1.6",
    "granite3-vision",
    "granite3.2-vision",
    "moondream",
    "bakllava",
    "cogvlm",
    "fuyu",
    "minicpm-v",
]

# Limiti upload
MAX_FILE_SIZE_MB = 10
MAX_DOCUMENT_CHARS = 50000
