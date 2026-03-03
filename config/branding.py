# config/branding.py
# DeepAiUG v1.10.0 - Branding personalizzabile
# ============================================================================
# Carica branding.yaml dalla root del progetto.
# Fallback silenzioso ai valori default se il file manca o è malformato.
# ============================================================================

from .constants import BASE_DIR, VERSION

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

# Path file branding nella root del progetto
_BRANDING_FILE = BASE_DIR / "branding.yaml"

# Valori default (identici ai valori hardcoded originali)
_DEFAULTS: dict = {
    "app": {
        "title": "DeepAiUG Chat",
        "icon": "\U0001f9e0",
        "subtitle": "",
    },
    "news_banner": {
        "enabled": True,
        "text": "Architettura Sidebar — configurazione separata e UI più pulita",
        "version": VERSION,
    },
    # v1.11.1 - Matrix rain
    "matrix_rain": True,
    "matrix_rain_intensity": 0.055,
}


def load_branding() -> dict:
    """
    Carica configurazione branding da branding.yaml.

    Se il file non esiste, yaml non è disponibile, o il file è malformato,
    ritorna i valori default senza errori.

    Returns:
        Dict con sezioni 'app' e 'news_banner'
    """
    if not _YAML_AVAILABLE or not _BRANDING_FILE.exists():
        return _DEFAULTS

    try:
        with open(_BRANDING_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return _DEFAULTS

    if not isinstance(data, dict):
        return _DEFAULTS

    # Merge: i campi mancanti nel YAML prendono il valore default
    result: dict = {}
    for key, default_value in _DEFAULTS.items():
        if isinstance(default_value, dict):
            # Nested section — merge key-by-key
            user_section = data.get(key, {})
            if not isinstance(user_section, dict):
                user_section = {}
            result[key] = {**default_value, **user_section}
        else:
            # Scalar value — use user value if present, else default
            result[key] = data.get(key, default_value)

    return result


# ============================================================================
# Costanti di modulo — calcolate una sola volta all'import
# ============================================================================

_branding = load_branding()

APP_TITLE: str = _branding["app"]["title"]
APP_ICON: str = _branding["app"]["icon"]
APP_SUBTITLE: str = _branding["app"]["subtitle"]

NEWS_BANNER_ENABLED: bool = _branding["news_banner"]["enabled"]
NEWS_BANNER_TEXT: str = _branding["news_banner"]["text"]
NEWS_BANNER_VERSION: str = _branding["news_banner"]["version"]

# v1.11.1 - Matrix rain
MATRIX_RAIN_ENABLED: bool = _branding.get("matrix_rain", True)
MATRIX_RAIN_INTENSITY: float = float(_branding.get("matrix_rain_intensity", 0.055))
