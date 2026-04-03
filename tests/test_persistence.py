# tests/test_persistence.py
# DeepAiUG v1.14.2 — Test per get_vault_used()
# ============================================================================

from core.persistence import get_vault_used


def test_get_vault_used_default_false():
    """Chat pre-v1.14.2 senza campo vault_used → False"""
    conv = {"id": "x", "title": "test", "messages": []}
    assert get_vault_used(conv) == False


def test_get_vault_used_true():
    """Chat con vault_used esplicito True → True"""
    conv = {"id": "x", "vault_used": True, "messages": []}
    assert get_vault_used(conv) == True


def test_get_vault_used_false_explicit():
    """Chat con vault_used esplicito False → False"""
    conv = {"id": "x", "vault_used": False, "messages": []}
    assert get_vault_used(conv) == False
