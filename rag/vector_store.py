# rag/vector_store.py
# DeepAiUG v1.15.0 - Vector Store per RAG (embedding multilingua)
# ============================================================================

import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from .models import Chunk
from .embeddings import (
    get_embedding_function,
    get_embeddings_helper,
    get_active_model_tag,
)
from config import KNOWLEDGE_BASE_DIR, DEFAULT_TOP_K_RESULTS

CHROMA_BATCH_SIZE = 500
COLLECTION_NAME = "wiki_knowledge_base"


class SimpleVectorStore:
    """
    Vector store semplificato con ChromaDB e fallback in memoria.
    
    Usa ChromaDB se disponibile per persistenza e ricerca semantica,
    altrimenti fallback a ricerca keyword-based in memoria.
    
    Attributes:
        persist_path: Percorso per persistenza ChromaDB
        use_chromadb: Se True, usa ChromaDB
        collection: Collezione ChromaDB
        chunks: Lista chunks (fallback in memoria)
    """
    
    def __init__(self, persist_path: str = None):
        """
        Inizializza il vector store.
        
        Args:
            persist_path: Percorso per persistenza (default: knowledge_base/vectorstore)
        """
        self.persist_path = persist_path or str(KNOWLEDGE_BASE_DIR / "vectorstore")
        self.chunks: List[Chunk] = []
        self.embeddings: List[List[float]] = []
        self.use_chromadb = False
        self.collection = None
        self.client = None
        self._init_store()
    
    def _init_store(self):
        """
        Inizializza ChromaDB se disponibile.

        v1.15.0 — usa embedding_function multilingua (e5-small) e gestisce
        la migrazione automatica delle collection costruite con un modello
        di embedding diverso (ricreazione → re-indicizzazione richiesta).
        """
        try:
            import chromadb

            # Crea directory se non esiste
            Path(self.persist_path).mkdir(parents=True, exist_ok=True)

            self.client = chromadb.PersistentClient(path=self.persist_path)

            embedding_fn = get_embedding_function()  # None se st non installato
            active_tag = get_active_model_tag()

            # Migrazione: se la collection esistente è stata costruita con un
            # modello diverso (o nessuno tracciato = collection legacy
            # pre-v1.15.0, presumibilmente MiniLM-L6 inglese), ricreala —
            # i vettori sarebbero in spazi vettoriali diversi e il retrieval
            # restituirebbe risultati casuali.
            try:
                existing = self.client.get_collection(name=COLLECTION_NAME)
                stored_tag = (existing.metadata or {}).get("embedding_model")
                if stored_tag != active_tag:
                    legacy_label = stored_tag or "<legacy/sconosciuto>"
                    print(
                        f"⚠️ Embedding model cambiato ({legacy_label} → {active_tag}). "
                        f"Reset collection '{COLLECTION_NAME}' — re-indicizzazione richiesta."
                    )
                    self.client.delete_collection(COLLECTION_NAME)
            except Exception:
                # Collection non esistente: ok, verrà creata sotto
                pass

            collection_kwargs = {
                "name": COLLECTION_NAME,
                "metadata": {
                    "description": "Knowledge Base for Wiki RAG",
                    "embedding_model": active_tag,
                },
            }
            if embedding_fn is not None:
                collection_kwargs["embedding_function"] = embedding_fn

            self.collection = self.client.get_or_create_collection(**collection_kwargs)
            self.use_chromadb = True

        except ImportError:
            print("⚠️ ChromaDB non installato. Usando store in memoria. "
                  "Installa con: pip install chromadb")
            self.use_chromadb = False

        except Exception as e:
            print(f"⚠️ Errore inizializzazione ChromaDB: {e}. "
                  "Usando store in memoria.")
            self.use_chromadb = False
    
    def add_chunks(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]] = None,
        progress_callback: Callable = None
    ):
        """
        Aggiunge chunks al vector store con batching e progress callback.

        Args:
            chunks: Lista di Chunk da aggiungere
            embeddings: Embeddings pre-calcolati (opzionale)
            progress_callback: Callback(status: str, progress: float) per aggiornamenti
        """
        if not chunks:
            return

        if self.use_chromadb and self.collection:
            try:
                total = len(chunks)
                n_batches = math.ceil(total / CHROMA_BATCH_SIZE)
                helper = get_embeddings_helper()  # None se st non disponibile

                for b in range(n_batches):
                    start = b * CHROMA_BATCH_SIZE
                    end = min(start + CHROMA_BATCH_SIZE, total)
                    batch = chunks[start:end]

                    ids = [chunk.id for chunk in batch]
                    documents = [chunk.text for chunk in batch]
                    metadatas = [chunk.to_dict() for chunk in batch]

                    # Determina gli embedding del batch:
                    # 1. Espliciti (passati dal chiamante) → usa quelli
                    # 2. Helper multilingua disponibile → pre-computa con prefix "passage:"
                    # 3. Altrimenti → ChromaDB userà la sua embedding_function
                    #    di default (no prefix, qualità inferiore su IT)
                    if embeddings:
                        batch_emb = embeddings[start:end]
                    elif helper is not None:
                        batch_emb = helper.encode_passages(documents)
                    else:
                        batch_emb = None

                    add_kwargs = {
                        "ids": ids,
                        "documents": documents,
                        "metadatas": metadatas,
                    }
                    if batch_emb is not None:
                        add_kwargs["embeddings"] = batch_emb

                    self.collection.add(**add_kwargs)

                    if progress_callback:
                        progress_callback(
                            f"ChromaDB: batch {b + 1}/{n_batches} ({end}/{total} chunks)",
                            end / total
                        )

            except Exception as e:
                print(f"❌ Errore aggiunta a ChromaDB: {e}")
        else:
            # Fallback: store in memoria
            self.chunks.extend(chunks)
    
    def search(
        self, 
        query: str, 
        top_k: int = DEFAULT_TOP_K_RESULTS
    ) -> List[Dict[str, Any]]:
        """
        Cerca chunks simili alla query.
        
        Args:
            query: Testo della query
            top_k: Numero massimo di risultati
            
        Returns:
            Lista di risultati con text, metadata, distance
        """
        if self.use_chromadb and self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"]
                )
                
                search_results = []
                if results and results["documents"] and results["documents"][0]:
                    for i, doc in enumerate(results["documents"][0]):
                        search_results.append({
                            "text": doc,
                            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                            "distance": results["distances"][0][i] if results["distances"] else 0,
                        })
                return search_results
                
            except Exception as e:
                print(f"❌ Errore ricerca ChromaDB: {e}")
                return []
        else:
            # Fallback: ricerca semplice basata su keyword
            return self._simple_search(query, top_k)
    
    def _simple_search(
        self, 
        query: str, 
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Ricerca semplice senza embeddings (fallback).
        
        Usa matching keyword-based: conta le occorrenze dei termini
        della query in ogni chunk.
        
        Args:
            query: Testo della query
            top_k: Numero massimo di risultati
            
        Returns:
            Lista di risultati ordinati per rilevanza
        """
        query_terms = query.lower().split()
        scored_chunks = []
        
        for chunk in self.chunks:
            # Conta occorrenze dei termini
            score = sum(1 for term in query_terms if term in chunk.text.lower())
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # Ordina per score decrescente
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {
                "text": chunk.text,
                "metadata": chunk.to_dict(),
                "distance": 1.0 / (score + 1)  # Converti score in "distanza"
            }
            for chunk, score in scored_chunks[:top_k]
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Ritorna statistiche del vector store.
        
        Returns:
            Dizionario con chunk_count, using_chromadb, persist_path
        """
        if self.use_chromadb and self.collection:
            try:
                count = self.collection.count()
                stored_meta = self.collection.metadata or {}
                return {
                    "chunk_count": count,
                    "using_chromadb": True,
                    "persist_path": self.persist_path,
                    "embedding_model": stored_meta.get("embedding_model"),
                }
            except:
                pass

        return {
            "chunk_count": len(self.chunks),
            "using_chromadb": False,
            "persist_path": None,
            "embedding_model": None,
        }
    
    def clear(self):
        """Svuota il vector store, preservando embedding_function e metadata."""
        if self.use_chromadb and self.collection:
            try:
                self.client.delete_collection(COLLECTION_NAME)

                embedding_fn = get_embedding_function()
                active_tag = get_active_model_tag()

                collection_kwargs = {
                    "name": COLLECTION_NAME,
                    "metadata": {
                        "description": "Knowledge Base for Wiki RAG",
                        "embedding_model": active_tag,
                    },
                }
                if embedding_fn is not None:
                    collection_kwargs["embedding_function"] = embedding_fn

                self.collection = self.client.get_or_create_collection(**collection_kwargs)
            except Exception as e:
                print(f"❌ Errore clear ChromaDB: {e}")

        self.chunks = []
        self.embeddings = []
    
    def is_empty(self) -> bool:
        """Verifica se il vector store è vuoto."""
        stats = self.get_stats()
        return stats.get("chunk_count", 0) == 0
