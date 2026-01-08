# rag/adapters/local_folder.py
# Datapizza v1.4.0 - Adapter per cartelle locali
# ============================================================================

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from .base import WikiAdapter
from ..models import Document


class LocalFolderAdapter(WikiAdapter):
    """
    Adapter per cartelle locali con file Markdown, TXT, HTML, PDF.
    
    Supporta:
    - File .md (Markdown)
    - File .txt (Testo puro)
    - File .html/.htm (HTML - richiede beautifulsoup4)
    - File .pdf (PDF - richiede PyPDF2)
    
    Attributes:
        folder_path: Percorso della cartella da scansionare
        extensions: Lista estensioni da includere
        recursive: Se True, cerca anche nelle sottocartelle
    """
    
    name = "Cartella Locale"
    description = "Legge documenti da una cartella locale"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.folder_path = config.get("folder_path", "") if config else ""
        self.extensions = config.get("extensions", [".md", ".txt", ".html"]) if config else [".md", ".txt", ".html"]
        self.recursive = config.get("recursive", True) if config else True
    
    def connect(self) -> bool:
        """
        Verifica che la cartella esista e sia accessibile.
        
        Returns:
            True se la cartella esiste ed è una directory
        """
        if not self.folder_path:
            return False
        path = Path(self.folder_path)
        return path.exists() and path.is_dir()
    
    def load_documents(self) -> List[Document]:
        """
        Carica tutti i documenti dalla cartella.
        
        Scansiona la cartella (ricorsivamente se configurato) e carica
        tutti i file con estensioni supportate.
        
        Returns:
            Lista di Document caricati
        """
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
                print(f"⚠️ Errore caricamento {file_path.name}: {e}")
        
        return self.documents
    
    def _load_single_file(self, file_path: Path) -> Optional[Document]:
        """
        Carica un singolo file.
        
        Args:
            file_path: Path del file da caricare
            
        Returns:
            Document se caricato con successo, None altrimenti
        """
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
                    "modified_at": datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat(),
                }
                return Document(str(file_path), content, metadata)
        except Exception as e:
            print(f"⚠️ Errore lettura {file_path}: {e}")
        
        return None
    
    def _load_text_file(self, file_path: Path) -> str:
        """
        Carica file di testo provando diversi encoding.
        
        Args:
            file_path: Path del file
            
        Returns:
            Contenuto del file come stringa
        """
        encodings = ["utf-8", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return ""
    
    def _load_html_file(self, file_path: Path) -> str:
        """
        Carica e pulisce file HTML.
        
        Rimuove tag script, style, nav, footer, header.
        Richiede beautifulsoup4.
        
        Args:
            file_path: Path del file HTML
            
        Returns:
            Testo estratto dall'HTML
        """
        try:
            from bs4 import BeautifulSoup
            html_content = self._load_text_file(file_path)
            if html_content:
                soup = BeautifulSoup(html_content, "html.parser")
                # Rimuovi elementi non testuali
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                return soup.get_text(separator="\n", strip=True)
        except ImportError:
            print("⚠️ beautifulsoup4 non installato. Installa con: pip install beautifulsoup4")
            return self._load_text_file(file_path)  # Fallback a testo grezzo
        except Exception as e:
            print(f"⚠️ Errore parsing HTML {file_path}: {e}")
        return ""
    
    def _load_pdf_file(self, file_path: Path) -> str:
        """
        Carica file PDF.
        
        Richiede PyPDF2.
        
        Args:
            file_path: Path del file PDF
            
        Returns:
            Testo estratto dal PDF
        """
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
            print("⚠️ PyPDF2 non installato. Installa con: pip install PyPDF2")
        except Exception as e:
            print(f"⚠️ Errore lettura PDF {file_path}: {e}")
        return ""
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Ritorna statistiche della cartella caricata.
        
        Returns:
            Dizionario con statistiche
        """
        stats = super().get_stats()
        stats["folder_path"] = self.folder_path
        stats["extensions"] = self.extensions
        stats["recursive"] = self.recursive
        return stats
