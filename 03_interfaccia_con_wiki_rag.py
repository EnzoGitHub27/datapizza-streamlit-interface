# Streamlit UI per LLM con Wiki RAG / Knowledge Base
# Versione 1.3.1 - Wiki RAG (Bug Fix)
# Gilles DeepAiUG - Gennaio 2025
# 
# Novità v1.3.1:
# - 🐛 FIX: Ora mostra tutti i modelli Ollama (non solo quelli con '-' nel nome)
# - 🐛 FIX: Persistenza impostazioni KB nelle conversazioni salvate
# - 🐛 FIX: Ricarica automatica KB quando carichi una conversazione
# - ✨ NEW: Parametri chunking configurabili (dimensione, overlap)
# - ✨ NEW: Chunking intelligente (rispetta titoli, paragrafi, frasi)
# - ✨ NEW: Estensioni file e opzioni salvate con la conversazione
#
# Novità v1.3.0:
# - 📚 Knowledge Base locale con RAG (Retrieval-Augmented Generation)
# - 📁 Supporto cartelle locali (Markdown, TXT, HTML, PDF)
# - 🔍 Indicizzazione documenti con ChromaDB
# - 💬 Chat con contesto dai documenti
# - 📎 Citazione fonti nelle risposte
# - 🔒 Privacy mode (blocco automatico provider cloud)
# - ⚙️ Configurazione knowledge base in sidebar

import os
import subprocess
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import json
import io
import zipfile
import hashlib

# Import datapizza clients
from datapizza.clients import ClientFactory
from datapizza.clients.factory import Provider
from datapizza.clients.openai_like import OpenAILikeClient

# ============================================================================
# COSTANTI
# ============================================================================

DEFAULT_MAX_MESSAGES = 50
DEFAULT_MAX_TOKENS_ESTIMATE = 8000

USER_MESSAGE_COLOR = "#E3F2FD"
ASSISTANT_MESSAGE_COLOR = "#F5F5F5"
USER_MESSAGE_COLOR_DARK = "#1E3A5F"
ASSISTANT_MESSAGE_COLOR_DARK = "#2D2D2D"

CONVERSATIONS_DIR = Path(__file__).parent / "conversations"
KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"

# Formati file supportati per Knowledge Base
SUPPORTED_EXTENSIONS = {
    ".md": "Markdown",
    ".txt": "Testo",
    ".html": "HTML",
    ".htm": "HTML",
    ".pdf": "PDF",
}

# Configurazione chunking
DEFAULT_CHUNK_SIZE = 1000  # caratteri
DEFAULT_CHUNK_OVERLAP = 200  # caratteri

# Configurazione RAG
DEFAULT_TOP_K_RESULTS = 5  # documenti da includere nel contesto

# Export formats (da v1.2.0)
EXPORT_FORMATS = {
    "Markdown": {"ext": ".md", "icon": "📝", "mime": "text/markdown"},
    "JSON": {"ext": ".json", "icon": "📋", "mime": "application/json"},
    "TXT": {"ext": ".txt", "icon": "📄", "mime": "text/plain"},
    "PDF": {"ext": ".pdf", "icon": "📕", "mime": "application/pdf"}
}

CONTENT_OPTIONS = {
    "Conversazione completa": None,
    "Ultimi 10 messaggi": 10,
    "Ultimi 20 messaggi": 20,
    "Ultimi 50 messaggi": 50,
}

# ============================================================================
# CLASSI RAG - DOCUMENT E CHUNK
# ============================================================================

class Document:
    """Rappresenta un documento caricato."""
    def __init__(self, path: str, content: str, metadata: Dict[str, Any] = None):
        self.path = path
        self.content = content
        self.metadata = metadata or {}
        self.metadata["source"] = path
        self.metadata["filename"] = Path(path).name
        self.metadata["extension"] = Path(path).suffix.lower()
    
    def __repr__(self):
        return f"Document({self.metadata.get('filename', 'unknown')})"


