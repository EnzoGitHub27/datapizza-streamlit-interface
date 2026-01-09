# rag/adapters/dokuwiki.py
# Datapizza v1.4.1 - Adapter per wiki DokuWiki
# ============================================================================

import re
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from .base import WikiAdapter
from ..models import Document
from config import (
    WIKI_CACHE_DIR,
    MEDIAWIKI_DEFAULT_REQUEST_DELAY,
    MEDIAWIKI_DEFAULT_TIMEOUT,
)


class DokuWikiAdapter(WikiAdapter):
    """
    Adapter per DokuWiki - sincronizza pagine wiki in locale.
    
    Funzionalità:
    - Connessione via XML-RPC a DokuWiki
    - Download batch delle pagine
    - Parsing DokuWiki syntax → testo pulito
    - Cache locale per sync incrementali
    - Supporto autenticazione
    
    Richiede: dokuwiki (pip install dokuwiki)
    
    Attributes:
        wiki_url: URL base della wiki
        namespaces: Lista namespace da includere (vuoto = tutti)
        exclude_namespaces: Namespace da escludere
        exclude_patterns: Pattern regex per escludere pagine
        max_pages: Limite pagine (0 = tutte)
    """
    
    name = "DokuWiki"
    description = "Sincronizza pagine da wiki DokuWiki"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        # Configurazione wiki
        self.wiki_url = config.get("url", "") if config else ""
        
        # Autenticazione
        self.requires_auth = config.get("requires_auth", False) if config else False
        self.username = config.get("username", "") if config else ""
        self.password = config.get("password", "") if config else ""
        
        # Filtri contenuto
        self.namespaces = config.get("namespaces", []) if config else []
        self.exclude_namespaces = config.get("exclude_namespaces", []) if config else []
        self.exclude_patterns = config.get("exclude_patterns", []) if config else []
        self.max_pages = config.get("max_pages", 0) if config else 0
        
        # Impostazioni connessione
        self.timeout = config.get("timeout", MEDIAWIKI_DEFAULT_TIMEOUT) if config else MEDIAWIKI_DEFAULT_TIMEOUT
        self.request_delay = config.get("request_delay", MEDIAWIKI_DEFAULT_REQUEST_DELAY) if config else MEDIAWIKI_DEFAULT_REQUEST_DELAY
        self.strip_wiki_markup = config.get("strip_wiki_markup", True) if config else True
        
        # Cache
        self.cache_dir = Path(config.get("cache_dir", str(WIKI_CACHE_DIR))) if config else WIKI_CACHE_DIR
        self.cache_ttl_hours = config.get("cache_ttl_hours", 24) if config else 24
        
        # Stato
        self.wiki = None
        self.last_sync = None
        self.sync_stats = {}
        
        # Verifica dokuwiki
        self.dokuwiki_available = self._check_dokuwiki()
    
    def _check_dokuwiki(self) -> bool:
        """Verifica che dokuwiki sia installato."""
        try:
            import dokuwiki
            return True
        except ImportError:
            return False
    
    def connect(self) -> bool:
        """
        Connette alla wiki DokuWiki via XML-RPC.
        
        Returns:
            True se connesso con successo
        """
        if not self.dokuwiki_available:
            print("❌ dokuwiki non installato. Installa con: pip install dokuwiki")
            return False
        
        if not self.wiki_url:
            print("❌ URL wiki non specificato")
            return False
        
        try:
            import dokuwiki
            
            # Costruisci URL XML-RPC
            xmlrpc_url = self.wiki_url.rstrip("/") + "/lib/exe/xmlrpc.php"
            
            # Connetti (con o senza autenticazione)
            if self.requires_auth and self.username and self.password:
                self.wiki = dokuwiki.DokuWiki(
                    xmlrpc_url,
                    self.username,
                    self.password
                )
            else:
                self.wiki = dokuwiki.DokuWiki(xmlrpc_url)
            
            # Verifica connessione con getVersion
            version = self.wiki.version
            print(f"✅ Connesso a DokuWiki {version}")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore connessione a {self.wiki_url}: {e}")
            return False
    
    def load_documents(self, progress_callback=None) -> List[Document]:
        """
        Carica tutte le pagine dalla wiki DokuWiki.
        
        Args:
            progress_callback: Funzione opzionale (progress_fraction, status_text)
                              per aggiornare la UI durante il caricamento
        
        Returns:
            Lista di Document caricati
        """
        self.documents = []
        
        if not self.connect():
            return self.documents
        
        try:
            pages_to_load = self._get_pages_list()
            
            if not pages_to_load:
                print("⚠️ Nessuna pagina trovata con i filtri specificati")
                return self.documents
            
            total = len(pages_to_load)
            
            for i, page_info in enumerate(pages_to_load):
                try:
                    # Delay tra richieste
                    if i > 0:
                        time.sleep(self.request_delay)
                    
                    doc = self._load_page(page_info)
                    if doc:
                        self.documents.append(doc)
                    
                    # Callback progress
                    if progress_callback:
                        progress = (i + 1) / total
                        status = f"📥 Caricamento: {i+1}/{total} pagine"
                        progress_callback(progress, status)
                    
                except Exception as e:
                    page_id = page_info.get("id", "unknown") if isinstance(page_info, dict) else str(page_info)
                    print(f"⚠️ Errore pagina '{page_id}': {e}")
            
            # Aggiorna statistiche sync
            self.last_sync = datetime.now().isoformat()
            self.sync_stats = {
                "total_pages": total,
                "loaded_pages": len(self.documents),
                "wiki_url": self.wiki_url,
                "timestamp": self.last_sync
            }
            
            # Salva statistiche sync
            self._save_sync_info()
            
            return self.documents
            
        except Exception as e:
            print(f"❌ Errore caricamento pagine: {e}")
            return self.documents
    
    def _get_pages_list(self) -> list:
        """
        Ottiene la lista delle pagine da scaricare.
        
        Applica filtri per namespace e esclusioni.
        
        Returns:
            Lista di dizionari con info pagina
        """
        pages = []
        
        try:
            # Ottieni lista di tutte le pagine
            if self.namespaces:
                # Filtra per namespace specifici
                for ns in self.namespaces:
                    try:
                        ns_pages = self.wiki.pages.list(ns)
                        for page_info in ns_pages:
                            if self._should_include_page(page_info):
                                pages.append(page_info)
                                if self.max_pages and len(pages) >= self.max_pages:
                                    return pages
                    except Exception as e:
                        print(f"⚠️ Namespace '{ns}' non accessibile: {e}")
            else:
                # Tutte le pagine (namespace root)
                try:
                    all_pages = self.wiki.pages.list()
                    for page_info in all_pages:
                        if self._should_include_page(page_info):
                            pages.append(page_info)
                            if self.max_pages and len(pages) >= self.max_pages:
                                return pages
                except Exception as e:
                    print(f"❌ Errore recupero lista pagine: {e}")
            
            return pages
            
        except Exception as e:
            print(f"❌ Errore recupero lista pagine: {e}")
            return []
    
    def _should_include_page(self, page_info) -> bool:
        """
        Verifica se una pagina deve essere inclusa.
        
        Args:
            page_info: Dizionario con info pagina o stringa ID
            
        Returns:
            True se la pagina passa tutti i filtri
        """
        try:
            # Estrai ID pagina
            if isinstance(page_info, dict):
                page_id = page_info.get("id", "")
            else:
                page_id = str(page_info)
            
            if not page_id:
                return False
            
            # Estrai namespace dalla pagina (formato: ns1:ns2:pagename)
            parts = page_id.split(":")
            page_ns = ":".join(parts[:-1]) if len(parts) > 1 else ""
            
            # Escludi per namespace
            for exclude_ns in self.exclude_namespaces:
                if page_ns == exclude_ns or page_ns.startswith(exclude_ns + ":"):
                    return False
            
            # Escludi per pattern regex
            for pattern in self.exclude_patterns:
                try:
                    if re.match(pattern, page_id):
                        return False
                except re.error:
                    # Pattern non valido, ignora
                    pass
            
            return True
            
        except Exception:
            return False
    
    def _load_page(self, page_info) -> Optional[Document]:
        """
        Carica una singola pagina DokuWiki.
        
        Args:
            page_info: Dizionario con info pagina o stringa ID
            
        Returns:
            Document se caricato con successo
        """
        try:
            # Estrai ID pagina
            if isinstance(page_info, dict):
                page_id = page_info.get("id", "")
                page_title = page_info.get("title", page_id)
                page_modified = page_info.get("mtime", None)
            else:
                page_id = str(page_info)
                page_title = page_id
                page_modified = None
            
            if not page_id:
                return None
            
            # Ottieni contenuto pagina
            content = self.wiki.pages.get(page_id)
            
            if not content:
                return None
            
            # Pulisci DokuWiki syntax
            if self.strip_wiki_markup:
                content = self._strip_dokuwiki_markup(content)
            
            if not content.strip():
                return None
            
            # Crea documento
            metadata = {
                "title": page_title,
                "wiki_url": self.wiki_url,
                "page_url": f"{self.wiki_url}/doku.php?id={page_id}",
                "page_id": page_id,
                "namespace": ":".join(page_id.split(":")[:-1]) if ":" in page_id else "",
                "last_modified": page_modified,
            }
            
            # Usa URL come path per unicità
            doc_path = f"dokuwiki://{self.wiki_url}/{page_id}"
            
            return Document(doc_path, content, metadata)
            
        except Exception as e:
            print(f"⚠️ Errore caricamento pagina: {e}")
            return None
    
    def _strip_dokuwiki_markup(self, text: str) -> str:
        """
        Converte DokuWiki syntax in testo pulito.
        
        Rimuove markup DokuWiki e converte formattazione.
        
        Args:
            text: Testo DokuWiki originale
            
        Returns:
            Testo pulito
        """
        if not text:
            return ""
        
        # Rimuovi commenti
        text = re.sub(r'~~NOTOC~~', '', text)
        text = re.sub(r'~~NOCACHE~~', '', text)
        text = re.sub(r'<WRAP[^>]*>.*?</WRAP>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Rimuovi code blocks (preserva contenuto)
        text = re.sub(r'<code[^>]*>(.*?)</code>', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'<file[^>]*>(.*?)</file>', r'\1', text, flags=re.DOTALL)
        
        # Converti titoli DokuWiki in markdown
        # DokuWiki usa ====== per H1 (al contrario di altri wiki)
        text = re.sub(r'^======\s*(.+?)\s*======\s*$', r'# \1', text, flags=re.MULTILINE)
        text = re.sub(r'^=====\s*(.+?)\s*=====\s*$', r'## \1', text, flags=re.MULTILINE)
        text = re.sub(r'^====\s*(.+?)\s*====\s*$', r'### \1', text, flags=re.MULTILINE)
        text = re.sub(r'^===\s*(.+?)\s*===\s*$', r'#### \1', text, flags=re.MULTILINE)
        text = re.sub(r'^==\s*(.+?)\s*==\s*$', r'##### \1', text, flags=re.MULTILINE)
        
        # Rimuovi formattazione bold/italic
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'//(.+?)//', r'\1', text)      # Italic
        text = re.sub(r'__(.+?)__', r'\1', text)      # Underline
        text = re.sub(r"''(.+?)''", r'\1', text)      # Monospace
        
        # Converti link interni [[page|text]] → text
        text = re.sub(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', r'\1', text)
        
        # Converti link esterni {{url|text}} → text
        text = re.sub(r'\{\{(?:[^|}]+\|)?([^}]+)\}\}', r'\1', text)
        
        # Rimuovi immagini {{image}}
        text = re.sub(r'\{\{[^}]+\}\}', '', text)
        
        # Converti liste
        text = re.sub(r'^(\s*)\*\s+', r'\1• ', text, flags=re.MULTILINE)
        text = re.sub(r'^(\s*)-\s+', r'\1• ', text, flags=re.MULTILINE)
        
        # Rimuovi tag HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Rimuovi macro e plugin
        text = re.sub(r'~~[A-Z]+~~', '', text)
        text = re.sub(r'\{\{[^}]+\}\}', '', text)
        
        # Normalizza whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()
    
    def _save_sync_info(self):
        """Salva informazioni dell'ultimo sync su disco."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Crea ID univoco per questa wiki
            wiki_id = hashlib.md5(self.wiki_url.encode()).hexdigest()[:12]
            sync_file = self.cache_dir / f"sync_doku_{wiki_id}.json"
            
            with open(sync_file, "w", encoding="utf-8") as f:
                json.dump(self.sync_stats, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Impossibile salvare info sync: {e}")
    
    def get_last_sync_info(self) -> Optional[Dict[str, Any]]:
        """
        Recupera informazioni dell'ultimo sync.
        
        Returns:
            Dizionario con info sync o None
        """
        try:
            wiki_id = hashlib.md5(self.wiki_url.encode()).hexdigest()[:12]
            sync_file = self.cache_dir / f"sync_doku_{wiki_id}.json"
            
            if sync_file.exists():
                with open(sync_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Ritorna statistiche dell'adapter.
        
        Returns:
            Dizionario con statistiche complete
        """
        stats = super().get_stats()
        stats["wiki_url"] = self.wiki_url
        stats["wiki_type"] = "dokuwiki"
        stats["last_sync"] = self.last_sync
        stats["dokuwiki_available"] = self.dokuwiki_available
        
        sync_info = self.get_last_sync_info()
        if sync_info:
            stats["last_sync_info"] = sync_info
        
        return stats
