# tests/test_delete_kb_chat.py
# DeepAiUG v1.15.4 — «Elimina» toglie la chat anche dalla KB Chat, e
# «Aggiorna KB Chat» toglie le chat orfane.
# ============================================================================
# Conversazioni inventate, cartella conversazioni e vectorstore temporanei.
# ============================================================================

import json
from unittest.mock import patch

import pytest

from tests.test_kb_chat_indexer import _make_chat


@pytest.fixture
def sandbox(tmp_path):
    """Cartella conversazioni, vectorstore e meta file tutti in tmp_path."""
    conv_dir = tmp_path / "conversations"
    conv_dir.mkdir()
    with patch("core.persistence.CONVERSATIONS_DIR", conv_dir), \
         patch("core.kb_chat_indexer.CHAT_KB_PERSIST_PATH", str(tmp_path / "chat_kb_vs")), \
         patch("core.kb_chat_indexer.CHAT_KB_META_FILE", tmp_path / "chat_kb_meta.json"):
        yield conv_dir


def _save(conv_dir, chat):
    path = conv_dir / f"conv_{chat['conversation_id']}.json"
    path.write_text(json.dumps(chat, ensure_ascii=False), encoding="utf-8")
    return path


def _index(chat):
    from core.kb_chat_indexer import index_chat_to_kb
    n = index_chat_to_kb(chat)
    assert n > 0
    return n


def test_delete_removes_file_and_chunks(sandbox):
    from core.kb_chat_indexer import delete_conversation_and_kb, get_chunks_per_chat

    chat = _make_chat("preventivo_ferrolago")
    path = _save(sandbox, chat)
    n = _index(chat)
    assert get_chunks_per_chat().get("preventivo_ferrolago") == n

    result = delete_conversation_and_kb("preventivo_ferrolago")

    assert result == {"file_deleted": True, "kb_chunks_removed": n, "kb_ok": True}
    assert not path.exists()
    assert "preventivo_ferrolago" not in get_chunks_per_chat()


def test_delete_leaves_other_chats(sandbox):
    from core.kb_chat_indexer import delete_conversation_and_kb, get_chunks_per_chat

    a, b = _make_chat("chat_a"), _make_chat("chat_b")
    _save(sandbox, a), _save(sandbox, b)
    _index(a), _index(b)

    delete_conversation_and_kb("chat_a")

    chunks = get_chunks_per_chat()
    assert "chat_a" not in chunks
    assert chunks.get("chat_b", 0) > 0


def test_delete_chat_not_in_kb(sandbox):
    from core.kb_chat_indexer import delete_conversation_and_kb

    chat = _make_chat("solo_file", includi_in_kb=False)
    path = _save(sandbox, chat)

    result = delete_conversation_and_kb("solo_file")

    assert result["file_deleted"] is True
    assert result["kb_chunks_removed"] == 0
    assert not path.exists()


def test_delete_with_kb_unavailable_still_deletes_file(sandbox):
    from core import kb_chat_indexer

    chat = _make_chat("senza_chroma")
    path = _save(sandbox, chat)
    with patch.object(kb_chat_indexer, "_get_chroma_collection", return_value=(None, None)):
        result = kb_chat_indexer.delete_conversation_and_kb("senza_chroma")
    assert result["file_deleted"] is True
    assert not path.exists()


def test_orphans_removed_on_reindex(sandbox):
    from core.kb_chat_indexer import get_chunks_per_chat, reindex_all_chat_kb

    vecchia = _make_chat("eliminata_a_mano")
    sfilata = _make_chat("non_piu_inclusa")
    tenuta = _make_chat("ancora_inclusa")
    p_vecchia = _save(sandbox, vecchia)
    _save(sandbox, sfilata), _save(sandbox, tenuta)
    for c in (vecchia, sfilata, tenuta):
        _index(c)

    # 1.15.3: il file cancellato lasciava i chunk; e una chat tolta dalla KB
    p_vecchia.unlink()
    sfilata["kb_metadata"]["includi_in_kb"] = False
    _save(sandbox, sfilata)

    result = reindex_all_chat_kb()

    chunks = get_chunks_per_chat()
    assert result["orphans_removed"] == 2
    assert "eliminata_a_mano" not in chunks
    assert "non_piu_inclusa" not in chunks
    assert chunks.get("ancora_inclusa", 0) > 0


def test_unreadable_file_is_kept(sandbox):
    """Nel dubbio non si cancella: file illeggibile → chunk tenuti."""
    from core.kb_chat_indexer import get_chunks_per_chat, remove_orphan_chats_from_kb

    chat = _make_chat("file_rotto")
    path = _save(sandbox, chat)
    _index(chat)
    path.write_text("{non è json", encoding="utf-8")

    assert remove_orphan_chats_from_kb() == []
    assert get_chunks_per_chat().get("file_rotto", 0) > 0
