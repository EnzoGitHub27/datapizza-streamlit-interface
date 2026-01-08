# rag/manager.py
# Datapizza v1.4.0 - Knowledge Base Manager
# ============================================================================

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Callable

from .models import Document, Chunk
from .adapters import WikiAdapter
from .chunker import TextChunker
from .vector_store import SimpleVectorStore
from config import DEFAULT_TOP_K_RESULTS


class KnowledgeBaseManager:
    """
    Gestisce l'intera knowledge base: adapter, chunking, indicizzazione e ricerca.
    
    Orchestrazione:
    1. Adapter carica documenti dalla sorgente
    2. Chunker divide i documenti in chunks
    3. VectorStore indicizza i chunks
    4. Search trova chunks rilevanti per una query
    
    Attributes:
        adapter: WikiAdapter per caricare documenti
        chunker: TextChunker per dividere documenti
        vector_store: SimpleVectorStore per indicizzazione
        documents: Lista documenti caricati
        chunks: Lista chunks creati
        last_indexed: Timestamp ultima indicizzazione
    """
    
    def __init__(self):
        self.adapter: Optional[WikiAdapter] = None
        self.chunker = TextChunker()
        self.vector_store = SimpleVectorStore()
        self.documents: List[Document] = []
        self.chunks: List[Chunk] = []
        self.last_indexed: Optional[str] = None
    
    def set_adapter(self, adapter: WikiAdapter):
        """
        Imposta l'adapter da usare per caricare documenti.
        
        Args:
            adapter: WikiAdapter configurato
        """
        self.adapter = adapter
    
    def set_chunker(self, chunker: TextChunker):
        """
        Imposta il chunker da usare.
        
        Args:
            chunker: TextChunker configurato
        """
        self.chunker = chunker
    
    def index_documents(
        self, 
        progress_callback: Callable[[str, float], None] = None
    ) -> bool:
        """
        Indicizza tutti i documenti dalla sorgente.
        
        Processo:
        1. Carica documenti via adapter
        2. Divide in chunks via chunker
        3. Indicizza in vector_store
        
        Args:
            progress_callback: Funzione (status_text, progress_fraction) per UI
            
        Returns:
            True se indicizzazione completata con successo
        """
        if not self.adapter:
            print("❌ Nessun adapter configurato")
            return False
        
        # 1. Carica documenti
        if progress_callback:
            progress_callback("📂 Caricamento documenti...", 0.1)
        
        self.documents = self.adapter.load_documents()
        
        if not self.documents:
            print("⚠️ Nessun documento trovato")
            return False
        
        if progress_callback:
            progress_callback(f"📄 Trovati {len(self.documents)} documenti", 0.3)
        
        # 2. Chunking
        if progress_callback:
            progress_callback("✂️ Suddivisione in chunks...", 0.5)
        
        self.chunks = self.chunker.chunk_documents(self.documents)
        
        if progress_callback:
            progress_callback(f"📦 Creati {len(self.chunks)} chunks", 0.7)
        
        # 3. Indicizzazione
        if progress_callback:
            progress_callback("🔍 Indicizzazione in corso...", 0.8)
        
        self.vector_store.clear()
        self.vector_store.add_chunks(self.chunks)
        
        self.last_indexed = datetime.now().isoformat()
        
        if progress_callback:
            progress_callback("✅ Indicizzazione completata!", 1.0)
        
        return True
    
    def search(
        self, 
        query: str, 
        top_k: int = DEFAULT_TOP_K_RESULTS
    ) -> List[Dict[str, Any]]:
        """
        Cerca nella knowledge base.
        
        Args:
            query: Testo della query
            top_k: Numero massimo di risultati
            
        Returns:
            Lista di risultati dal vector store
        """
        return self.vector_store.search(query, top_k)
    
    def get_context_for_prompt(
        self, 
        query: str, 
        top_k: int = DEFAULT_TOP_K_RESULTS
    ) -> Tuple[str, List[str]]:
        """
        Genera contesto da inserire nel prompt LLM.
        
        Cerca i documenti più rilevanti e li formatta per l'iniezione
        nel prompt del modello.
        
        Args:
            query: Domanda dell'utente
            top_k: Numero documenti da includere
            
        Returns:
            Tupla (context_text, list_of_sources)
        """
        results = self.search(query, top_k)
        
        if not results:
            return "", []
        
        context_parts = []
        sources = []
        
        for i, result in enumerate(results, 1):
            text = result.get("text", "")
            metadata = result.get("metadata", {})
            source = metadata.get("filename", metadata.get("source", "Unknown"))
            
            context_parts.append(f"[Documento {i}: {source}]\n{text}")
            if source not in sources:
                sources.append(source)
        
        context_text = "\n\n---\n\n".join(context_parts)
        
        return context_text, sources
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Ritorna statistiche della knowledge base.
        
        Returns:
            Dizionario con document_count, chunk_count, etc.
        """
        vs_stats = self.vector_store.get_stats()
        
        return {
            "document_count": len(self.documents),
            "chunk_count": vs_stats.get("chunk_count", len(self.chunks)),
            "total_chars": sum(len(d.content) for d in self.documents),
            "using_chromadb": vs_stats.get("using_chromadb", False),
            "last_indexed": self.last_indexed,
            "persist_path": vs_stats.get("persist_path"),
        }
    
    def is_indexed(self) -> bool:
        """
        Verifica se la knowledge base è indicizzata.
        
        Returns:
            True se ci sono chunks indicizzati
        """
        stats = self.get_stats()
        return stats.get("chunk_count", 0) > 0
    
    def clear(self):
        """Svuota completamente la knowledge base."""
        self.documents = []
        self.chunks = []
        self.vector_store.clear()
        self.last_indexed = None
