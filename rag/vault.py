# rag/vault.py
# DeepAiUG v1.13.0 - F3 Vault Support
# ============================================================================
# Riconoscimento automatico vault Obsidian, LogSeq, Notion Export.
# Filtro file per tipo vault, parser .canvas, aggiornamento incrementale.
# ============================================================================

import json
from pathlib import Path

from config.constants import VAULT_TYPES


def detect_vault_type(folder_path: str) -> dict:
    """
    Rileva automaticamente il tipo di vault.
    Controlla la struttura della cartella e ritorna
    il dizionario corrispondente da VAULT_TYPES.
    """
    path = Path(folder_path)

    if (path / '.obsidian').is_dir():
        return {**VAULT_TYPES['obsidian'], 'type': 'obsidian'}

    if (path / 'logseq').is_dir():
        return {**VAULT_TYPES['logseq'], 'type': 'logseq'}

    if list(path.glob('_index*.csv')):
        return {**VAULT_TYPES['notion'], 'type': 'notion'}

    return {**VAULT_TYPES['folder'], 'type': 'folder'}


def scan_vault_files(folder_path: str, vault_info: dict) -> list:
    """
    Restituisce la lista dei Path da indicizzare,
    filtrata per estensione e pattern di esclusione.
    """
    path = Path(folder_path)
    files = []
    for ext in vault_info['include_ext']:
        for f in path.rglob(f'*{ext}'):
            escluso = any(pat in str(f) for pat in vault_info['exclude_patterns'])
            if not escluso:
                files.append(f)
    return sorted(files)


def parse_canvas_file(filepath: Path) -> str:
    """
    Estrae il testo dai nodi di un file .canvas di Obsidian.
    I canvas sono JSON — i nodi 'text' contengono markdown.
    """
    try:
        data = json.loads(filepath.read_text(encoding='utf-8'))
        testi = []
        for node in data.get('nodes', []):
            if node.get('type') == 'text':
                testi.append(node.get('text', '').strip())
            elif node.get('type') == 'file':
                testi.append(f"[File collegato: {node.get('file', '')}]")
        return '\n\n'.join(t for t in testi if t)
    except Exception:
        return ''


def get_files_to_update(folder_path: str,
                        vault_info: dict,
                        last_index_time: float) -> list:
    """
    Aggiornamento incrementale: ritorna solo i file
    modificati dopo last_index_time (timestamp Unix).
    """
    tutti = scan_vault_files(folder_path, vault_info)
    return [f for f in tutti if f.stat().st_mtime > last_index_time]
