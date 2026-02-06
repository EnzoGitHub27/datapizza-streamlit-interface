# ui/socratic/history.py
# DeepAiUG v1.9.0 - Storia Esplorazioni Socratiche
# ============================================================================
# Traccia le esplorazioni socratiche dell'utente per analisi e riflessione.
# Storage: st.session_state (privacy-first, nessun dato esce dal sistema)
# ============================================================================

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

import streamlit as st

# Chiave per lo storage in session_state
HISTORY_KEY = "socratic_history"

# Tipi di bottone socratico supportati
SocraticButtonType = Literal[
    "alternatives",
    "assumptions",
    "limits",
    "confute",
    "reflect"
]


@dataclass
class SocraticExploration:
    """
    Rappresenta una singola esplorazione socratica.

    Cattura il contesto completo: domanda utente, risposta AI,
    e il risultato dell'analisi socratica.
    """
    timestamp: datetime
    button_type: SocraticButtonType
    original_question: str
    ai_response_snippet: str  # Primi 200 caratteri della risposta AI
    socratic_result: str
    session_id: str
    msg_index: int = -1  # Indice del messaggio nella chat (-1 se sconosciuto)

    def to_dict(self) -> dict:
        """Serializza l'esplorazione in un dict JSON-compatibile."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "button_type": self.button_type,
            "original_question": self.original_question,
            "ai_response_snippet": self.ai_response_snippet,
            "socratic_result": self.socratic_result,
            "session_id": self.session_id,
            "msg_index": self.msg_index,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SocraticExploration":
        """
        Crea un'esplorazione da un dict deserializzato.

        Args:
            data: Dict con i campi dell'esplorazione (da JSON)
        """
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            button_type=data["button_type"],
            original_question=data.get("original_question", ""),
            ai_response_snippet=data.get("ai_response_snippet", ""),
            socratic_result=data.get("socratic_result", ""),
            session_id=data.get("session_id", ""),
            msg_index=data.get("msg_index", -1),
        )


class SocraticHistory:
    """
    Gestisce la storia delle esplorazioni socratiche della sessione.

    Tutti i dati sono memorizzati in st.session_state per garantire
    privacy (nessun dato persistente su disco o cloud).
    """

    @staticmethod
    def _ensure_history_exists() -> None:
        """Inizializza la lista history se non esiste."""
        if HISTORY_KEY not in st.session_state:
            st.session_state[HISTORY_KEY] = []

    @staticmethod
    def add_exploration(exploration: SocraticExploration) -> None:
        """
        Aggiunge un'esplorazione socratica alla storia.

        Args:
            exploration: L'esplorazione da salvare
        """
        SocraticHistory._ensure_history_exists()
        st.session_state[HISTORY_KEY].append(exploration)

    @staticmethod
    def get_session_history() -> list[SocraticExploration]:
        """
        Restituisce la storia delle esplorazioni della sessione corrente.

        Returns:
            Lista delle esplorazioni (vuota se nessuna)
        """
        SocraticHistory._ensure_history_exists()
        return st.session_state[HISTORY_KEY]

    @staticmethod
    def get_stats() -> dict[str, int]:
        """
        Calcola statistiche sulle esplorazioni per tipo di bottone.

        Returns:
            Dict con conteggio per ogni button_type usato
        """
        SocraticHistory._ensure_history_exists()
        history = st.session_state[HISTORY_KEY]

        stats: dict[str, int] = {}
        for exploration in history:
            btn_type = exploration.button_type
            stats[btn_type] = stats.get(btn_type, 0) + 1

        return stats

    @staticmethod
    def clear_history() -> None:
        """Svuota la storia delle esplorazioni socratiche."""
        st.session_state[HISTORY_KEY] = []

    @staticmethod
    def to_serializable() -> list[dict]:
        """
        Serializza tutta la history in una lista di dict JSON-compatibili.

        Returns:
            Lista di dict pronti per json.dump
        """
        SocraticHistory._ensure_history_exists()
        return [exp.to_dict() for exp in st.session_state[HISTORY_KEY]]

    @staticmethod
    def load_from_data(data: list[dict]) -> None:
        """
        Carica la history da una lista di dict e ricostruisce la cache UI.

        Sostituisce completamente la history corrente.
        Ricrea le chiavi socratic_{action}_{msg_index} in session_state
        per ripristinare gli expander nella chat.

        Args:
            data: Lista di dict con i campi delle esplorazioni
        """
        explorations = [
            SocraticExploration.from_dict(item) for item in data
        ]
        st.session_state[HISTORY_KEY] = explorations

        # Ricostruisci cache UI per ogni esplorazione con msg_index valido
        for exp in explorations:
            if exp.msg_index >= 0:
                cache_key = f"socratic_{exp.button_type}_{exp.msg_index}"
                st.session_state[cache_key] = exp.socratic_result
