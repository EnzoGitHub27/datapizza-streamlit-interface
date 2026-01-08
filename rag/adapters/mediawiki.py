# rag/adapters/mediawiki.py
# Datapizza v1.4.0 - Adapter per wiki MediaWiki
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
    MEDIAWIKI_DEFAULT_USER_AGENT,
    MEDIAWIKI_DEFAULT_REQUEST_DELAY,
    MEDIAWIKI_DEFAULT_BATCH_SIZE,
    MEDIAWIKI_DEFAULT_TIMEOUT,
)


class MediaWikiAdapter(WikiAdapter):
    """
    Adapter per MediaWiki - sincronizza pagine wiki in locale.
    
    Funzionalità:
    - Connessione via mwclient a qualsiasi wiki MediaWiki
    - Download batch delle pagine
    - Parsing wikitext → testo pulito
    - Cache locale per sync incrementali
    - Supporto autenticazione
    
    Richiede: mwclient (pip install mwclient)
    
    Attributes:
        wiki_url: URL base della wiki
        api_path: Percorso endpoint API (default: /w/api.php)
        namespaces: Lista namespace da includere
        categories: Categorie da cui estrarre pagine
        exclude_categories: Categorie da escludere
        exclude_pages: Pagine da escludere
        max_pages: Limite pagine (0 = tutte)
    """
    
    name = "MediaWiki"
    description = "Sincronizza pagine da wiki MediaWiki"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        # Configurazione wiki
        self.wiki_url = config.get("url", "") if config else ""
        self.api_path = config.get("api_path", "/w/api.php") if config else "/w/api.php"
        
        # Autenticazione
        self.requires_auth = config.get("requires_auth", False) if config else False
        self.username = config.get("username", "") if config else ""
        self.password = config.get("password", "") if config else ""
        
        # Filtri contenuto
        self.namespaces = config.get("namespaces", [0]) if config else [0]
        self.categories = config.get("categories", []) if config else []
        self.exclude_categories = config.get("exclude_categories", []) if config else []
        self.exclude_pages = config.get("exclude_pages", []) if config else []
        self.max_pages = config.get("max_pages", 0) if config else 0
        self.include_redirects = config.get("include_redirects", False) if config else False
        
        # Impostazioni connessione
        self.timeout = config.get("timeout", MEDIAWIKI_DEFAULT_TIMEOUT) if config else MEDIAWIKI_DEFAULT_TIMEOUT
        self.user_agent = config.get("user_agent", MEDIAWIKI_DEFAULT_USER_AGENT) if config else MEDIAWIKI_DEFAULT_USER_AGENT
        self.request_delay = config.get("request_delay", MEDIAWIKI_DEFAULT_REQUEST_DELAY) if config else MEDIAWIKI_DEFAULT_REQUEST_DELAY
        self.batch_size = config.get("batch_size", MEDIAWIKI_DEFAULT_BATCH_SIZE) if config else MEDIAWIKI_DEFAULT_BATCH_SIZE
        self.strip_wiki_markup = config.get("strip_wiki_markup", True) if config else True
        
        # Cache
        self.cache_dir = Path(config.get("cache_dir", str(WIKI_CACHE_DIR))) if config else WIKI_CACHE_DIR
        self.cache_ttl_hours = config.get("cache_ttl_hours", 24) if config else 24
        
        # Stato
        self.site = None
        self.last_sync = None
        self.sync_stats = {}
        
        # Verifica mwclient
        self.mwclient_available = self._check_mwclient()
    
    def _check_mwclient(self) -> bool:
        """Verifica che mwclient sia installato."""
        try:
            import mwclient
            return True
        except ImportError:
            return False
    
    def connect(self) -> bool:
        """
        Connette alla wiki MediaWiki.
        
        Returns:
            True se connesso con successo
        """
        if not self.mwclient_available:
            print("❌ mwclient non installato. Installa con: pip install mwclient")
            return False
        
        if not self.wiki_url:
            print("❌ URL wiki non specificato")
            return False
        
        try:
            import mwclient
            from urllib.parse import urlparse
            
            # Estrai host e path dall'URL
            parsed = urlparse(self.wiki_url)
            host = parsed.netloc
            scheme = parsed.scheme or "https"
            path = self.api_path.replace("/api.php", "/").replace("/w/api.php", "/w/")
            
            # Connetti
            self.site = mwclient.Site(
                host,
                path=path,
                scheme=scheme,
                clients_useragent=self.user_agent
            )
            
            # Autenticazione se richiesta
            if self.requires_auth and self.username and self.password:
                self.site.login(self.username, self.password)
            
            return True
            
        except Exception as e:
            print(f"❌ Errore connessione a {self.wiki_url}: {e}")
            return False
    
    def load_documents(self, progress_callback=None) -> List[Document]:
        """
        Carica tutte le pagine dalla wiki.
        
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
            
            for i, page in enumerate(pages_to_load):
                try:
                    # Delay tra richieste
                    if i > 0:
                        time.sleep(self.request_delay)
                    
                    doc = self._load_page(page)
                    if doc:
                        self.documents.append(doc)
                    
                    # Callback progress
                    if progress_callback:
                        progress = (i + 1) / total
                        status = f"📥 Caricamento: {i+1}/{total} pagine"
                        progress_callback(progress, status)
                    
                except Exception as e:
                    print(f"⚠️ Errore pagina '{page.name}': {e}")
            
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
        
        Applica filtri per namespace, categorie e esclusioni.
        
        Returns:
            Lista di oggetti pagina mwclient
        """
        pages = []
        
        try:
            if self.categories:
                # Filtra per categorie specifiche
                for cat_name in self.categories:
                    try:
                        category = self.site.categories[cat_name]
                        for page in category:
                            if self._should_include_page(page):
                                pages.append(page)
                                if self.max_pages and len(pages) >= self.max_pages:
                                    return pages
                    except Exception as e:
                        print(f"⚠️ Categoria '{cat_name}' non trovata: {e}")
            else:
                # Tutte le pagine nei namespace specificati
                for ns in self.namespaces:
                    for page in self.site.allpages(namespace=ns):
                        if self._should_include_page(page):
                            pages.append(page)
                            if self.max_pages and len(pages) >= self.max_pages:
                                return pages
            
            return pages
            
        except Exception as e:
            print(f"❌ Errore recupero lista pagine: {e}")
            return []
    
    def _should_include_page(self, page) -> bool:
        """
        Verifica se una pagina deve essere inclusa.
        
        Args:
            page: Oggetto pagina mwclient
            
        Returns:
            True se la pagina passa tutti i filtri
        """
        try:
            # Escludi redirect
            if not self.include_redirects and page.redirect:
                return False
            
            # Escludi pagine per titolo esatto
            if page.name in self.exclude_pages:
                return False
            
            # Pattern matching per esclusioni (supporta wildcard *)
            for pattern in self.exclude_pages:
                if "*" in pattern:
                    regex = pattern.replace("*", ".*")
                    if re.match(regex, page.name):
                        return False
            
            # Escludi per categoria
            if self.exclude_categories:
                try:
                    page_cats = [
                        cat.name.replace("Category:", "").replace("Categoria:", "") 
                        for cat in page.categories()
                    ]
                    if any(ec in page_cats for ec in self.exclude_categories):
                        return False
                except:
                    pass
            
            return True
            
        except Exception:
            return False
    
    def _load_page(self, page) -> Optional[Document]:
        """
        Carica una singola pagina wiki.
        
        Args:
            page: Oggetto pagina mwclient
            
        Returns:
            Document se caricato con successo
        """
        try:
            # Ottieni contenuto
            content = page.text()
            
            if not content:
                return None
            
            # Pulisci wikitext
            if self.strip_wiki_markup:
                content = self._strip_wikitext(content)
            
            if not content.strip():
                return None
            
            # Crea documento
            metadata = {
                "title": page.name,
                "wiki_url": self.wiki_url,
                "page_url": f"{self.wiki_url}/wiki/{page.name.replace(' ', '_')}",
                "namespace": page.namespace,
                "last_modified": str(page.touched) if hasattr(page, 'touched') else None,
            }
            
            # Usa URL come path per unicità
            doc_path = f"mediawiki://{self.wiki_url}/wiki/{page.name}"
            
            return Document(doc_path, content, metadata)
            
        except Exception as e:
            print(f"⚠️ Errore caricamento pagina: {e}")
            return None
    
    def _strip_wikitext(self, text: str) -> str:
        """
        Converte wikitext in testo pulito.
        
        Rimuove markup wiki, template, riferimenti e converte
        la formattazione in equivalenti leggibili.
        
        Args:
            text: Wikitext originale
            
        Returns:
            Testo pulito
        """
        if not text:
            return ""
        
        # Rimuovi commenti HTML
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # Rimuovi tag nowiki
        text = re.sub(r'<nowiki>.*?</nowiki>', '', text, flags=re.DOTALL)
        
        # Rimuovi template semplici ({{ ... }})
        # Iterativo per template annidati
        for _ in range(5):
            prev = text
            text = re.sub(r'\{\{[^{}]*\}\}', '', text)
            if prev == text:
                break
        
        # Rimuovi tag ref
        text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
        text = re.sub(r'<ref[^>]*/>', '', text)
        
        # Converti wikilink [[link|testo]] → testo (o link se no testo)
        text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
        
        # Converti link esterni [url testo] → testo
        text = re.sub(r'\[https?://[^\s\]]+\s+([^\]]+)\]', r'\1', text)
        text = re.sub(r'\[https?://[^\s\]]+\]', '', text)
        
        # Rimuovi bold/italic wiki
        text = re.sub(r"'{2,5}", '', text)
        
        # Converti titoli wiki in markdown
        text = re.sub(r'^======\s*(.+?)\s*======', r'###### \1', text, flags=re.MULTILINE)
        text = re.sub(r'^=====\s*(.+?)\s*=====', r'##### \1', text, flags=re.MULTILINE)
        text = re.sub(r'^====\s*(.+?)\s*====', r'#### \1', text, flags=re.MULTILINE)
        text = re.sub(r'^===\s*(.+?)\s*===', r'### \1', text, flags=re.MULTILINE)
        text = re.sub(r'^==\s*(.+?)\s*==', r'## \1', text, flags=re.MULTILINE)
        text = re.sub(r'^=\s*(.+?)\s*=', r'# \1', text, flags=re.MULTILINE)
        
        # Rimuovi liste con * e # (converti in testo)
        text = re.sub(r'^[*#]+\s*', '• ', text, flags=re.MULTILINE)
        
        # Rimuovi tag HTML comuni
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</?[a-z][^>]*>', '', text, flags=re.IGNORECASE)
        
        # Rimuovi categorie e interwiki
        text = re.sub(r'\[\[(?:Category|Categoria):[^\]]+\]\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[[a-z]{2,3}:[^\]]+\]\]', '', text)
        
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
            sync_file = self.cache_dir / f"sync_{wiki_id}.json"
            
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
            sync_file = self.cache_dir / f"sync_{wiki_id}.json"
            
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
        stats["last_sync"] = self.last_sync
        stats["mwclient_available"] = self.mwclient_available
        
        sync_info = self.get_last_sync_info()
        if sync_info:
            stats["last_sync_info"] = sync_info
        
        return stats
