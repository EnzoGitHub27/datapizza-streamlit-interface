# rag/adapters/base.py
# DeepAiUG v1.4.0 - Adapter base per sorgenti documenti
# ============================================================================

from abc import ABC, abstractmethod
from typing import Dict, Any, List

from ..models import Document


class WikiAdapter(ABC):
    """
    Classe base astratta per tutti gli adapter di sorgenti documenti.
    
    Definisce l'interfaccia comune che tutti gli adapter devono implementare
    per caricare documenti da diverse sorgenti (cartelle locali, wiki, etc.).
    
    Attributes:
        name: Nome descrittivo dell'adapter
        description: Descrizione dell'adapter
        config: Configurazione specifica dell'adapter
        documents: Lista documenti caricati
    """
    
    name = "Base Adapter"
    description = "Adapter base - non usare direttamente"
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inizializza l'adapter.
        
        Args:
            config: Dizionario con la configurazione specifica
        """
        self.config = config or {}
        self.documents: List[Document] = []
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connette alla sorgente dati.
        
        Returns:
            True se la connessione ha successo, False altrimenti
        """
        raise NotImplementedError
    
    @abstractmethod
    def load_documents(self) -> List[Document]:
        """
        Carica tutti i documenti dalla sorgente.
        
        Returns:
            Lista di Document caricati
        """
        raise NotImplementedError
    
    def get_document_count(self) -> int:
        """
        Ritorna il numero di documenti caricati.
        
        Returns:
            Numero di documenti
        """
        return len(self.documents)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Ritorna statistiche sui documenti caricati.
        
        Returns:
            Dizionario con statistiche (document_count, total_chars, etc.)
        """
        return {
            "document_count": len(self.documents),
            "total_chars": sum(len(d.content) for d in self.documents),
        }
    
    def clear(self):
        """Svuota la lista di documenti caricati."""
        self.documents = []
