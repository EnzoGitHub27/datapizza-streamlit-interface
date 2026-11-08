# tests/test_windows_installer.py
# DeepAiUG v1.16.1 — voce 37 del giro 8: l'installer Windows su una macchina pulita.
# ============================================================================
# Qui Windows non c'è: si controlla il testo di installer/INSTALLA_DeepAiUG.bat.
#   1. la cartella di destinazione si crea PRIMA dei download (Python, Ollama
#      e lo ZIP vanno in !DEST!): su una macchina pulita il download falliva;
#   2. Ollama si cerca anche dove lo mette OllamaSetup
#      (%LOCALAPPDATA%\Programs\Ollama), la stessa cartella aggiunta al PATH;
#   3. il Python trovato nel PATH si prova davvero (versione >= 3.10): l'alias
#      del Microsoft Store o un Python vecchio non vanno bene.
# La prova vera resta da fare su un Windows pulito (vedi CHANGELOG 1.16.1).
# ============================================================================

import re
from pathlib import Path

BAT = Path(__file__).resolve().parent.parent / "installer" / "INSTALLA_DeepAiUG.bat"


def _lines():
    return BAT.read_text(encoding="utf-8").splitlines()


def _code(lines):
    """Le righe vere, senza i commenti «::» e «rem»."""
    return [(i, l) for i, l in enumerate(lines)
            if l.strip() and not l.strip().startswith("::") and not l.strip().lower().startswith("rem ")]


def test_dest_created_before_any_download():
    code = _code(_lines())
    mkdir = [i for i, l in code if re.search(r'mkdir\s+"!DEST!"', l)]
    downloads = [i for i, l in code if l.strip().lower().startswith("call :downloadfile")]
    assert mkdir and downloads
    assert min(mkdir) < min(downloads), "la cartella va creata prima del primo download"


def test_dest_creation_checked():
    text = BAT.read_text(encoding="utf-8")
    block = text[text.index('mkdir "!DEST!"'):][:400]
    assert "ERRORE" in block, "se la cartella non si crea, l'installer deve dirlo e fermarsi"


def test_ollama_searched_where_setup_installs_it():
    text = BAT.read_text(encoding="utf-8")
    assert r'if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe"' in text
    # e la stessa cartella finisce nel PATH della sessione
    assert r'%LOCALAPPDATA%\Programs\Ollama' in text[text.index("set \"PATH="):][:200]


def test_python_from_path_is_checked():
    text = BAT.read_text(encoding="utf-8")
    start = text.index(":: Prova PATH")
    block = text[start:start + 1500]
    assert "sys.version_info" in block, "il python del PATH va provato, non preso a scatola chiusa"
    assert "(3, 10)" in block or "(3,10)" in block
