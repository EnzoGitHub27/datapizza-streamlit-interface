# core/pii_guard.py
# DeepAiUG v1.16.0 (giro 4, P6) - Il guard: verso fuori casa solo testo pulito
# ============================================================================
# GuardedClient avvolge il client vero quando l'ibrido è acceso
# (hybrid.pii.enabled) e la destinazione è fuori casa (core/egress.py).
# Ha gli stessi due metodi che l'app usa, invoke e stream_invoke:
#
#   1. system prompt + testo del messaggio → UNA chiamata a rizzo-pii, così i
#      segnaposto hanno una numerazione sola ([FULLNAME_1] è la stessa
#      persona nel system prompt e nel messaggio);
#   2. il client vero si costruisce per ogni chiamata con il system prompt
#      pulito, e riceve solo testo pulito;
#   3. la risposta torna con i valori veri, solo sul computer:
#      invoke → oggetto con .text ripristinato (e .raw_text/.restore per chi
#               deve analizzare il testo prima di ripristinarlo, la mappa);
#      stream_invoke → chunk con .text CUMULATIVO già ripristinato, senza
#               segnaposto a metà (StreamRestorer).
#
# Guasti (SPEC §8): rizzo-pii giù, in modalità definitiva o con risposta
# rotta → PIIGuardBlocked PRIMA di ogni chiamata al client vero: verso fuori
# casa non parte niente. Un'immagine (MediaBlock) verso fuori casa → blocco.
#
# La tabella segnaposto → valore vive solo durante la chiamata: mai in log,
# messaggi d'errore, cronologia, KB Chat o export. Questo modulo non scrive
# log; le eccezioni portano solo testi fissi e il tipo dell'errore.
# ============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, List, Optional, Sequence, Tuple

from .pii_client import (
    AnonymizedText,
    PIIClient,
    PIIMappingDisabled,
    PIIServiceError,
    PIIServiceUnavailable,
)

# Separatore fra system prompt e testo nella chiamata unica a rizzo-pii.
# Caratteri che rizzo-pii non riconosce come dato personale.
_SEP_MARK = "⟦DEEPAIUG·PARTE⟧"
_SEP = f"\n\n{_SEP_MARK}\n\n"


# v1.16.0 giro 7 — la riga che spiega i segnaposto al modello. Senza, il modello
# li commenta («l'uso di segnaposto (ad esempio, [FULLNAME_1])») e, ripristinata,
# la frase diventa «l'uso di segnaposto (ad esempio, Mario Rossi)». Gli esempi
# hanno «_N», non un numero: non possono coincidere con un segnaposto vero.
PLACEHOLDER_NOTE = (
    "Nota: le parole fra parentesi quadre come [FULLNAME_N] o [CF_N] sono dati "
    "personali tolti di proposito prima dell'invio. Usale così come sono, senza "
    "commentarle, senza spiegarle e senza inventare i valori."
)


class PIIGuardBlocked(Exception):
    """Il testo non è partito verso fuori casa. Il messaggio è per l'utente."""


GATEWAY_NEEDS_PII = (
    "🧭 Con il gateway di Annona, questa funzione verso il cloud richiede rizzo-pii: "
    "non è partito niente. Accendi rizzo-pii (hybrid.pii) oppure usa un modello in casa."
)


class GatewaySideCallBlocked(PIIGuardBlocked):
    """Gateway acceso, rizzo-pii spento: una chiamata fuori da Annona non parte (giro 5b)."""


