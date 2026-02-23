# ui/socratic/session_map.py
# DeepAiUG v1.10.0 - Mappa Sessione (F2)
# ============================================================================
# Rende visibile la cornice interpretativa invisibile che si costruisce
# domanda dopo domanda in una sessione.
# Indirizza il "sovrascopo" (Ligas): la direzione simbolica in cui,
# risposta dopo risposta, viene condotta la semiosfera dell'utente.
# ============================================================================

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

# Session state key
SESSION_MAP_KEY = "session_map_data"

# Prompt copiato esattamente dalla sezione 7 di F2_MAPPA_SESSIONE_SPEC.md
SESSION_MAP_PROMPT = """Analizza le seguenti domande fatte dall'utente in questa sessione
e produci una Mappa Sessione strutturata.

DOMANDE DELLA SESSIONE:
{lista_domande}

Produci esattamente:

1. FRAME DOMINANTE (1 frase)
   La cornice interpretativa implicita che emerge dall'insieme
   delle domande. Cosa sta presupponendo l'utente senza saperlo?

2. CONNESSIONE DOMANDE → FRAME
   Per ogni domanda, una riga che spiega come ha contribuito
   a costruire o rinforzare il frame.

3. FRAME NON ESPLORATI (2-3 voci)
   Prospettive alternative che la sessione non ha percorso.
   Non risposte: solo domande che aprirebbero corridoi diversi.

NON giudicare le scelte dell'utente.
NON dare consigli o raccomandazioni.
Restituisci solo la struttura richiesta, in modo chiaro e conciso."""


@dataclass
class SessionMapEntry:
    """Singola domanda analizzata nella mappa sessione."""
    message_index: int
    question_summary: str
    frame_contribution: str
    timestamp: datetime


