# rag/adapters/__init__.py
# Datapizza v1.4.0 - Modulo adapters
# ============================================================================

from .base import WikiAdapter
from .local_folder import LocalFolderAdapter
from .mediawiki import MediaWikiAdapter

__all__ = [
    "WikiAdapter",
    "LocalFolderAdapter",
    "MediaWikiAdapter",
]
