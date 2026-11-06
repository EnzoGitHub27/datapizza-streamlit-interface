# rag/embeddings.py
# DeepAiUG v1.15.0 - Embedding multilingua per RAG
# ============================================================================
# Sostituisce il default ChromaDB (all-MiniLM-L6-v2, principalmente inglese)
# con un modello multilingua di sentence-transformers, ottimizzato per IT.
#
# Strategia prefix per modelli e5:
#   - "passage: <testo>" per i documenti durante l'indicizzazione
#   - "query: <testo>" per le query durante la ricerca
# I prefix migliorano il retrieval perché distinguono il "ruolo" del testo
# nello spazio vettoriale.
# ============================================================================

import os
import warnings
from typing import List, Optional, Tuple

# Default: e5-small è il miglior compromesso qualità/velocità per IT.
# 117M params, 384 dim (drop-in con MiniLM-L6 in termini di dimensionalità),
# multilingua nativo, ~118 MB download al primo uso (cached).
# Override possibile via env var per esperimenti (es. multilingual-e5-base
# per più qualità, paraphrase-multilingual-MiniLM-L12-v2 per più velocità).
EMBEDDING_MODEL_NAME = os.environ.get(
    "DEEPAIUG_EMBEDDING_MODEL",
    "intfloat/multilingual-e5-small",
)

# Identificatore "logico" del modello attivo, salvato nei metadata della
# collection ChromaDB. Quando cambia, le collection esistenti vengono
# ricreate (vedi vector_store._init_store).
EMBEDDING_MODEL_TAG = EMBEDDING_MODEL_NAME

# Prefix usati dai modelli e5. Per altri modelli sentence-transformers
# (paraphrase-*, sentence-t5-*) i prefix sono inutili ma non dannosi.
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "


# ============================================================================
# Scelta del device (v1.15.4)
# ============================================================================
# torch può dire cuda.is_available() == True anche quando non ha i kernel per
# la scheda: es. torch 2.13+cu130 (sm_75 e superiori) su una MX250 (sm_61).
# In quel caso il primo calcolo fallisce con «no kernel image». Qui si usa la
# GPU solo se torch è compilato per la sua architettura; altrimenti la CPU.
# DEEPAIUG_EMBEDDINGS_DEVICE=cpu|cuda forza la scelta.
# ============================================================================

DEVICE_ENV_VAR = "DEEPAIUG_EMBEDDINGS_DEVICE"


def _arch_supported(capability: Tuple[int, int], arch_list: List[str]) -> bool:
    """
    True se torch ha kernel per la scheda: lo stesso sm_XY, un sm della stessa
    generazione con minor più basso (compatibilità binaria), o un PTX
    compute_XY non più recente della scheda (compilato al volo).
    """
    major, minor = capability
    for arch in arch_list:
        kind, _, num = arch.partition("_")
        if not num.isdigit() or len(num) < 2:
            continue
        a_major, a_minor = int(num[:-1]), int(num[-1])
        if kind == "sm" and a_major == major and a_minor <= minor:
            return True
        if kind == "compute" and (a_major, a_minor) <= (major, minor):
            return True
    return False


def select_device() -> Tuple[str, str]:
    """Restituisce (device, motivo). Ogni errore nel controllo → cpu."""
    forced = os.environ.get(DEVICE_ENV_VAR, "").strip().lower()
    if forced in ("cpu", "cuda"):
        return forced, f"forzato da {DEVICE_ENV_VAR}"

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            import torch

            if not torch.cuda.is_available():
                return "cpu", "CUDA non disponibile"
            major, minor = torch.cuda.get_device_capability()
            arch_list = list(torch.cuda.get_arch_list())
            sm = f"sm_{major}{minor}"
            if _arch_supported((major, minor), arch_list):
                return "cuda", f"GPU {sm} supportata da torch {torch.__version__}"
            return "cpu", (
                f"GPU {sm} non supportata da torch {torch.__version__} "
                f"({', '.join(arch_list) or 'nessuna architettura'})"
            )
    except Exception as e:  # noqa: BLE001 - nel dubbio, CPU
        return "cpu", f"controllo GPU fallito ({type(e).__name__}: {e})"