class Chunk:
    """Rappresenta un chunk di testo da un documento."""
    def __init__(self, text: str, document: Document, chunk_index: int, start_char: int, end_char: int):
        self.text = text
        self.document = document
        self.chunk_index = chunk_index
        self.start_char = start_char
        self.end_char = end_char
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Genera ID univoco per il chunk."""
        content = f"{self.document.path}_{self.chunk_index}_{self.text[:50]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
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


# ============================================================================
# CLASSI RAG - ADAPTERS
# ============================================================================

class WikiAdapter:
    """Classe base per tutti gli adapter wiki."""
    name = "Base Adapter"
    description = "Adapter base - non usare direttamente"
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.documents: List[Document] = []
    
    def connect(self) -> bool:
        """Connette alla sorgente dati. Ritorna True se successo."""
        raise NotImplementedError
    
    def load_documents(self) -> List[Document]:
        """Carica tutti i documenti dalla sorgente."""
        raise NotImplementedError
    
    def get_document_count(self) -> int:
        """Ritorna il numero di documenti."""
        return len(self.documents)
    
    def get_stats(self) -> Dict[str, Any]:
        """Ritorna statistiche sui documenti."""
        return {
            "document_count": len(self.documents),
            "total_chars": sum(len(d.content) for d in self.documents),
        }


class LocalFolderAdapter(WikiAdapter):
    """Adapter per cartelle locali con file Markdown, TXT, HTML, PDF."""
    name = "Cartella Locale"
    description = "Legge documenti da una cartella locale"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.folder_path = config.get("folder_path", "") if config else ""
        self.extensions = config.get("extensions", [".md", ".txt", ".html"]) if config else [".md", ".txt", ".html"]
        self.recursive = config.get("recursive", True) if config else True
    
    def connect(self) -> bool:
        """Verifica che la cartella esista e sia accessibile."""
        if not self.folder_path:
            return False
        path = Path(self.folder_path)
        return path.exists() and path.is_dir()
    
    def load_documents(self) -> List[Document]:
        """Carica tutti i documenti dalla cartella."""
        self.documents = []
        
        if not self.connect():
            return self.documents
        
        folder = Path(self.folder_path)
        
        # Trova tutti i file con estensioni supportate
        if self.recursive:
            files = []
            for ext in self.extensions:
                files.extend(folder.rglob(f"*{ext}"))
        else:
            files = []
            for ext in self.extensions:
                files.extend(folder.glob(f"*{ext}"))
        
        for file_path in files:
            try:
                doc = self._load_single_file(file_path)
                if doc:
                    self.documents.append(doc)
            except Exception as e:
                st.warning(f"Errore caricamento {file_path.name}: {e}")
        
        return self.documents
    
    def _load_single_file(self, file_path: Path) -> Optional[Document]:
        """Carica un singolo file."""
        ext = file_path.suffix.lower()
        
        try:
            if ext in [".md", ".txt"]:
                content = self._load_text_file(file_path)
            elif ext in [".html", ".htm"]:
                content = self._load_html_file(file_path)
            elif ext == ".pdf":
                content = self._load_pdf_file(file_path)
            else:
                return None
            
            if content:
                metadata = {
                    "file_size": file_path.stat().st_size,
                    "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                }
                return Document(str(file_path), content, metadata)
        except Exception as e:
            st.warning(f"Errore lettura {file_path}: {e}")
        
        return None
    
    def _load_text_file(self, file_path: Path) -> str:
        """Carica file di testo."""
        encodings = ["utf-8", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return ""
    
    def _load_html_file(self, file_path: Path) -> str:
        """Carica e pulisce file HTML."""
        try:
            from bs4 import BeautifulSoup
            html_content = self._load_text_file(file_path)
            if html_content:
                soup = BeautifulSoup(html_content, "html.parser")
                # Rimuovi script e style
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                return soup.get_text(separator="\n", strip=True)
        except ImportError:
            st.warning("Installa beautifulsoup4: pip install beautifulsoup4")
            return self._load_text_file(file_path)  # Fallback
        except Exception as e:
            st.warning(f"Errore parsing HTML {file_path}: {e}")
        return ""
    
    def _load_pdf_file(self, file_path: Path) -> str:
        """Carica file PDF."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(str(file_path))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts)
        except ImportError:
            st.warning("Installa PyPDF2: pip install PyPDF2")
        except Exception as e:
            st.warning(f"Errore lettura PDF {file_path}: {e}")
        return ""


# ============================================================================
# CLASSI RAG - CHUNKING
# ============================================================================

