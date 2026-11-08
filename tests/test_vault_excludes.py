# tests/test_vault_excludes.py
# DeepAiUG v1.16.1 — voce 9 del giro 8: le esclusioni dei vault valgono anche
# nell'indicizzazione.
# ============================================================================
# Fino alla 1.16.0 il conteggio dei file del pannello vault toglieva
# .obsidian/, templates/, .trash/, logseq/bak/..., ma LocalFolderAdapter (che
# legge davvero i file per la KB) non guardava exclude_patterns: quei file
# finivano nella Knowledge Base. Cartelle finte in tmp_path.
# ============================================================================

from pathlib import Path

import pytest

from rag.adapters.local_folder import LocalFolderAdapter
from rag.vault import detect_vault_type, scan_vault_files


def _write(root: Path, rel: str, text: str = "contenuto") -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


@pytest.fixture
def obsidian(tmp_path):
    root = tmp_path / "vault"
    _write(root, "nota.md", "nota vera")
    _write(root, "progetti/piano.md", "piano vero")
    _write(root, ".obsidian/workspace.md", "config di obsidian")
    _write(root, "templates/modello.md", "modello vuoto")
    _write(root, ".trash/vecchia.md", "nel cestino")
    _write(root, "progetti/templates/sotto.md", "modello in sottocartella")
    return root


@pytest.fixture
def logseq(tmp_path):
    root = tmp_path / "grafo"
    _write(root, "pages/pagina.md", "pagina vera")
    _write(root, "journals/2026_11_08.md", "diario vero")
    _write(root, "logseq/config.edn", "{}")
    _write(root, "logseq/bak/pages/pagina.md", "copia di backup")
    _write(root, "logseq/version-files/pagina.md", "versione vecchia")
    return root


def _rel_paths(adapter, root):
    return sorted(Path(d.path).relative_to(root).as_posix() for d in adapter.load_documents())


def test_obsidian_excludes_applied_by_adapter(obsidian):
    vi = detect_vault_type(str(obsidian))
    adapter = LocalFolderAdapter({"folder_path": str(obsidian), "extensions": vi["include_ext"],
                                  "recursive": True, "exclude_patterns": vi["exclude_patterns"]})
    assert _rel_paths(adapter, obsidian) == ["nota.md", "progetti/piano.md"]


def test_logseq_excludes_applied_by_adapter(logseq):
    vi = detect_vault_type(str(logseq))
    adapter = LocalFolderAdapter({"folder_path": str(logseq), "extensions": [".md"],
                                  "recursive": True, "exclude_patterns": vi["exclude_patterns"]})
    assert _rel_paths(adapter, logseq) == ["journals/2026_11_08.md", "pages/pagina.md"]


def test_vault_detected_even_without_patterns_in_config(obsidian):
    # «Percorso cartella» e la ricarica di una conversazione non passano
    # exclude_patterns: le esclusioni del tipo di vault valgono lo stesso
    adapter = LocalFolderAdapter({"folder_path": str(obsidian), "extensions": [".md"], "recursive": True})
    assert _rel_paths(adapter, obsidian) == ["nota.md", "progetti/piano.md"]


def test_extra_patterns_from_config(obsidian):
    adapter = LocalFolderAdapter({"folder_path": str(obsidian), "extensions": [".md"], "recursive": True,
                                  "exclude_patterns": ["progetti"]})
    assert _rel_paths(adapter, obsidian) == ["nota.md"]


def test_patterns_match_inside_vault_not_parent_path(tmp_path):
    # un vault che sta DENTRO una cartella chiamata «templates» non si svuota
    root = tmp_path / "templates" / "mio_vault"
    _write(root, ".obsidian/app.md", "config")
    _write(root, "nota.md", "nota vera")
    adapter = LocalFolderAdapter({"folder_path": str(root), "extensions": [".md"], "recursive": True})
    assert _rel_paths(adapter, root) == ["nota.md"]
    assert [p.name for p in scan_vault_files(str(root), detect_vault_type(str(root)))] == ["nota.md"]


def test_counter_and_adapter_agree(obsidian):
    vi = detect_vault_type(str(obsidian))
    counted = [p.relative_to(obsidian).as_posix() for p in scan_vault_files(str(obsidian), vi)]
    adapter = LocalFolderAdapter({"folder_path": str(obsidian), "extensions": vi["include_ext"], "recursive": True})
    assert sorted(counted) == _rel_paths(adapter, obsidian)