class _EmbeddingsHelper:
    """
    Wrapper attorno a sentence-transformers. Carica il modello una sola volta
    (singleton in get_embeddings_helper) e fornisce due metodi distinti per
    encode di query e passage con il prefix corretto.
    """

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.device, reason = select_device()
        print(f"🧮 Embedding {model_name} su {self.device}: {reason}")
        self.model = SentenceTransformer(model_name, device=self.device)

    def encode_query(self, texts: List[str]) -> List[List[float]]:
        prefixed = [QUERY_PREFIX + t for t in texts]
        embeddings = self.model.encode(
            prefixed,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def encode_passages(self, texts: List[str]) -> List[List[float]]:
        prefixed = [PASSAGE_PREFIX + t for t in texts]
        embeddings = self.model.encode(
            prefixed,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()


_helper_singleton: Optional[_EmbeddingsHelper] = None
_helper_init_failed: bool = False


def get_embeddings_helper() -> Optional[_EmbeddingsHelper]:
    """
    Restituisce il singleton di _EmbeddingsHelper. Lazy: il modello viene
    caricato solo alla prima chiamata. Se sentence-transformers non è
    installato (o il download del modello fallisce), restituisce None e
    il chiamante può fare fallback al default ChromaDB.
    """
    global _helper_singleton, _helper_init_failed

    if _helper_singleton is not None:
        return _helper_singleton
    if _helper_init_failed:
        return None

    try:
        _helper_singleton = _EmbeddingsHelper(EMBEDDING_MODEL_NAME)
        return _helper_singleton
    except ImportError:
        print(
            "⚠️ sentence-transformers non installato. "
            "Fallback a embedding default ChromaDB (qualità ridotta su IT). "
            "Installa con: pip install sentence-transformers"
        )
        _helper_init_failed = True
        return None
    except Exception as e:
        print(
            f"⚠️ Errore caricamento modello embedding {EMBEDDING_MODEL_NAME}: {e}. "
            f"Fallback a embedding default ChromaDB."
        )
        _helper_init_failed = True
        return None


# ============================================================================
# ChromaDB EmbeddingFunction wrapper
# ============================================================================

def _build_chroma_embedding_function():
    """
    Costruisce un'EmbeddingFunction compatibile con ChromaDB usando il helper.
    ChromaDB la chiamerà SOLO per le query (in fase di indicizzazione passiamo
    embeddings precomputati con prefix "passage:"), quindi qui usiamo
    "query: " come prefix.
    """
    try:
        from chromadb.api.types import EmbeddingFunction
    except ImportError:
        return None

    helper = get_embeddings_helper()
    if helper is None:
        return None

    class MultilingualE5EmbeddingFunction(EmbeddingFunction):
        """Embedding function ChromaDB con prefix 'query: ' per modelli e5."""

        def __call__(self, input):
            # input può essere stringa singola o lista; normalizziamo a lista
            if isinstance(input, str):
                texts = [input]
            else:
                texts = list(input)
            return helper.encode_query(texts)

        def name(self):
            return f"multilingual-e5:{helper.model_name}"

    return MultilingualE5EmbeddingFunction()


_embedding_function_singleton = None


def get_embedding_function():
    """
    Singleton dell'EmbeddingFunction passata a ChromaDB nella creazione delle
    collection. Restituisce None se sentence-transformers non disponibile —
    in quel caso il chiamante deve creare la collection senza
    embedding_function (ChromaDB userà il suo default).
    """
    global _embedding_function_singleton
    if _embedding_function_singleton is None:
        _embedding_function_singleton = _build_chroma_embedding_function()
    return _embedding_function_singleton


def get_active_model_tag() -> str:
    """
    Restituisce il tag identificativo del modello effettivamente attivo,
    da salvare nei metadata della collection ChromaDB per le migrazioni.
    Se il modello custom non si carica, ritorna 'chromadb_default' per
    distinguerlo da una collection costruita col modello multilingua.
    """
    helper = get_embeddings_helper()
    if helper is None:
        return "chromadb_default"
    return EMBEDDING_MODEL_TAG


# ============================================================================
# Stime tempo di indicizzazione (adattive al modello attivo)
# ============================================================================
# Secondi/file approssimati su CPU mobile (laptop tipico utente DeepAiUG:
# i5/i7 mobile gen 8-12, no GPU acceleration), assumendo ~9-10 chunks per file
# in media. Tarati su benchmark reali (es. i7-8565U + vault 966 file +
# multilingual-e5-small → 1080s totali → 1.12 s/file).
#
# Servono SOLO per la UI (banner "tempo stimato") — non influiscono sul
# comportamento dell'indicizzazione effettiva.
# ============================================================================

_TIME_PER_FILE_SECONDS = {
    # Tarato su misurazione reale (i7-8565U mobile, 966 file → 18 min)
    "intfloat/multilingual-e5-small":              1.10,
    # ~3× e5-small (modello 2.4× parametri + 2× dim vettore)
    "intfloat/multilingual-e5-base":               3.00,
    # ~5× e5-small (560M params)
    "intfloat/multilingual-e5-large":              5.50,
    # MiniLM-L12 multilingual: simile a e5-small in dim ma layer più leggeri
    "paraphrase-multilingual-MiniLM-L12-v2":       0.80,
    # MiniLM-L6 (default ChromaDB ONNX): 6 layer, modello distillato leggero
    "all-MiniLM-L6-v2":                            0.10,
    "chromadb_default":                            0.10,
}

# Default conservativo se il modello attivo non è in tabella (assume e5-small).
_DEFAULT_TIME_PER_FILE = 1.10


def get_seconds_per_file() -> float:
    """
    Restituisce una stima in secondi del costo di indicizzazione per file
    locale, adattata al modello di embedding attualmente attivo.

    Usato dalla UI per il banner "tempo stimato" prima dell'indicizzazione.
    """
    return _TIME_PER_FILE_SECONDS.get(get_active_model_tag(), _DEFAULT_TIME_PER_FILE)


def get_seconds_per_wiki_page(request_delay: float = 0.5) -> float:
    """
    Stima per pagina wiki = HTTP throttling + parsing + embedding.
    Le wiki tipicamente generano 1-3 chunks per pagina, quindi il
    contributo dell'embedding è frazione di get_seconds_per_file().
    """
    return float(request_delay) + get_seconds_per_file() * 0.3


def format_eta(seconds: float) -> str:
    """
    Formatta una stima in secondi in stringa leggibile per l'utente.

    >>> format_eta(45)   -> '~45s'
    >>> format_eta(180)  -> '~3 min'
    >>> format_eta(450)  -> '~7 min (operazione lunga)'
    """
    s = max(1, int(seconds))
    if s < 60:
        return f"~{s}s"
    if s < 300:
        return f"~{s // 60} min"
    return f"~{s // 60} min (operazione lunga)"