class TextChunker:
    """Divide documenti in chunks con strategie intelligenti."""
    
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, 
                 chunk_overlap: int = DEFAULT_CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Separatori in ordine di priorità (dal più forte al più debole)
        self.separators = [
            "\n## ",      # Titoli Markdown H2
            "\n### ",     # Titoli Markdown H3
            "\n\n\n",     # Tripla newline (sezioni)
            "\n\n",       # Doppia newline (paragrafi)
            "\n",         # Singola newline
            ". ",         # Fine frase con punto
            "! ",         # Fine frase con esclamativo
            "? ",         # Fine frase con interrogativo
            "; ",         # Punto e virgola
            ", ",         # Virgola
            " ",          # Spazio (ultima risorsa)
        ]
    
    def _find_best_split_point(self, text: str, max_pos: int) -> int:
        """Trova il miglior punto di divisione nel testo."""
        if max_pos >= len(text):
            return len(text)
        
        # Cerca il separatore più forte possibile
        for sep in self.separators:
            # Cerca l'ultima occorrenza del separatore prima di max_pos
            # ma dopo almeno metà del chunk (per evitare chunk troppo piccoli)
            search_start = max(0, self.chunk_size // 3)
            search_text = text[search_start:max_pos]
            last_sep = search_text.rfind(sep)
            
            if last_sep > 0:
                return search_start + last_sep + len(sep)
        
        # Nessun separatore trovato, usa max_pos
        return max_pos
    
    def chunk_document(self, document: Document) -> List[Chunk]:
        """Divide un documento in chunks con chunking intelligente."""
        text = document.content
        chunks = []
        
        if not text:
            return chunks
        
        # Preprocessa: normalizza whitespace eccessivo
        import re
        text = re.sub(r'\n{4,}', '\n\n\n', text)  # Max 3 newline consecutive
        text = re.sub(r' {3,}', '  ', text)       # Max 2 spazi consecutivi
        
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calcola la fine ideale del chunk
            ideal_end = start + self.chunk_size
            
            if ideal_end >= len(text):
                # Ultimo chunk: prendi tutto il resto
                chunk_text = text[start:].strip()
                if chunk_text:
                    chunk = Chunk(
                        text=chunk_text,
                        document=document,
                        chunk_index=chunk_index,
                        start_char=start,
                        end_char=len(text)
                    )
                    chunks.append(chunk)
                break
            
            # Trova il miglior punto di split
            end = self._find_best_split_point(text[start:], self.chunk_size)
            end = start + end
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                # Aggiungi contesto: se il chunk inizia a metà frase, cerca l'inizio
                chunk = Chunk(
                    text=chunk_text,
                    document=document,
                    chunk_index=chunk_index,
                    start_char=start,
                    end_char=end
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # Calcola il prossimo start con overlap
            start = max(start + 1, end - self.chunk_overlap)
            
            # Safety check per evitare loop infiniti
            if start >= len(text) or (end == start + self.chunk_size and end < len(text)):
                break
        
        return chunks
    
    def chunk_documents(self, documents: List[Document]) -> List[Chunk]:
        """Divide una lista di documenti in chunks."""
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        return all_chunks


# ============================================================================
# CLASSI RAG - VECTOR STORE (ChromaDB)
# ============================================================================

class SimpleVectorStore:
    """Vector store semplificato - usa ChromaDB se disponibile, altrimenti fallback."""
    
    def __init__(self, persist_path: str = None):
        self.persist_path = persist_path or str(KNOWLEDGE_BASE_DIR / "vectorstore")
        self.chunks: List[Chunk] = []
        self.embeddings: List[List[float]] = []
        self.use_chromadb = False
        self.collection = None
        self._init_store()
    
    def _init_store(self):
        """Inizializza ChromaDB se disponibile."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Crea directory se non esiste
            Path(self.persist_path).mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=self.persist_path)
            self.collection = self.client.get_or_create_collection(
                name="wiki_knowledge_base",
                metadata={"description": "Knowledge Base for Wiki RAG"}
            )
            self.use_chromadb = True
        except ImportError:
            st.warning("⚠️ ChromaDB non installato. Usando store in memoria (dati persi al riavvio). Installa con: pip install chromadb")
            self.use_chromadb = False
        except Exception as e:
            st.warning(f"⚠️ Errore inizializzazione ChromaDB: {e}. Usando store in memoria.")
            self.use_chromadb = False
    
    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]] = None):
        """Aggiunge chunks al vector store."""
        if not chunks:
            return
        
        if self.use_chromadb and self.collection:
            try:
                ids = [chunk.id for chunk in chunks]
                documents = [chunk.text for chunk in chunks]
                metadatas = [chunk.to_dict() for chunk in chunks]
                
                # Se abbiamo embeddings, usiamoli
                if embeddings:
                    self.collection.add(
                        ids=ids,
                        documents=documents,
                        metadatas=metadatas,
                        embeddings=embeddings
                    )
                else:
                    # ChromaDB genererà embeddings automaticamente
                    self.collection.add(
                        ids=ids,
                        documents=documents,
                        metadatas=metadatas
                    )
            except Exception as e:
                st.error(f"Errore aggiunta a ChromaDB: {e}")
        else:
            # Fallback: store in memoria
            self.chunks.extend(chunks)
    
    def search(self, query: str, top_k: int = DEFAULT_TOP_K_RESULTS) -> List[Dict[str, Any]]:
        """Cerca chunks simili alla query."""
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
                st.error(f"Errore ricerca ChromaDB: {e}")
                return []
        else:
            # Fallback: ricerca semplice basata su keyword
            return self._simple_search(query, top_k)
    
    def _simple_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Ricerca semplice senza embeddings (fallback)."""
        query_terms = query.lower().split()
        scored_chunks = []
        
        for chunk in self.chunks:
            score = sum(1 for term in query_terms if term in chunk.text.lower())
            if score > 0:
                scored_chunks.append((chunk, score))
        
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {
                "text": chunk.text,
                "metadata": chunk.to_dict(),
                "distance": 1.0 / (score + 1)
            }
            for chunk, score in scored_chunks[:top_k]
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Ritorna statistiche del vector store."""
        if self.use_chromadb and self.collection:
            try:
                count = self.collection.count()
                return {
                    "chunk_count": count,
                    "using_chromadb": True,
                    "persist_path": self.persist_path
                }
            except:
                pass
        
        return {
            "chunk_count": len(self.chunks),
            "using_chromadb": False,
            "persist_path": None
        }
    
    def clear(self):
        """Svuota il vector store."""
        if self.use_chromadb and self.collection:
            try:
                # Elimina e ricrea collection
                self.client.delete_collection("wiki_knowledge_base")
                self.collection = self.client.get_or_create_collection(
                    name="wiki_knowledge_base",
                    metadata={"description": "Knowledge Base for Wiki RAG"}
                )
            except Exception as e:
                st.error(f"Errore clear ChromaDB: {e}")
        
        self.chunks = []
        self.embeddings = []


# ============================================================================
# CLASSE RAG - KNOWLEDGE BASE MANAGER
# ============================================================================

class KnowledgeBaseManager:
    """Gestisce l'intera knowledge base."""
    
    def __init__(self):
        self.adapter: Optional[WikiAdapter] = None
        self.chunker = TextChunker()
        self.vector_store = SimpleVectorStore()
        self.documents: List[Document] = []
        self.chunks: List[Chunk] = []
        self.last_indexed: Optional[str] = None
    
    def set_adapter(self, adapter: WikiAdapter):
        """Imposta l'adapter da usare."""
        self.adapter = adapter
    
    def index_documents(self) -> bool:
        """Indicizza tutti i documenti."""
        if not self.adapter:
            st.error("Nessun adapter configurato")
            return False
        
        # Carica documenti
        with st.spinner("📂 Caricamento documenti..."):
            self.documents = self.adapter.load_documents()
        
        if not self.documents:
            st.warning("Nessun documento trovato")
            return False
        
        st.info(f"📄 Trovati {len(self.documents)} documenti")
        
        # Chunking
        with st.spinner("✂️ Suddivisione in chunks..."):
            self.chunks = self.chunker.chunk_documents(self.documents)
        
        st.info(f"📦 Creati {len(self.chunks)} chunks")
        
        # Indicizzazione
        with st.spinner("🔍 Indicizzazione in corso..."):
            self.vector_store.clear()
            self.vector_store.add_chunks(self.chunks)
        
        self.last_indexed = datetime.now().isoformat()
        
        st.success(f"✅ Indicizzazione completata!")
        return True
    
    def search(self, query: str, top_k: int = DEFAULT_TOP_K_RESULTS) -> List[Dict[str, Any]]:
        """Cerca nella knowledge base."""
        return self.vector_store.search(query, top_k)
    
    def get_context_for_prompt(self, query: str, top_k: int = DEFAULT_TOP_K_RESULTS) -> Tuple[str, List[str]]:
        """
        Genera contesto da inserire nel prompt.
        Ritorna (context_text, list_of_sources)
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
        """Ritorna statistiche della knowledge base."""
        vs_stats = self.vector_store.get_stats()
        
        return {
            "document_count": len(self.documents),
            "chunk_count": vs_stats.get("chunk_count", len(self.chunks)),
            "total_chars": sum(len(d.content) for d in self.documents),
            "using_chromadb": vs_stats.get("using_chromadb", False),
            "last_indexed": self.last_indexed,
        }
    
    def is_indexed(self) -> bool:
        """Verifica se la knowledge base è indicizzata."""
        stats = self.get_stats()
        return stats.get("chunk_count", 0) > 0
        
# ============================================================================
# FUNZIONI API KEYS (da versioni precedenti)
# ============================================================================

def load_api_key(provider_name: str, env_var_name: str) -> str:
    """Carica API key da env o file secrets."""
    load_dotenv()
    api_key = os.getenv(env_var_name)
    if api_key:
        return api_key
    base_dir = Path(__file__).parent
    key_file = base_dir / "secrets" / f"{provider_name}_key.txt"
    if key_file.exists():
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            pass
    return ""

def save_api_key_to_file(provider_name: str, api_key: str) -> bool:
    """Salva API key in file secrets."""
    try:
        base_dir = Path(__file__).parent
        secrets_dir = base_dir / "secrets"
        secrets_dir.mkdir(exist_ok=True)
        key_file = secrets_dir / f"{provider_name}_key.txt"
        with open(key_file, "w", encoding="utf-8") as f:
            f.write(api_key)
        return True
    except:
        return False

def get_local_ollama_models():
    """Recupera lista modelli Ollama."""
    try:
        proc = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True, timeout=5)
        lines = proc.stdout.splitlines()
        models = []
        for line in lines:
            s = line.strip()
            # Salta righe vuote, header e separatori
            if not s or s.upper().startswith("NAME") or set(s) <= set("- "):
                continue
            parts = s.split()
            if parts:
                models.append(parts[0])
        return models
    except Exception:
        return []

def create_client(connection_type: str, provider: str, api_key: str, 
                 model: str, system_prompt: str, base_url: str, temperature: float):
    """Crea client LLM."""
    if connection_type == "Cloud provider":
        if provider == "OpenAI":
            return ClientFactory.create(provider=Provider.OPENAI, api_key=api_key, model=model, temperature=temperature, system_prompt=system_prompt)
        elif provider == "Anthropic (Claude)":
            return ClientFactory.create(provider=Provider.ANTHROPIC, api_key=api_key, model=model, temperature=temperature, system_prompt=system_prompt)
        elif provider == "Google Gemini":
            return ClientFactory.create(provider=Provider.GOOGLE, api_key=api_key, model=model, temperature=temperature, system_prompt=system_prompt)
        else:
            return OpenAILikeClient(api_key=api_key, model=model, system_prompt=system_prompt, base_url=base_url, temperature=temperature)
    else:
        return OpenAILikeClient(api_key=api_key or "ollama", model=model, system_prompt=system_prompt, base_url=base_url, temperature=temperature)

# ============================================================================
# FUNZIONI PERSISTENZA (da v1.1.1)
# ============================================================================

def ensure_conversations_dir():
    CONVERSATIONS_DIR.mkdir(exist_ok=True)

def get_conversation_filename(conversation_id: str) -> Path:
    return CONVERSATIONS_DIR / f"conv_{conversation_id}.json"

def save_conversation_to_file():
    try:
        ensure_conversations_dir()
        
        # Raccogli impostazioni Knowledge Base
        kb_settings = {
            "use_knowledge_base": st.session_state.get("use_knowledge_base", False),
            "kb_folder_path": st.session_state.get("kb_folder_path", ""),
            "kb_extensions": st.session_state.get("kb_extensions", [".md", ".txt", ".html"]),
            "kb_recursive": st.session_state.get("kb_recursive", True),
            "kb_chunk_size": st.session_state.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
            "kb_chunk_overlap": st.session_state.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP),
            "rag_top_k": st.session_state.get("rag_top_k", DEFAULT_TOP_K_RESULTS),
        }
        
        conversation_data = {
            "conversation_id": st.session_state.get("conversation_id", "unknown"),
            "created_at": st.session_state.get("conversation_created_at", datetime.now().isoformat()),
            "last_updated": datetime.now().isoformat(),
            "model": st.session_state.get("current_model", "unknown"),
            "provider": st.session_state.get("connection_type", "unknown"),
            "messages": st.session_state.get("messages", []),
            "stats": {
                "total_messages": len(st.session_state.get("messages", [])),
                "tokens_estimate": st.session_state.get("total_tokens_estimate", 0)
            },
            "knowledge_base": kb_settings  # NUOVO: salva impostazioni KB
        }
        filename = get_conversation_filename(conversation_data["conversation_id"])
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def load_conversation_from_file(conversation_id: str) -> bool:
    try:
        filename = get_conversation_filename(conversation_id)
        if not filename.exists():
            return False
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        st.session_state["conversation_id"] = data.get("conversation_id")
        st.session_state["conversation_created_at"] = data.get("created_at")
        st.session_state["messages"] = data.get("messages", [])
        st.session_state["total_tokens_estimate"] = data.get("stats", {}).get("tokens_estimate", 0)
        
        # NUOVO: Ripristina impostazioni Knowledge Base
        kb_settings = data.get("knowledge_base", {})
        if kb_settings:
            st.session_state["use_knowledge_base"] = kb_settings.get("use_knowledge_base", False)
            st.session_state["kb_folder_path"] = kb_settings.get("kb_folder_path", "")
            st.session_state["kb_extensions"] = kb_settings.get("kb_extensions", [".md", ".txt", ".html"])
            st.session_state["kb_recursive"] = kb_settings.get("kb_recursive", True)
            st.session_state["kb_chunk_size"] = kb_settings.get("kb_chunk_size", DEFAULT_CHUNK_SIZE)
            st.session_state["kb_chunk_overlap"] = kb_settings.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP)
            st.session_state["rag_top_k"] = kb_settings.get("rag_top_k", DEFAULT_TOP_K_RESULTS)
            st.session_state["kb_needs_reindex"] = True  # Flag per ricaricare KB
        
        return True
    except:
        return False

def list_saved_conversations() -> List[Dict[str, Any]]:
    try:
        ensure_conversations_dir()
        conversations = []
        for file_path in CONVERSATIONS_DIR.glob("conv_*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                conversations.append({
                    "id": data.get("conversation_id"),
                    "created_at": data.get("created_at"),
                    "last_updated": data.get("last_updated"),
                    "model": data.get("model"),
                    "message_count": data.get("stats", {}).get("total_messages", 0),
                })
            except:
                continue
        conversations.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
        return conversations
    except:
        return []

def delete_conversation_file(conversation_id: str) -> bool:
    try:
        filename = get_conversation_filename(conversation_id)
        if filename.exists():
            filename.unlink()
            return True
    except:
        pass
    return False

def get_conversation_preview(conversation_id: str) -> str:
    try:
        filename = get_conversation_filename(conversation_id)
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        messages = data.get("messages", [])[:3]
        lines = []
        for msg in messages:
            role = "👤" if msg["role"] == "user" else "🤖"
            content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
            lines.append(f"{role}: {content}")
        return "\n".join(lines) if lines else "Vuota"
    except:
        return "Errore"

# ============================================================================
# FUNZIONI EXPORT (da v1.2.0)
# ============================================================================

def get_messages_for_export(content_option: str) -> List[Dict[str, Any]]:
    messages = st.session_state.get("messages", [])
    limit = CONTENT_OPTIONS.get(content_option)
    if limit is None:
        return messages
    return messages[-limit:] if len(messages) > limit else messages

def export_to_markdown(messages: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
    lines = ["# Conversazione LLM", "", f"**Data:** {metadata.get('created_at', 'N/A')}", 
             f"**Modello:** {metadata.get('model', 'N/A')}", f"**Messaggi:** {len(messages)}", "", "---", ""]
    for msg in messages:
        role = "👤 Tu" if msg.get("role") == "user" else f"🤖 AI"
        timestamp = msg.get("timestamp", "")[:19].replace("T", " ")
        lines.extend([f"## {role} - {timestamp}", "", msg.get("content", ""), "", "---", ""])
    lines.append(f"*Generato con Datapizza v1.3.1 - {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    return "\n".join(lines)

def export_to_json(messages: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
    return json.dumps({"export_info": {"exported_at": datetime.now().isoformat(), "version": "1.3.0"}, 
                       "conversation": {"id": metadata.get("conversation_id"), "messages": messages}}, indent=2, ensure_ascii=False)

def export_to_txt(messages: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
    lines = ["=" * 60, "CONVERSAZIONE LLM", "=" * 60, f"Data: {metadata.get('created_at', 'N/A')}", 
             f"Modello: {metadata.get('model', 'N/A')}", "=" * 60, ""]
    for msg in messages:
        role = "Tu" if msg.get("role") == "user" else "AI"
        lines.extend([f"[{role}]", msg.get("content", ""), "", "-" * 40, ""])
    return "\n".join(lines)

def export_to_pdf(messages: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bytes:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph("Conversazione LLM", styles['Title']), Spacer(1, 20)]
        for msg in messages:
            role = "Tu" if msg.get("role") == "user" else "AI"
            story.append(Paragraph(f"<b>{role}:</b>", styles['Heading2']))
            story.append(Paragraph(msg.get("content", "").replace("<", "&lt;"), styles['Normal']))
            story.append(Spacer(1, 10))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        return None

# ============================================================================
# FUNZIONI CONVERSAZIONE
# ============================================================================

def initialize_conversation():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "conversation_id" not in st.session_state:
        st.session_state["conversation_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    if "conversation_created_at" not in st.session_state:
        st.session_state["conversation_created_at"] = datetime.now().isoformat()
    if "total_tokens_estimate" not in st.session_state:
        st.session_state["total_tokens_estimate"] = 0
    if "auto_save_enabled" not in st.session_state:
        st.session_state["auto_save_enabled"] = True
    if "kb_manager" not in st.session_state:
        st.session_state["kb_manager"] = KnowledgeBaseManager()
    if "use_knowledge_base" not in st.session_state:
        st.session_state["use_knowledge_base"] = False

def add_message(role: str, content: str, model: str = None, sources: List[str] = None):
    message = {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
    if role == "assistant" and model:
        message["model"] = model
    if sources:
        message["sources"] = sources
    st.session_state["messages"].append(message)
    st.session_state["total_tokens_estimate"] += len(content) // 4
    if st.session_state.get("auto_save_enabled", True):
        save_conversation_to_file()

def get_conversation_history(max_messages: int = None) -> List[Dict[str, str]]:
    messages = st.session_state.get("messages", [])
    if max_messages and len(messages) > max_messages:
        messages = messages[-max_messages:]
    return [{"role": msg["role"], "content": msg["content"]} for msg in messages]

def reset_conversation():
    st.session_state["messages"] = []
    st.session_state["conversation_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state["conversation_created_at"] = datetime.now().isoformat()
    st.session_state["total_tokens_estimate"] = 0

def estimate_tokens_in_conversation() -> int:
    return st.session_state.get("total_tokens_estimate", 0)

def render_chat_message(message: Dict[str, Any], index: int):
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    model_used = message.get("model", "")
    sources = message.get("sources", [])
    
    time_str = ""
    if timestamp:
        try:
            time_str = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
        except:
            pass
    
    if role == "user":
        avatar, label = "👤", "Tu"
        col_config = [3, 7, 0.5]
        bubble_class = "user-bubble"
    else:
        avatar = "🤖"
        label = f"AI{f' ({model_used})' if model_used else ''}"
        col_config = [0.5, 7, 3]
        bubble_class = "assistant-bubble"
    
    cols = st.columns(col_config)
    with cols[1]:
        st.caption(f"{avatar} **{label}** • {time_str}")
        st.markdown(f'<div class="{bubble_class}">', unsafe_allow_html=True)
        st.write(content)
        
        # Mostra fonti se presenti (NUOVO v1.3.0)
        if sources:
            with st.expander(f"📎 Fonti ({len(sources)})"):
                for src in sources:
                    st.caption(f"• {src}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")
        
# ============================================================================
# CONFIGURAZIONE STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="Datapizza → LLM Chat v1.3.1 (Wiki RAG)", 
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_conversation()

# ============================================================================
# STILI CSS
# ============================================================================

st.markdown("""
<style>
.user-bubble {
    background-color: #E3F2FD !important;
    padding: 0.75rem 1rem !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    margin-bottom: 0.5rem !important;
    color: #1a1a1a !important;
}
.assistant-bubble {
    background-color: #F5F5F5 !important;
    padding: 0.75rem 1rem !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    margin-bottom: 0.5rem !important;
    color: #1a1a1a !important;
}
.kb-enabled {
    border-left: 4px solid #4CAF50 !important;
    padding-left: 10px !important;
}
@media (prefers-color-scheme: dark) {
    .user-bubble { background-color: #1E3A5F !important; color: #E8E8E8 !important; }
    .assistant-bubble { background-color: #2D2D2D !important; color: #E8E8E8 !important; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - CONFIGURAZIONE LLM
# ============================================================================

st.sidebar.header("⚙️ Configurazione")

connection_type = st.sidebar.selectbox("Tipo connessione", ["Local (Ollama)", "Remote host", "Cloud provider"], index=0)
st.session_state["connection_type"] = connection_type

# Blocco Cloud se Knowledge Base attiva (PRIVACY)
if st.session_state.get("use_knowledge_base") and connection_type == "Cloud provider":
    st.sidebar.error("🔒 **Cloud bloccato**: Knowledge Base attiva. I tuoi documenti rimangono privati!")
    st.sidebar.info("Disattiva Knowledge Base o usa Local/Remote")
    connection_type = "Local (Ollama)"
    st.session_state["connection_type"] = connection_type

base_url = "http://localhost:11434/v1"
api_key = ""
models_local = []
provider = None
model = ""

if connection_type == "Local (Ollama)":
    st.sidebar.markdown("### 🖥️ Locale")
    base_url = st.sidebar.text_input("Base URL", value=base_url)
    col_r, col_c = st.sidebar.columns([3, 1])
    with col_r:
        if st.button("🔄 Aggiorna", use_container_width=True):
            st.session_state["models_local"] = get_local_ollama_models()
    models_local = st.session_state.get("models_local", get_local_ollama_models())
    if not st.session_state.get("models_local"):
        st.session_state["models_local"] = models_local
    with col_c:
        if models_local:
            st.metric("", len(models_local))
    if models_local:
        prev = st.session_state.get("model_select")
        idx = models_local.index(prev) if prev in models_local else 0
        model = st.sidebar.selectbox("Modello", models_local, index=idx, key="model_select")
    else:
        model = st.sidebar.text_input("Modello", value="llama3.2")

elif connection_type == "Remote host":
    st.sidebar.markdown("### 🌐 Remote")
    hosts_text = st.sidebar.text_area("Host", value="http://192.168.1.10:11434/v1", height=60)
    hosts = [h.strip() for h in hosts_text.splitlines() if h.strip()] or [base_url]
    base_url = st.sidebar.selectbox("Host", hosts)
    api_key = st.sidebar.text_input("API Key", type="password")
    model = st.sidebar.text_input("Modello", value="llama3.2")

else:  # Cloud provider
    st.sidebar.markdown("### ☁️ Cloud")
    provider = st.sidebar.selectbox("Provider", ["OpenAI", "Anthropic (Claude)", "Google Gemini", "Custom"])
    configs = {
        "OpenAI": ("openai", "OPENAI_API_KEY", "gpt-4o-mini", "https://api.openai.com/v1"),
        "Anthropic (Claude)": ("anthropic", "ANTHROPIC_API_KEY", "claude-sonnet-4-20250514", "https://api.anthropic.com"),
        "Google Gemini": ("google", "GOOGLE_API_KEY", "gemini-1.5-pro", "https://generativelanguage.googleapis.com"),
        "Custom": ("custom", "CUSTOM_API_KEY", "", "")
    }
    pk, ev, dm, db = configs.get(provider, configs["Custom"])
    existing_key = load_api_key(pk, ev)
    if existing_key:
        st.sidebar.success("✅ Key trovata")
        api_key = existing_key
    else:
        api_key = st.sidebar.text_input("API Key", type="password")
        if api_key and st.sidebar.button("💾 Salva"):
            save_api_key_to_file(pk, api_key)
            st.rerun()
    model = st.sidebar.text_input("Modello", value=dm)
    base_url = db

st.session_state["current_model"] = model

# Parametri LLM
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Parametri")
system_prompt = st.sidebar.text_area("System Prompt", value="Sei un assistente utile. Rispondi in modo chiaro e preciso.", height=80)
temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
max_messages = st.sidebar.slider("Max messaggi", 10, 100, 50, 10)

# ============================================================================
# SIDEBAR - KNOWLEDGE BASE (NUOVO v1.3.0)
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Knowledge Base")

# Toggle principale
use_kb = st.sidebar.checkbox(
    "🔍 Usa Knowledge Base",
    value=st.session_state.get("use_knowledge_base", False),
    help="Cerca nei documenti prima di rispondere"
)
st.session_state["use_knowledge_base"] = use_kb

if use_kb:
    # Avviso privacy
    if connection_type == "Cloud provider":
        st.sidebar.error("🔒 Cloud provider bloccato per privacy!")
    else:
        st.sidebar.success("🔒 Privacy OK - Dati locali")
    
    # Configurazione sorgente
    st.sidebar.markdown("#### 📁 Sorgente Documenti")
    
    adapter_type = st.sidebar.selectbox(
        "Tipo sorgente",
        ["Cartella Locale"],  # Future: "MediaWiki", "DokuWiki", etc.
        help="Seleziona il tipo di sorgente documenti"
    )
    
    if adapter_type == "Cartella Locale":
        folder_path = st.sidebar.text_input(
            "Percorso cartella",
            value=st.session_state.get("kb_folder_path", ""),
            placeholder="/path/to/documents",
            help="Percorso assoluto alla cartella con i documenti"
        )
        st.session_state["kb_folder_path"] = folder_path
        
        # Selezione estensioni
        st.sidebar.markdown("**Formati file:**")
        col_ext1, col_ext2 = st.sidebar.columns(2)
        
        # Recupera valori salvati o usa default
        saved_ext = st.session_state.get("kb_extensions", [".md", ".txt", ".html"])
        with col_ext1:
            use_md = st.checkbox(".md", value=".md" in saved_ext, key="ext_md")
            use_txt = st.checkbox(".txt", value=".txt" in saved_ext, key="ext_txt")
        with col_ext2:
            use_html = st.checkbox(".html", value=".html" in saved_ext, key="ext_html")
            use_pdf = st.checkbox(".pdf", value=".pdf" in saved_ext, key="ext_pdf")
        
        extensions = []
        if use_md: extensions.append(".md")
        if use_txt: extensions.append(".txt")
        if use_html: extensions.extend([".html", ".htm"])
        if use_pdf: extensions.append(".pdf")
        st.session_state["kb_extensions"] = extensions  # Salva per persistenza
        
        recursive = st.sidebar.checkbox(
            "📂 Includi sottocartelle", 
            value=st.session_state.get("kb_recursive", True),
            key="recursive_check"
        )
        st.session_state["kb_recursive"] = recursive  # Salva per persistenza
        
        # NUOVO: Parametri Chunking configurabili
        with st.sidebar.expander("⚙️ Parametri Chunking", expanded=False):
            st.caption("Controlla come i documenti vengono suddivisi")
            
            chunk_size = st.slider(
                "Dimensione chunk (caratteri)",
                min_value=200,
                max_value=3000,
                value=st.session_state.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
                step=100,
                help="Dimensione massima di ogni chunk. Valori più grandi = più contesto ma meno precisione"
            )
            st.session_state["kb_chunk_size"] = chunk_size
            
            chunk_overlap = st.slider(
                "Overlap (caratteri)",
                min_value=0,
                max_value=500,
                value=st.session_state.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP),
                step=50,
                help="Sovrapposizione tra chunk consecutivi. Aiuta a non perdere contesto ai bordi"
            )
            st.session_state["kb_chunk_overlap"] = chunk_overlap
            
            st.caption(f"📊 Ratio overlap: {chunk_overlap/chunk_size*100:.0f}%")
        
        # Pulsante indicizzazione
        if st.sidebar.button("🔄 Indicizza Documenti", use_container_width=True, type="primary"):
            if folder_path and Path(folder_path).exists():
                kb_manager: KnowledgeBaseManager = st.session_state["kb_manager"]
                
                # Aggiorna parametri chunking
                kb_manager.chunker = TextChunker(
                    chunk_size=st.session_state.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
                    chunk_overlap=st.session_state.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP)
                )
                
                # Configura adapter
                adapter = LocalFolderAdapter({
                    "folder_path": folder_path,
                    "extensions": extensions,
                    "recursive": recursive
                })
                kb_manager.set_adapter(adapter)
                
                # Indicizza
                if kb_manager.index_documents():
                    st.sidebar.success("✅ Indicizzazione completata!")
                else:
                    st.sidebar.error("❌ Errore indicizzazione")
            else:
                st.sidebar.error("❌ Percorso cartella non valido")
    
    # Statistiche Knowledge Base
    kb_manager: KnowledgeBaseManager = st.session_state.get("kb_manager")
    if kb_manager and kb_manager.is_indexed():
        stats = kb_manager.get_stats()
        st.sidebar.markdown("#### 📊 Statistiche")
        
        col_s1, col_s2 = st.sidebar.columns(2)
        col_s1.metric("📄 Documenti", stats.get("document_count", 0))
        col_s2.metric("📦 Chunks", stats.get("chunk_count", 0))
        
        if stats.get("last_indexed"):
            try:
                dt = datetime.fromisoformat(stats["last_indexed"])
                st.sidebar.caption(f"🕐 Ultimo update: {dt.strftime('%d/%m %H:%M')}")
            except:
                pass
        
        if stats.get("using_chromadb"):
            st.sidebar.caption("💾 Storage: ChromaDB (persistente)")
        else:
            st.sidebar.caption("⚠️ Storage: Memoria (temporaneo)")
        
        # Parametri RAG
        st.sidebar.markdown("#### ⚙️ Parametri RAG")
        top_k = st.sidebar.slider("Documenti per query", 1, 10, DEFAULT_TOP_K_RESULTS)
        st.session_state["rag_top_k"] = top_k
    else:
        st.sidebar.info("💡 Configura e indicizza una cartella per iniziare")

# ============================================================================
# SIDEBAR - CONVERSAZIONI SALVATE (da v1.1.1)
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Conversazioni")

auto_save = st.sidebar.checkbox("Auto-save", value=st.session_state.get("auto_save_enabled", True))
st.session_state["auto_save_enabled"] = auto_save

saved_conversations = list_saved_conversations()
if saved_conversations:
    conv_options = [(f"{c['last_updated'][:10]} - {c['model'][:12]} ({c['message_count']})", c["id"]) for c in saved_conversations]
    selected = st.sidebar.selectbox("Carica", [None] + [c[0] for c in conv_options], format_func=lambda x: "-- Seleziona --" if x is None else x)
    if selected:
        sel_id = next((c[1] for c in conv_options if c[0] == selected), None)
        if sel_id:
            col_l, col_d = st.sidebar.columns(2)
            with col_l:
                if st.button("📂 Carica"):
                    if load_conversation_from_file(sel_id):
                        # NUOVO: Ricarica KB se era attiva nella conversazione salvata
                        if st.session_state.get("kb_needs_reindex") and st.session_state.get("use_knowledge_base"):
                            folder_path = st.session_state.get("kb_folder_path", "")
                            if folder_path and Path(folder_path).exists():
                                kb_manager: KnowledgeBaseManager = st.session_state.get("kb_manager")
                                if kb_manager:
                                    # Riconfigura chunker con parametri salvati
                                    kb_manager.chunker = TextChunker(
                                        chunk_size=st.session_state.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
                                        chunk_overlap=st.session_state.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP)
                                    )
                                    # Riconfigura adapter
                                    adapter = LocalFolderAdapter({
                                        "folder_path": folder_path,
                                        "extensions": st.session_state.get("kb_extensions", [".md", ".txt", ".html"]),
                                        "recursive": st.session_state.get("kb_recursive", True)
                                    })
                                    kb_manager.set_adapter(adapter)
                                    # Re-indicizza in background
                                    kb_manager.index_documents()
                            st.session_state["kb_needs_reindex"] = False
                    st.rerun()
            with col_d:
                if st.button("🗑️ Elimina"):
                    delete_conversation_file(sel_id)
                    st.rerun()

# ============================================================================
# MAIN - TITOLO E INFO
# ============================================================================

version = "v1.3.1"
if connection_type == "Cloud provider":
    st.title(f"🍕 Datapizza Chat → {provider} `{version}`")
elif connection_type == "Remote host":
    st.title(f"🍕 Datapizza Chat → Remote `{version}`")
else:
    st.title(f"🍕 Datapizza Chat → Ollama `{version}`")

# Banner Knowledge Base
if st.session_state.get("use_knowledge_base"):
    kb_manager = st.session_state.get("kb_manager")
    if kb_manager and kb_manager.is_indexed():
        stats = kb_manager.get_stats()
        st.success(f"📚 **Knowledge Base ATTIVA** - {stats.get('document_count', 0)} documenti | {stats.get('chunk_count', 0)} chunks")
    else:
        st.warning("📚 Knowledge Base attivata ma non indicizzata. Configura una cartella nella sidebar.")
else:
    st.info("✨ **Novità v1.3.0**: Knowledge Base RAG! Attivala nella sidebar per interrogare i tuoi documenti.")

# Privacy indicator
if connection_type == "Local (Ollama)":
    st.success("💻 **Locale** - Privacy totale")
elif connection_type == "Remote host":
    st.info("🌐 **Remote** - Rete locale")
else:
    st.warning("☁️ **Cloud** - Dati esterni (KB disabilitata)")

# Statistiche
messages = st.session_state.get("messages", [])
c1, c2, c3, c4 = st.columns(4)
c1.metric("📝 Messaggi", len(messages))
c2.metric("👤 Domande", len([m for m in messages if m["role"] == "user"]))
c3.metric("🪙 Token", f"{estimate_tokens_in_conversation():,}")
c4.metric("🆔 ID", st.session_state.get("conversation_id", "N/A")[-8:])

st.markdown("---")

# ============================================================================
# CHAT
# ============================================================================

st.subheader("💬 Conversazione")

if not messages:
    if st.session_state.get("use_knowledge_base"):
        st.info("👋 Knowledge Base attiva! Fai una domanda sui tuoi documenti.")
    else:
        st.info("👋 Inizia una conversazione!")
else:
    for idx, msg in enumerate(messages):
        render_chat_message(msg, idx)

st.markdown("---")

# ============================================================================
# INPUT
# ============================================================================

st.subheader("✍️ Messaggio")

with st.form("msg_form", clear_on_submit=True):
    placeholder = "Chiedi qualcosa sui tuoi documenti..." if st.session_state.get("use_knowledge_base") else "Scrivi..."
    user_input = st.text_area("Messaggio", "", height=100, placeholder=placeholder, label_visibility="collapsed")
    
    col1, col2, _ = st.columns([2, 2, 6])
    with col1:
        submit = st.form_submit_button("🚀 Invia", use_container_width=True, type="primary")
    with col2:
        pass

# Reset
_, col_reset, _ = st.columns([2, 2, 6])
with col_reset:
    if st.button("🔄 Nuova", use_container_width=True):
        reset_conversation()
        st.rerun()

# ============================================================================
# INVIO MESSAGGIO CON RAG
# ============================================================================

if submit and user_input.strip():
    if not model:
        st.error("❌ Seleziona modello!")
    elif connection_type == "Cloud provider" and not api_key:
        st.error("❌ Inserisci API key!")
    elif connection_type == "Cloud provider" and st.session_state.get("use_knowledge_base"):
        st.error("🔒 Cloud bloccato con Knowledge Base attiva!")
    else:
        try:
            # Aggiungi messaggio utente
            add_message("user", user_input.strip())
            
            # Prepara contesto RAG se attivo
            context_text = ""
            sources = []
            
            if st.session_state.get("use_knowledge_base"):
                kb_manager: KnowledgeBaseManager = st.session_state.get("kb_manager")
                if kb_manager and kb_manager.is_indexed():
                    top_k = st.session_state.get("rag_top_k", DEFAULT_TOP_K_RESULTS)
                    with st.spinner("🔍 Ricerca documenti rilevanti..."):
                        context_text, sources = kb_manager.get_context_for_prompt(user_input.strip(), top_k)
                    
                    if context_text:
                        st.info(f"📎 Trovati {len(sources)} documenti rilevanti")
            
            # Crea client
            with st.spinner("🔧 Connessione..."):
                client = create_client(connection_type, provider, api_key, model, system_prompt, base_url, temperature)
            
            # Prepara prompt
            history = get_conversation_history(max_messages)
            
            # Costruisci prompt con contesto RAG
            if context_text:
                # System prompt arricchito con contesto
                rag_system = f"""{system_prompt}

IMPORTANTE: Usa le seguenti informazioni dalla Knowledge Base per rispondere. 
Se la risposta non è presente nei documenti, dillo chiaramente.
Cita sempre le fonti quando usi informazioni dai documenti.

--- DOCUMENTI RILEVANTI ---
{context_text}
--- FINE DOCUMENTI ---"""
                
                full_prompt = f"{rag_system}\n\nUtente: {user_input.strip()}\n\nAssistente:"
            else:
                # Prompt normale con cronologia
                context = ""
                for msg in history[:-1]:
                    role_label = "Utente" if msg["role"] == "user" else "AI"
                    context += f"{role_label}: {msg['content']}\n\n"
                full_prompt = f"{context}Utente: {user_input.strip()}\n\nAI:" if context else user_input.strip()
            
            # Invoca LLM
            with st.spinner(f"🤖 {model} sta pensando..."):
                response = client.invoke(full_prompt)
                response_text = getattr(response, "text", str(response))
            
            # Aggiungi risposta con fonti
            add_message("assistant", response_text, model=model, sources=sources if sources else None)
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Errore: {e}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
c1, c2, _ = st.columns([2, 8, 2])
c1.caption("🍕 Datapizza AI")
c2.caption("v1.3.1 - Wiki RAG / Knowledge Base | Gilles DeepAiUG © 2025")

if connection_type == "Cloud provider":
    st.markdown("""<style>.stApp { border-top: 4px solid #ff6b6b !important; }</style>""", unsafe_allow_html=True)
elif st.session_state.get("use_knowledge_base"):
    st.markdown("""<style>.stApp { border-top: 4px solid #4CAF50 !important; }</style>""", unsafe_allow_html=True)