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


def is_excluded(file_path, root, patterns) -> bool:
    """
    v1.16.1 — True se il file sta sotto una delle cartelle escluse.

    Il pattern («.obsidian», «templates», «logseq/bak») si confronta con le
    cartelle del percorso RELATIVO al vault, pezzo per pezzo: «templates»
    toglie vault/templates/ e vault/progetti/templates/, ma non un vault che
    sta dentro una cartella chiamata «templates», né «miei_templates/».
    """
    try:
        parts = Path(file_path).relative_to(root).parts
    except ValueError:
        parts = Path(file_path).parts
    for pat in patterns or []:
        pat_parts = tuple(p for p in str(pat).replace("\\", "/").split("/") if p)
        n = len(pat_parts)
        if not n:
            continue
        for i in range(len(parts) - n + 1):
            if tuple(parts[i:i + n]) == pat_parts:
                return True
    return False


def exclusion_patterns(folder_path: str, configured=None) -> list:
    """
    v1.16.1 — Le esclusioni che valgono per una cartella: quelle del tipo di
    vault riconosciuto (VAULT_TYPES) più quelle della configurazione.
    Così valgono anche quando chi chiama non le passa («Percorso cartella»,
    ricarica di una conversazione con KB).
    """
    patterns = list(detect_vault_type(folder_path).get('exclude_patterns', []))
    for pat in configured or []:
        if pat not in patterns:
            patterns.append(pat)
    return patterns


def list_files(folder_path: str, extensions, recursive: bool = True, patterns=None) -> list:
    """
    v1.16.1 — I file da indicizzare, in un posto solo: lo usano il conteggio
    del pannello, la stima del tempo e LocalFolderAdapter.
    """
    root = Path(folder_path)
    glob_fn = root.rglob if recursive else root.glob
    seen, files = set(), []
    for ext in extensions:
        for f in glob_fn(f'*{ext}'):
            if f in seen or not f.is_file() or is_excluded(f, root, patterns):
                continue
            seen.add(f)
            files.append(f)
    return sorted(files)


def scan_vault_files(folder_path: str, vault_info: dict) -> list:
    """
    Restituisce la lista dei Path da indicizzare,
    filtrata per estensione e pattern di esclusione.
    """
    return list_files(
        folder_path,
        vault_info['include_ext'],
        recursive=True,
        patterns=exclusion_patterns(folder_path, vault_info.get('exclude_patterns')),
    )


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
