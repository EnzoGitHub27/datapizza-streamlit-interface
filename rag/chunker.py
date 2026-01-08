# rag/chunker.py
# Datapizza v1.4.0 - Text Chunking intelligente
# ============================================================================

import re
from typing import List

from .models import Document, Chunk
from config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


class TextChunker:
    """
    Divide documenti in chunks con strategie intelligenti.
    
    Utilizza separatori gerarchici (titoli, paragrafi, frasi) per dividere
    il testo in modo che ogni chunk sia semanticamente coerente.
    
    Attributes:
        chunk_size: Dimensione target di ogni chunk (in caratteri)
        chunk_overlap: Sovrapposizione tra chunk consecutivi
        separators: Lista di separatori in ordine di priorità
    """
    
    def __init__(
        self, 
        chunk_size: int = DEFAULT_CHUNK_SIZE, 
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    ):
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
        """
        Trova il miglior punto di divisione nel testo.
        
        Cerca il separatore più forte possibile entro la posizione massima,
        evitando chunk troppo piccoli.
        
        Args:
            text: Testo da dividere
            max_pos: Posizione massima per lo split
            
        Returns:
            Indice ottimale per la divisione
        """
        if max_pos >= len(text):
            return len(text)
        
        # Cerca il separatore più forte possibile
        for sep in self.separators:
            # Cerca l'ultima occorrenza del separatore prima di max_pos
            # ma dopo almeno 1/3 del chunk (per evitare chunk troppo piccoli)
            search_start = max(0, self.chunk_size // 3)
            search_text = text[search_start:max_pos]
            last_sep = search_text.rfind(sep)
            
            if last_sep > 0:
                return search_start + last_sep + len(sep)
        
        # Nessun separatore trovato, usa max_pos
        return max_pos
    
    def chunk_document(self, document: Document) -> List[Chunk]:
        """
        Divide un documento in chunks con chunking intelligente.
        
        Args:
            document: Documento da dividere
            
        Returns:
            Lista di Chunk
        """
        text = document.content
        chunks = []
        
        if not text:
            return chunks
        
        # Preprocessa: normalizza whitespace eccessivo
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
        """
        Divide una lista di documenti in chunks.
        
        Args:
            documents: Lista di Document
            
        Returns:
            Lista di tutti i Chunk
        """
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        return all_chunks
    
    def get_stats(self) -> dict:
        """Ritorna statistiche della configurazione chunker."""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "overlap_ratio": self.chunk_overlap / self.chunk_size if self.chunk_size > 0 else 0,
        }
