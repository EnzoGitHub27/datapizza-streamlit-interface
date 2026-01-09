# rag/adapters/__init__.py
# Datapizza v1.4.1 - Modulo adapters
# ============================================================================

from .base import WikiAdapter
from .local_folder import LocalFolderAdapter
from .mediawiki import MediaWikiAdapter
from .dokuwiki import DokuWikiAdapter

__all__ = [
    "WikiAdapter",
    "LocalFolderAdapter",
    "MediaWikiAdapter",
    "DokuWikiAdapter",
]