class GatewayBlockedClient:
    """Al posto del client vero per le chiamate che non passano da Annona
    (bottoni socratici, nudge, generazione e rigenerazione della mappa) quando
    il gateway è acceso, la destinazione è fuori casa e rizzo-pii è spento.
    Non chiama niente: ogni invio solleva GatewaySideCallBlocked."""

    pii_guard = False
    gateway_blocked = True
    last_removed = 0
    last_egress = ""

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        raise GatewaySideCallBlocked(GATEWAY_NEEDS_PII)

    def stream_invoke(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        raise GatewaySideCallBlocked(GATEWAY_NEEDS_PII)


@dataclass
class GuardedResponse:
    """Risposta di invoke: .text con i valori veri, già sul computer.

    raw_text è il testo del modello con i segnaposto; restore() li rimette.
    Servono alla mappa della sessione, che analizza il formato prima di
    ripristinare. Nessuno dei due finisce nel repr.
    """

    text: str
    pii_removed: int = 0
    raw_text: str = field(default="", repr=False)
    restore: Callable[[str], str] = field(default=lambda s: s, repr=False)

    @property
    def content(self) -> str:  # come le risposte di datapizza
        return self.text


@dataclass
class GuardedChunk:
    """Chunk dello streaming: .text cumulativo, già ripristinato."""

    text: str


def _response_text(result: Any) -> str:
    """Come l'app legge le risposte: .text, poi .content, poi str()."""
    if hasattr(result, "text"):
        return result.text or ""
    if hasattr(result, "content"):
        return result.content or ""
    return str(result)


def _is_media(block: Any) -> bool:
    return type(block).__name__ == "MediaBlock" or hasattr(block, "media")


def _is_text_block(block: Any) -> bool:
    return type(block).__name__ == "TextBlock" or (
        hasattr(block, "content") and isinstance(getattr(block, "content"), str)
    )


class GuardedClient:
    """Client che anonimizza prima di uscire di casa. Vedi l'intestazione.

    Args:
        client_factory: system_prompt pulito → client vero (create_client senza guard)
        system_prompt: il system prompt dell'utente, con i valori veri
        pii: PIIClient verso rizzo-pii (solo loopback)
        exclude_tags: tag da lasciare in chiaro (default nessuno)
        on_anonymized: chiamata con il numero di dati tolti, dopo ogni
            anonimizzazione riuscita (per i metadati della conversazione)
    """

    pii_guard = True

    def __init__(
        self,
        client_factory: Callable[[str], Any],
        system_prompt: str,
        pii: PIIClient,
        exclude_tags: Sequence[str] = (),
        on_anonymized: Optional[Callable[[int], None]] = None,
    ):
        self._factory = client_factory
        self._system_prompt = system_prompt or ""
        self._pii = pii
        self._exclude_tags = list(exclude_tags)
        self._on_anonymized = on_anonymized
        # P9 — l'ultimo invio, solo in memoria: quanti dati tolti e il testo
        # com'è partito (con i segnaposto). Mai la tabella.
        self.last_removed: Optional[int] = None
        self.last_egress: str = ""

    # -- preparazione: una chiamata sola a rizzo-pii -------------------------

    def _split_input(self, llm_input: Any) -> Tuple[List[str], Callable[[List[str]], Any]]:
        """Testi da anonimizzare e la funzione che rimonta l'input pulito."""
        if isinstance(llm_input, str):
            return [llm_input], lambda parts: parts[0]

        if isinstance(llm_input, (list, tuple)):
            blocks = list(llm_input)
            if any(_is_media(b) for b in blocks):
                raise PIIGuardBlocked(
                    "🔒 Le immagini non escono dalla tua rete: il messaggio non è stato inviato."
                )
            idx = [i for i, b in enumerate(blocks) if _is_text_block(b)]
            if len(idx) != len(blocks):
                raise PIIGuardBlocked(
                    "🔒 Contenuto non riconosciuto: il messaggio non è stato inviato."
                )

            def rebuild(parts: List[str]) -> Any:
                out = list(blocks)
                for i, text in zip(idx, parts):
                    out[i] = type(blocks[i])(content=text)
                return out

            return [blocks[i].content for i in idx], rebuild

        raise PIIGuardBlocked("🔒 Contenuto non riconosciuto: il messaggio non è stato inviato.")

    def _prepare(self, llm_input: Any) -> Tuple[Any, str, AnonymizedText]:
        texts, rebuild = self._split_input(llm_input)
        if _SEP_MARK in self._system_prompt or any(_SEP_MARK in t for t in texts):
            raise PIIGuardBlocked("🔒 Testo non anonimizzabile: il messaggio non è stato inviato.")
        # la riga sui segnaposto passa da rizzo-pii insieme al resto (stessa chiamata)
        system_prompt = (
            f"{self._system_prompt.rstrip()}\n\n{PLACEHOLDER_NOTE}"
            if self._system_prompt.strip() else PLACEHOLDER_NOTE
        )
        joined = _SEP.join([system_prompt, *texts])

        try:
            anon = self._pii.anonymize(joined, exclude_tags=self._exclude_tags)
        except PIIServiceUnavailable as exc:
            raise PIIGuardBlocked(
                "🛡️ rizzo-pii non risponde: il messaggio non è stato inviato fuori dalla tua rete. "
                "Avvia rizzo-pii e riprova."
            ) from exc
        except PIIMappingDisabled as exc:
            raise PIIGuardBlocked(
                "🛡️ rizzo-pii è in modalità definitiva (senza tabella): il messaggio non è stato "
                "inviato. Riattiva la tabella dei segnaposto nelle impostazioni di rizzo-pii."
            ) from exc
        except PIIServiceError as exc:
            raise PIIGuardBlocked(
                f"🛡️ rizzo-pii ha risposto con un errore ({type(exc).__name__}): "
                "il messaggio non è stato inviato."
            ) from exc

        parts = [p.strip("\n") for p in anon.text.split(_SEP_MARK)]
        if len(parts) != len(texts) + 1:
            raise PIIGuardBlocked(
                "🛡️ Risposta di rizzo-pii non coerente: il messaggio non è stato inviato."
            )
        clean_sp, clean_texts = parts[0].strip(), parts[1:]
        self.last_removed = anon.n_entities
        self.last_egress = (
            (f"[system prompt]\n{clean_sp}\n\n" if clean_sp else "")
            + "[messaggio]\n" + "\n\n".join(clean_texts)
        )
        if self._on_anonymized is not None:
            self._on_anonymized(anon.n_entities)
        return rebuild(clean_texts), clean_sp, anon

    # -- i due metodi usati dall'app ----------------------------------------

    def invoke(self, llm_input: Any, *args: Any, **kwargs: Any) -> GuardedResponse:
        clean_input, clean_sp, anon = self._prepare(llm_input)
        result = self._factory(clean_sp).invoke(clean_input, *args, **kwargs)
        raw = _response_text(result)
        return GuardedResponse(
            text=anon.restore(raw),
            pii_removed=anon.n_entities,
            raw_text=raw,
            restore=anon.restore,
        )

    def stream_invoke(self, llm_input: Any, *args: Any, **kwargs: Any) -> Iterator[GuardedChunk]:
        # L'anonimizzazione avviene al primo next(): se fallisce, al client
        # vero non arriva niente.
        clean_input, clean_sp, anon = self._prepare(llm_input)
        restorer = anon.stream_restorer()
        previous, restored = "", ""
        for chunk in self._factory(clean_sp).stream_invoke(clean_input, *args, **kwargs):
            current = getattr(chunk, "text", None)
            if current is None:
                current = str(chunk)
            if not current:
                continue
            if current.startswith(previous):
                delta = current[len(previous):]
            else:  # client che manda delta invece del cumulativo
                delta = current
                current = previous + current
            previous = current
            out = restorer.push(delta)
            if out:
                restored += out
                yield GuardedChunk(text=restored)
        rest = restorer.flush()
        if rest:
            restored += rest
            yield GuardedChunk(text=restored)
