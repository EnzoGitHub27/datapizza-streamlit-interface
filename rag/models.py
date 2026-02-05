# rag/models.py
# DeepAiUG v1.4.0 - Modelli dati RAG
# ============================================================================

from pathlib import Path
from typing import Dict, Any
import hashlib


class Document:
    """
    Rappresenta un documento caricato nella Knowledge Base.
    
    Attributes:
        path: Percorso del file sorgente
        content: Contenuto testuale del documento
        metadata: Metadati aggiuntivi (source, filename, extension, etc.)
    """
    
    def __init__(
        self, 
        path: str, 
        content: str, 
        metadata: Dict[str, Any] = None
    ):
        self.path = path
        self.content = content
        self.metadata = metadata or {}
        
        # Auto-populate metadata base
        self.metadata["source"] = path
        self.metadata["filename"] = Path(path).name
        self.metadata["extension"] = Path(path).suffix.lower()
    
    def __repr__(self):
        return f"Document({self.metadata.get('filename', 'unknown')})"
    
    def __len__(self):
        return len(self.content)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte il documento in dizionario."""
        return {
            "path": self.path,
            "content": self.content,
            "metadata": self.metadata,
        }


class Chunk:
    """
    Rappresenta un chunk di testo estratto da un documento.
    
    Usato per la suddivisione dei documenti in parti più piccole
    per l'indicizzazione nel vector store.
    
    Attributes:
        text: Testo del chunk
        document: Documento di origine
        chunk_index: Indice del chunk nel documento
        start_char: Posizione iniziale nel documento originale
        end_char: Posizione finale nel documento originale
        id: ID univoco generato automaticamente
    """
    
    def __init__(
        self, 
        text: str, 
        document: Document, 
        chunk_index: int, 
        start_char: int, 
        end_char: int
    ):
        self.text = text
        self.document = document
        self.chunk_index = chunk_index
        self.start_char = start_char
        self.end_char = end_char
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Genera ID univoco per il chunk basato su contenuto e posizione."""
        content = f"{self.document.path}_{self.chunk_index}_{self.text[:50]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte il chunk in dizionario per storage."""
        return {
            "id": self.id,
            "text": self.text,
            "source": self.document.path,
            "filename": self.document.metadata.get("filename"),
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
        }
    
    def __repr__(self):
        return f"Chunk({self.document.metadata.get('filename')}[{self.chunk_index}])"
    
    def __len__(self):
        return len(self.text)