@dataclass
class SessionMap:
    """Mappa sessione completa prodotta dall'analisi LLM."""
    entries: list[SessionMapEntry]
    dominant_frame: str
    unexplored_frames: list[str]
    session_id: str
    created_at: datetime

    def to_dict(self) -> dict:
        """Serializza la mappa in un dict JSON-compatibile."""
        return {
            "entries": [
                {
                    "message_index": e.message_index,
                    "question_summary": e.question_summary,
                    "frame_contribution": e.frame_contribution,
                    "timestamp": e.timestamp.isoformat(),
                }
                for e in self.entries
            ],
            "dominant_frame": self.dominant_frame,
            "unexplored_frames": self.unexplored_frames,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionMap":
        """
        Ricostruisce una SessionMap da un dict deserializzato.

        Args:
            data: Dict con i campi della mappa (da JSON)
        """
        entries = [
            SessionMapEntry(
                message_index=e["message_index"],
                question_summary=e["question_summary"],
                frame_contribution=e["frame_contribution"],
                timestamp=datetime.fromisoformat(e["timestamp"]),
            )
            for e in data.get("entries", [])
        ]
        return cls(
            entries=entries,
            dominant_frame=data.get("dominant_frame", ""),
            unexplored_frames=data.get("unexplored_frames", []),
            session_id=data.get("session_id", ""),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
        )


def extract_user_questions(messages: list[dict]) -> list[tuple[int, str]]:
    """
    Estrae le domande dell'utente dal chat history.

    Args:
        messages: Lista di messaggi della conversazione

    Returns:
        Lista di tuple (message_index, question_text)
    """
    questions: list[tuple[int, str]] = []
    for i, msg in enumerate(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip():
                questions.append((i, content.strip()))
    return questions


def get_nudge_text(question_count: int) -> str:
    """
    Restituisce il testo del nudge per la mappa sessione.

    Puro testo, nessuna logica decisionale.

    Args:
        question_count: Numero di domande nella sessione corrente
    """
    return (
        f"Hai fatto {question_count} domande in questa sessione.\n"
        "Sai da dove stai guardando il problema?"
    )


def _extract_llm_text(result: object) -> str:
    """Extract text from LLM response, following existing project pattern."""
    if hasattr(result, "text"):
        return result.text
    elif hasattr(result, "content"):
        return result.content
    return str(result)


def _parse_llm_response(
    raw_text: str,
    questions: list[tuple[int, str]],
) -> tuple[str, list[SessionMapEntry], list[str]]:
    """
    Parse LLM response into structured components.

    Returns:
        Tuple of (dominant_frame, entries, unexplored_frames)
    """
    dominant_frame = ""
    entries: list[SessionMapEntry] = []
    unexplored_frames: list[str] = []

    current_section = ""
    now = datetime.now()

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        # Detect section headers
        upper = stripped.upper()
        if "FRAME DOMINANTE" in upper:
            current_section = "frame"
            continue
        elif "CONNESSIONE" in upper and "FRAME" in upper:
            current_section = "connections"
            continue
        elif "FRAME NON ESPLORATI" in upper:
            current_section = "unexplored"
            continue

        # Parse content per section
        if current_section == "frame" and not dominant_frame:
            dominant_frame = stripped.strip('"').strip("'")
        elif current_section == "connections":
            # Match numbered lines (1. / 1) ) or bulleted (- / •)
            import re
            num_match = re.match(r'^(\d+)[.\)]\s*(.*)', stripped)
            dash_match = re.match(r'^[-•]\s*(.*)', stripped) if not num_match else None

            line_content = None
            q_number = None
            if num_match:
                q_number = int(num_match.group(1))
                line_content = num_match.group(2)
            elif dash_match:
                line_content = dash_match.group(1)

            if line_content is not None:
                # Split on arrow or colon to extract contribution
                contribution = line_content
                for sep in ["→", "->", ":"]:
                    if sep in line_content:
                        contribution = line_content.split(sep, 1)[1].strip()
                        break

                # Associate with question by number or sequential order
                target_idx = None
                if q_number and 1 <= q_number <= len(questions):
                    target_idx = q_number - 1
                else:
                    target_idx = len(entries)

                if target_idx is not None and target_idx < len(questions):
                    msg_idx, q_text = questions[target_idx]
                    entries.append(SessionMapEntry(
                        message_index=msg_idx,
                        question_summary=q_text[:120],
                        frame_contribution=contribution,
                        timestamp=now,
                    ))
            elif entries:
                # Continuation line
                entries[-1].frame_contribution += " " + stripped
        elif current_section == "unexplored":
            # Strip leading markers like →, -, *
            clean = stripped.lstrip("→-*• ").strip()
            if clean:
                unexplored_frames.append(clean)

    # If parsing didn't produce entries, create basic ones from questions
    if not entries and questions:
        for msg_idx, q_text in questions:
            entries.append(SessionMapEntry(
                message_index=msg_idx,
                question_summary=q_text[:120],
                frame_contribution="",
                timestamp=now,
            ))

    return dominant_frame, entries, unexplored_frames


class SessionMapAnalyzer:
    """
    Analizzatore mappa sessione — delega all'LLM su richiesta esplicita dell'utente.

    Non accede a session_state: riceve i dati e restituisce il risultato.
    La decisione di quando invocare l'analisi resta in app.py.
    """

    @staticmethod
    def analyze(
        messages: list[dict],
        llm_invoke_fn: Callable,
        session_id: str,
    ) -> "SessionMap | None":
        """
        Analizza le domande della sessione e produce una mappa.

        Args:
            messages: Lista completa dei messaggi della conversazione
            llm_invoke_fn: Funzione per invocare l'LLM (es. client.invoke)
            session_id: Identificativo della sessione corrente

        Returns:
            SessionMap con l'analisi, o None se meno di 2 domande
        """
        questions = extract_user_questions(messages)

        if len(questions) < 2:
            return None

        # Build numbered list for prompt
        lista_domande = "\n".join(
            f"{i + 1}. {q_text}" for i, (_, q_text) in enumerate(questions)
        )
        prompt = SESSION_MAP_PROMPT.format(lista_domande=lista_domande)

        result = llm_invoke_fn(prompt)
        raw_text = _extract_llm_text(result)

        dominant_frame, entries, unexplored_frames = _parse_llm_response(
            raw_text, questions
        )

        return SessionMap(
            entries=entries,
            dominant_frame=dominant_frame,
            unexplored_frames=unexplored_frames,
            session_id=session_id,
            created_at=datetime.now(),
        )
