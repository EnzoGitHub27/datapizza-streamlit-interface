# tests/test_hybrid_settings.py
# DeepAiUG v1.16.0 (giro 3, P5) — La sezione `hybrid:` di security_settings.yaml
# ============================================================================

import pytest

from config.hybrid_settings import (
    DEFAULTS,
    HybridSettingsError,
    load_hybrid_settings,
    parse_hybrid_settings,
)
from config.settings import load_security_settings, should_show_saved_api_keys


def _write(tmp_path, text):
    path = tmp_path / "security_settings.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_defaults_all_off():
    assert DEFAULTS.enabled is False
    assert DEFAULTS.pii.enabled is False and DEFAULTS.annona.enabled is False
    assert DEFAULTS.pii.url == "http://127.0.0.1:5005"
    assert DEFAULTS.pii.exclude_tags == ()
    assert DEFAULTS.annona.mode == "read"
    assert DEFAULTS.on_service_down_cloud == "block"
    assert DEFAULTS.on_service_down_local == "proceed"


def test_file_missing(tmp_path):
    assert load_hybrid_settings(tmp_path / "non_esiste.yaml") == DEFAULTS


def test_section_missing(tmp_path):
    path = _write(tmp_path, "cloud_api_keys:\n  show_saved_keys: false\n")
    assert load_hybrid_settings(path) == DEFAULTS


def test_section_empty(tmp_path):
    assert load_hybrid_settings(_write(tmp_path, "hybrid:\n")) == DEFAULTS


def test_repo_file_is_all_off():
    """Il security_settings.yaml del repo ha la sezione, tutta spenta."""
    s = load_hybrid_settings()
    assert s == DEFAULTS


def test_cloud_allow_rejected(tmp_path):
    path = _write(tmp_path, "hybrid:\n  on_service_down:\n    cloud: allow\n")
    with pytest.raises(HybridSettingsError, match="block"):
        load_hybrid_settings(path)


@pytest.mark.parametrize("value", ["proceed", "", None, True])
def test_cloud_only_block(value):
    with pytest.raises(HybridSettingsError):
        parse_hybrid_settings({"on_service_down": {"cloud": value}})


def test_pii_on_with_tags(tmp_path):
    path = _write(tmp_path, (
        "hybrid:\n"
        "  pii:\n"
        "    enabled: true\n"
        "    timeout_s: 10\n"
        "    exclude_tags: [AMOUNT, DATE, AMOUNT]\n"
        "  annona:\n"
        "    enabled: true\n"
        "    mode: gateway\n"
        "  sconosciuta: 1\n"
    ))
    s = load_hybrid_settings(path)
    assert s.enabled and s.pii.enabled and s.annona.enabled
    assert s.pii.timeout_s == 10.0
    assert s.pii.exclude_tags == ("AMOUNT", "DATE")  # senza doppioni
    assert s.annona.mode == "gateway"


@pytest.mark.parametrize(
    "raw",
    [
        {"pii": {"enabled": "sì"}},                    # non booleano
        {"pii": {"timeout_s": 0}},
        {"pii": {"timeout_s": "30"}},
        {"pii": {"exclude_tags": "AMOUNT"}},           # non elenco
        {"pii": {"apply_to": ["cloud"]}},              # manca remote_public
        {"pii": {"apply_to": ["cloud", "remote_public", "local"]}},
        {"pii": {"url": ""}},
        {"annona": {"mode": "auto"}},
        {"on_service_down": {"local": "allow"}},
        {"pii": "on"},                                 # sezione non dizionario
        ["pii"],
    ],
)
def test_bad_values_rejected(raw):
    with pytest.raises(HybridSettingsError):
        parse_hybrid_settings(raw)


def test_broken_yaml_is_an_error_not_off(tmp_path):
    """Un file rotto non spegne l'ibrido in silenzio."""
    path = _write(tmp_path, "hybrid:\n  pii: [enabled: true\n")
    with pytest.raises(HybridSettingsError, match="YAML"):
        load_hybrid_settings(path)


def test_existing_settings_still_read():
    """La sezione nuova non cambia la lettura di cloud_api_keys (1.15.4)."""
    config = load_security_settings()
    assert config is not None and "hybrid" in config
    assert should_show_saved_api_keys(config) is False
