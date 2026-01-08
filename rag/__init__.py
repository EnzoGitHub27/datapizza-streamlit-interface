# rag/__init__.py
# Datapizza v1.4.0 - Modulo RAG (Retrieval-Augmented Generation)
# ============================================================================

from .models import Document, Chunk
from .chunker import TextChunker
from .vector_store import SimpleVectorStore
from .manager import KnowledgeBaseManager
from .adapters import (
    WikiAdapter,
    LocalFolderAdapter,
    MediaWikiAdapter,
)

__all__ = [
    # Models
    "Document",
    "Chunk",
    # Chunker
    "TextChunker",
    # Vector Store
    "SimpleVectorStore",
    # Manager
    "KnowledgeBaseManager",
    # Adapters
    "WikiAdapter",
    "LocalFolderAdapter",
    "MediaWikiAdapter",
]
