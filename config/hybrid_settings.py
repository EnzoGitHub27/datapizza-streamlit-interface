# config/hybrid_settings.py
# DeepAiUG v1.16.0 (giro 3, P5) - La sezione `hybrid:` di security_settings.yaml
# ============================================================================
# Tutto spento per default. File assente, sezione assente o vuota → default.
# Chiavi sconosciute: ignorate. Valori sbagliati: HybridSettingsError, mai un
# ripiego silenzioso (un errore che spegnesse l'ibrido senza dirlo manderebbe
# testo in chiaro al cloud a chi crede di averlo acceso).
#
# Regole fisse (SPEC §7):
#   on_service_down.cloud  → solo "block": se rizzo-pii non risponde, verso
#                            fuori casa non parte niente
#   dove si anonimizza     → sempre fuori casa (cloud e host su internet,
#                            core/egress.py): APPLY_TO non è configurabile;
#                            una chiave `apply_to` nel file viene ignorata
#
# Nessuno lo usa ancora: il guard arriva con P6 (giro 4). Con l'ibrido spento
# l'app è identica alla 1.15.4.
# ============================================================================

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML è nei requisiti
    yaml = None

from .constants import SECURITY_SETTINGS_ALT, SECURITY_SETTINGS_FILE

APPLY_TO = ("cloud", "remote_public")
ANNONA_MODES = ("read", "gateway")
LOCAL_DOWN_CHOICES = ("proceed", "block")


class HybridSettingsError(ValueError):
    """La sezione `hybrid:` c'è ma ha un valore non accettato."""


@dataclass(frozen=True)
class PIISettings:
    enabled: bool = False
    url: str = "http://127.0.0.1:5005"
    timeout_s: float = 30.0
    exclude_tags: Tuple[str, ...] = ()

    @property
    def apply_to(self) -> Tuple[str, ...]:
        """Fisso (decisione di Gilles, giro 4): fuori casa si anonimizza sempre."""
        return APPLY_TO


@dataclass(frozen=True)
class AnnonaSettings:
    enabled: bool = False
    url: str = "http://127.0.0.1:7070"
    mode: str = "read"


@dataclass(frozen=True)
class HybridSettings:
    pii: PIISettings = field(default_factory=PIISettings)
    annona: AnnonaSettings = field(default_factory=AnnonaSettings)
    on_service_down_cloud: str = "block"
    on_service_down_local: str = "proceed"

    @property
    def enabled(self) -> bool:
        """True se almeno un servizio è acceso."""
        return self.pii.enabled or self.annona.enabled


DEFAULTS = HybridSettings()


# ----------------------------------------------------------------------------
# Controlli dei valori
# ----------------------------------------------------------------------------

def _section(raw: Dict[str, Any], key: str, where: str) -> Dict[str, Any]:
    value = raw.get(key)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise HybridSettingsError(f"{where}.{key} deve essere una sezione, non {type(value).__name__}")
    return value


def _bool(raw: Dict[str, Any], key: str, default: bool, where: str) -> bool:
    value = raw.get(key, default)
    if not isinstance(value, bool):
        raise HybridSettingsError(f"{where}.{key} deve essere true o false, non {value!r}")
    return value


def _str(raw: Dict[str, Any], key: str, default: str, where: str) -> str:
    value = raw.get(key, default)
    if not isinstance(value, str) or not value.strip():
        raise HybridSettingsError(f"{where}.{key} deve essere un testo non vuoto, non {value!r}")
    return value.strip()


def _choice(raw: Dict[str, Any], key: str, default: str, choices, where: str) -> str:
    value = raw.get(key, default)
    if value not in choices:
        allowed = ", ".join(f'"{c}"' for c in choices)
        raise HybridSettingsError(f"{where}.{key} accetta solo {allowed}, non {value!r}")
    return value


def _str_list(raw: Dict[str, Any], key: str, default, where: str) -> Tuple[str, ...]:
    value = raw.get(key, list(default))
    if value is None:
        value = []
    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
        raise HybridSettingsError(f"{where}.{key} deve essere un elenco di testi, non {value!r}")
    return tuple(dict.fromkeys(v.strip() for v in value))


def parse_hybrid_settings(raw: Optional[Dict[str, Any]]) -> HybridSettings:
    """Dal dizionario della sezione `hybrid:` (o None) alle impostazioni."""
    if raw is None:
        return DEFAULTS
    if not isinstance(raw, dict):
        raise HybridSettingsError(f"hybrid deve essere una sezione, non {type(raw).__name__}")

    p = _section(raw, "pii", "hybrid")
    timeout = p.get("timeout_s", PIISettings.timeout_s)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
        raise HybridSettingsError(f"hybrid.pii.timeout_s deve essere un numero positivo, non {timeout!r}")
    pii = PIISettings(
        enabled=_bool(p, "enabled", False, "hybrid.pii"),
        url=_str(p, "url", PIISettings.url, "hybrid.pii"),
        timeout_s=float(timeout),
        exclude_tags=_str_list(p, "exclude_tags", (), "hybrid.pii"),
    )

    a = _section(raw, "annona", "hybrid")
    annona = AnnonaSettings(
        enabled=_bool(a, "enabled", False, "hybrid.annona"),
        url=_str(a, "url", AnnonaSettings.url, "hybrid.annona"),
        mode=_choice(a, "mode", "read", ANNONA_MODES, "hybrid.annona"),
    )

    d = _section(raw, "on_service_down", "hybrid")
    cloud = d.get("cloud", "block")
    if cloud != "block":
        raise HybridSettingsError(
            f"hybrid.on_service_down.cloud accetta solo \"block\", non {cloud!r}: "
            "se rizzo-pii non risponde, verso fuori casa non parte niente"
        )
    local = _choice(d, "local", "proceed", LOCAL_DOWN_CHOICES, "hybrid.on_service_down")

    return HybridSettings(pii=pii, annona=annona, on_service_down_cloud="block", on_service_down_local=local)


def _find_settings_file() -> Optional[Path]:
    for path in (SECURITY_SETTINGS_FILE, SECURITY_SETTINGS_ALT):
        if path.exists():
            return path
    return None


def load_hybrid_settings(path: Optional[Path] = None) -> HybridSettings:
    """
    Legge `hybrid:` da security_settings.yaml (radice del progetto, poi config/).

    - file assente → DEFAULTS (tutto spento)
    - YAML illeggibile → HybridSettingsError (non si sa se l'ibrido era acceso)
    - sezione assente o vuota → DEFAULTS
    """
    path = Path(path) if path is not None else _find_settings_file()
    if path is None or not path.exists():
        return DEFAULTS
    if yaml is None:  # pragma: no cover
        raise HybridSettingsError("PyYAML non installato: impossibile leggere security_settings.yaml")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise HybridSettingsError(f"{path.name} non è YAML valido: {e}") from e
    if not isinstance(data, dict):
        raise HybridSettingsError(f"{path.name} deve contenere delle sezioni")
    return parse_hybrid_settings(data.get("hybrid"))
