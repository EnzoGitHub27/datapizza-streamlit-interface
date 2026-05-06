---
versione: 1.15.0
data: 2026-05-06
tipo: spec
ciclo: v1.x maintenance → minor feature
tags:
  - deepaiug
  - release
  - rag
  - embedding
  - chromadb
  - retrieval
  - multilingua
  - quality
---

# SPEC — v1.15.0: Embedding multilingua per RAG (qualità retrieval su contenuti italiani)

## Contesto

**Repository:** `EnzoGitHub27/datapizza-streamlit-interface`
**Branch di partenza:** `dev`
**Versione precedente:** `v1.14.4` (KB sidebar visibility + installer icons)
**Versione target:** `v1.15.0`
**Natura del rilascio:** minor feature — sostituzione del modello di embedding RAG

> [!warning] Re-indicizzazione richiesta
> Cambiare il modello di embedding rende incompatibili tutte le collection ChromaDB pre-esistenti. v1.15.0 rileva automaticamente la mismatch e ricrea le collection vuote: gli utenti esistenti dovranno cliccare "Indicizza" un'altra volta sui loro vault/wiki/cartelle e "Aggiorna KB Chat" se usano la KB epistemica.

---

## Obiettivo

Migliorare la qualità del retrieval in italiano sostituendo l'embedding model di default di ChromaDB (`all-MiniLM-L6-v2`, principalmente inglese) con un modello multilingua (`intfloat/multilingual-e5-small`).

**Non è un cambio cosmetico**: è il singolo intervento con il maggior impatto sulla "qualità delle risposte basate su documenti" che si possa fare senza riscrivere l'architettura RAG.

---

## Problema osservato in v1.14.x

Su contenuti in italiano (vault Obsidian, wiki MediaWiki/DokuWiki in IT, cartelle locali con documentazione aziendale italiana), il retrieval restituiva spesso chunks "topicalmente vicini" ma non "semanticamente rilevanti". Cause:

1. **`all-MiniLM-L6-v2`** è addestrato prevalentemente su corpus inglesi. Le rappresentazioni vettoriali in italiano sono mediocri — il modello "capisce" l'italiano per ereditarietà cross-linguale dal training ma non al livello di un modello multilingua nativo.
2. **384 dimensioni** sono poche per discriminare contenuti tecnici simili in domini ricchi (l'attuale rimane 384, ma vedi "scelta del modello").
3. Nessun reranker, nessuna hybrid search → tutto il peso della qualità retrieval sta sull'embedding.

L'osservazione concreta: domanda in italiano, sistema risponde con chunks che condividono parole-chiave ma rispondono ad altro.

---

## Decisione: quale modello

Tre alternative considerate, in ordine di "vicinanza" al setup attuale:

| Modello | Dim | Multilingua | Peso | Velocità rel. | Qualità IT |
|---|---|---|---|---|---|
| `all-MiniLM-L6-v2` (attuale) | 384 | 🟡 | ~80 MB | 1× | 🟡 |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | 🟢 | ~470 MB | ~1.2× | 🟢 |
| **`intfloat/multilingual-e5-small`** | **384** | **🟢** | **~118 MB** | **~1.5×** | **🟢🟢** |
| `intfloat/multilingual-e5-base` | 768 | 🟢 | ~280 MB | ~3× | 🟢🟢🟢 |
| `intfloat/multilingual-e5-large` | 1024 | 🟢 | ~700 MB | ~5× | 🟢🟢🟢🟢 |

**Scelta: `intfloat/multilingual-e5-small`.** Bilancio ottimale per laptop modesti:
- Top-3 multilingua su MTEB con costo computazionale gestibile
- Drop-in dimensionalmente con il vecchio modello (384 dim) — meno impatto su tuning a valle
- ~118 MB scaricati al primo uso, cached in `~/.cache/huggingface/`
- Override possibile via env var `DEEPAIUG_EMBEDDING_MODEL` per chi vuole spingere su `e5-base`/`e5-large`

---

## Architettura della modifica

### Nuovo modulo: `rag/embeddings.py`

Centralizza la logica di embedding. Tre componenti:

#### 1. `_EmbeddingsHelper`

Wrapper attorno a `sentence_transformers.SentenceTransformer` con due metodi distinti per riflettere il pattern di prefix richiesto dai modelli e5:

```python
helper.encode_query(texts)    # → prefix "query: "
helper.encode_passages(texts) # → prefix "passage: "
```

I prefix migliorano il retrieval perché distinguono il "ruolo" del testo nello spazio vettoriale (la query *cerca* qualcosa, il passage *contiene* la risposta). I vettori sono normalizzati (`normalize_embeddings=True`) per cosine similarity.

#### 2. `MultilingualE5EmbeddingFunction` (ChromaDB-compatible)

Implementa l'interfaccia `chromadb.api.types.EmbeddingFunction`. Chiamata da ChromaDB **solo per le query** (perché in indicizzazione passiamo embedding precomputati). Usa quindi sempre prefix `"query: "`.

#### 3. Singleton + fallback

`get_embeddings_helper()` carica il modello una sola volta. Se `sentence-transformers` non è installato o il download del modello fallisce, restituisce `None` → il chiamante usa il default ChromaDB (regressione automatica, niente crash).

`get_active_model_tag()` restituisce un identificatore stringa del modello effettivamente attivo (es. `"intfloat/multilingual-e5-small"` o `"chromadb_default"` in fallback). Salvato nei metadata della collection per la migrazione.

### Modifiche a `rag/vector_store.py`

#### Indicizzazione

[`SimpleVectorStore._init_store`](../rag/vector_store.py) ora:

1. Calcola `active_tag = get_active_model_tag()`
2. **Migration check**: se la collection esiste già e ha `embedding_model` diverso → `delete_collection`. Sarà ricreata vuota → l'utente vede 0 chunk e re-indicizza.
3. Crea la collection con `embedding_function=` (per le query) e `metadata={"embedding_model": active_tag}` (per future migrazioni).

[`add_chunks`](../rag/vector_store.py) ora pre-computa gli embedding con `helper.encode_passages(documents)` (prefix `"passage:"`) per ogni batch e li passa a ChromaDB via `add(..., embeddings=batch_emb)`.

#### Ricerca

Invariata a livello di codice: `collection.query(query_texts=[query], ...)`. ChromaDB invoca automaticamente l'`embedding_function` configurata, che è la `MultilingualE5EmbeddingFunction` con prefix `"query:"`.

### Modifiche a `core/kb_chat_indexer.py`

Stesso pattern, replicato per la collection separata `deepaiug_chat_kb` (Chat-KB epistemica introdotta in v1.14.0):

- `_get_chroma_collection()`: migration check + embedding_function + metadata
- `index_chat_to_kb()`: pre-computa embedding `passage:` per ogni batch

### Configurazione

Nuova costante in [`config/constants.py`](../config/constants.py):

```python
DEFAULT_EMBEDDING_MODEL = os.environ.get(
    "DEEPAIUG_EMBEDDING_MODEL",
    "intfloat/multilingual-e5-small",
)
```

Override via env var: `export DEEPAIUG_EMBEDDING_MODEL="intfloat/multilingual-e5-base"` per qualità superiore (a costo di ~3× la velocità).

### Dipendenze

Aggiunto a [`requirements.txt`](../requirements.txt):

```
sentence-transformers>=2.2.0
```

Nota: `sentence-transformers` ha come dipendenza transitiva `torch` (~750 MB su Linux/Mac, ~2 GB su Windows con CUDA opzionale). È un'aggiunta significativa al footprint dell'installazione, ma necessaria per modelli sentence-transformers di qualità.

---

## Strategia prefix — perché `passage:` e `query:`

I modelli e5 sono addestrati con un'asimmetria: durante il training i testi-sorgente erano prefissati con `"passage:"`, le query con `"query:"`. Questo aiuta il modello a costruire spazi vettoriali in cui:

- Una query `"come configurare la rete?"` (prefix `query:`) è vicina a un passage `"per configurare la rete..."` (prefix `passage:`)
- Due passage tematicamente simili `"configurazione di rete..."` e `"setup di rete..."` sono vicini tra loro
- Ma soprattutto: una query è ottimizzata per **trovare** passage rilevanti, non per **somigliare** ad altre query

Senza i prefix, e5 funziona ma il guadagno qualitativo è ridotto (~5-10% di recall in meno su benchmark multilingua).

> [!tip] Trasparente all'utente
> Tutta questa logica è incapsulata in `rag/embeddings.py`. Né l'UI né il manager RAG né l'utente finale devono sapere dei prefix — il sistema usa quello giusto in base al ruolo (indexing vs query).

---

## Migrazione — cosa succede agli utenti esistenti

### Comportamento al primo avvio v1.15.0

1. App parte → `_init_store()` invocato sia per `wiki_knowledge_base` che per `deepaiug_chat_kb`
2. ChromaDB carica le collection esistenti (costruite con MiniLM v1.14.x)
3. Ogni collection ha (o non ha) un campo `embedding_model` nei metadata:
   - **Non ha** (collection v1.14.x e precedenti): la check non scatta, la collection rimane intatta — **ma diventa inutilizzabile** perché le query verrebbero embedded con e5 e cercate contro vettori MiniLM (spazi diversi → risultati casuali). L'utente deve cliccare "Indicizza" e ricrearla.
   - **Ha**, valore diverso da quello attuale: la check scatta, la collection viene `delete`-ata e ricreata vuota.
4. La prima volta che `sentence-transformers` viene importato, il modello viene scaricato da HuggingFace (~118 MB → cache utente). Serve connessione internet **una sola volta**.

### Casi d'uso pratici

**A. Utente nuovo (mai indicizzato)** — nessun problema, lavora con e5 dall'inizio.

**B. Utente esistente con vault indicizzato in v1.14.x** — al riavvio:
- La collection ChromaDB sembra esserci (nessun reset auto, mancando il metadata)
- Ma le query restituiscono risultati strani / inconsistenti
- **Azione**: re-indicizzare cliccando "Indicizza" sul vault → la collection viene ricostruita con e5 e i metadata corretti

**C. Utente esistente con Chat-KB epistemica** — stesso scenario:
- **Azione**: cliccare "🔄 Aggiorna KB Chat" nella sidebar → tutte le chat flaggate vengono ricostruite con e5

**D. Sistema senza connessione internet** — `sentence-transformers` prova a scaricare il modello, fallisce, `get_embeddings_helper()` restituisce `None`, vector_store usa il default ChromaDB → fallback funzionante ma senza miglioramento qualitativo. L'utente vede un warning a console.

### Migration check su collection legacy (importante!)

> [!warning] Comportamento corretto in fase di test su utente reale
> Il primo design del migration check confrontava `stored_tag and stored_tag != active_tag` — che lasciava passare le collection legacy (pre-v1.15.0) senza il campo `embedding_model`. Risultato: utenti aggiornati a v1.15.0 con una collection esistente avevano vettori MiniLM in spazio diverso da quello e5, e il retrieval restituiva risultati casuali silenziosamente.
>
> **Correzione applicata**: il check ora è `stored_tag != active_tag`, dove `stored_tag` può essere `None` per collection legacy. Una collection senza tag viene trattata come "modello sconosciuto, presumibilmente diverso" → reset automatico, log chiaro a console (`(<legacy/sconosciuto> → intfloat/multilingual-e5-small)`), e l'utente deve solo cliccare "Indicizza" una volta.

### Banner "tempo stimato" prima dell'indicizzazione (adattivo al modello)

Aggiunto in `_sync_source` un banner che precede la progress bar e mostra una stima del tempo di indicizzazione adattata al modello effettivamente attivo. Copre tutti i 6 entry point (cartella custom, cartella YAML, vault, MediaWiki custom, MediaWiki YAML, DokuWiki custom, DokuWiki YAML) tramite l'unico chokepoint `_sync_source`.

**Tabella secondi/file per modello** (CPU mobile, ~9-10 chunks/file medi).

Tarata su misurazione reale: laptop **i7-8565U** (mobile gen 8, no GPU), vault Obsidian da **966 file → 9043 chunks**, modello `multilingual-e5-small`, tempo totale **18 minuti** → **1.12 s/file**. Il fattore per e5-small è stato impostato a 1.10 con margine; gli altri modelli sono scalati in proporzione ai parametri/dimensioni vettoriali.

| Modello | s/file | Fonte taratura |
|---|---|---|
| `intfloat/multilingual-e5-small` | 1.10 | misurato (i7-8565U) |
| `intfloat/multilingual-e5-base` | 3.00 | scalato (~3× e5-small) |
| `intfloat/multilingual-e5-large` | 5.50 | scalato (~5× e5-small) |
| `paraphrase-multilingual-MiniLM-L12-v2` | 0.80 | scalato (modello più leggero) |
| `chromadb_default` (MiniLM-L6 ONNX) | 0.10 | stimato (ONNX leggero) |

> [!note] Calibrazione futura
> Le stime sono volutamente conservative — meglio dire "~10 min" e finire in 8 che promettere 4 e finire in 18. Se in futuro arrivano misurazioni reali da CPU desktop più potenti, si potranno introdurre fattori per "tier" hardware.

Per le wiki, la stima per pagina è `request_delay + s/file × 0.3` — il throttling HTTP è dominante. Sopra i 5 minuti totali compare l'etichetta `(operazione lunga)`, coerente col pattern già presente in `conversations.py` per il caricamento conversazioni con KB.

Helper esportati da `rag/embeddings.py`:
- `get_seconds_per_file()` — fattore per il modello attivo
- `get_seconds_per_wiki_page(request_delay)` — variante per wiki
- `format_eta(seconds)` — formattazione stringa (`~45s`, `~3 min`, `~7 min (operazione lunga)`)

### Indicatore UI del modello embedding attivo

Aggiunta una riga nelle statistiche KB della sidebar che mostra quale modello è effettivamente in uso nella collection corrente:

- `🌍 Embedding: multilingual-e5-small` — funzionante con il modello v1.15.0
- `🔤 Embedding: ChromaDB default (MiniLM-L6, EN)` — fallback attivo (sentence-transformers non disponibile)
- `⚠️ Embedding: legacy (pre-1.15.0) — re-indicizza per usare e5` — collection vecchia rimasta dopo update

Reso `embedding_model` accessibile via `KnowledgeBaseManager.get_stats()` (proveniente da `SimpleVectorStore.get_stats()` → `collection.metadata`).

---

## Performance attese

### Indicizzazione

- **e5-small** è ~1.5× più lento di MiniLM-L6 in CPU. Su un vault da 6921 chunks (caso reale citato in `docs/docs_ollama_gpu_embedding_notes.md`), l'indicizzazione passa da ~3 min a ~5 min. Costo accettabile per la qualità guadagnata.
- Indicizzazione resta in CPU dentro al processo Streamlit (no Ollama, no rete) — uguale al pattern v1.14.x.
- Batch ChromaDB invariato (`CHROMA_BATCH_SIZE = 500`).

### Ricerca (query a runtime)

- Encoding query con e5-small: ~30-50 ms su CPU (vs ~10-15 ms di MiniLM-L6). Trascurabile rispetto al tempo totale di una query LLM.

### First-run penalty

- ~118 MB scaricati al primo `import sentence_transformers`. Connessione lenta? Conta 1-2 minuti, una volta sola.
- Caching: `~/.cache/huggingface/hub/`.

---

## Estensioni future (non in v1.15.0)

### Migrazione automatica più "smart"

Detect-and-rebuild silenzioso: se il sistema rileva una collection senza `embedding_model` nei metadata, mostra un dialogo all'utente prima di re-indicizzare automaticamente, con stima del tempo.

### Embedding Ollama (opzionale)

Per chi ha già Ollama installato e vuole consolidare lo stack, supportare `nomic-embed-text` come backend alternativo via Ollama. Richiederebbe un secondo `EmbeddingsHelper` (es. `_OllamaEmbeddingsHelper`) e una scelta di config. Costo: complessità + risolto-load/unload citato nelle note GPU.

### Reranker post-retrieval

Cross-encoder leggero (es. `cross-encoder/ms-marco-MiniLM-L-6-v2`) per ri-ordinare i top-20 e tenere i top-5. Tipicamente +10-15% in MRR — più impatto di qualunque cambio embedding. Modulo opzionale `rag/reranker.py`.

### Hybrid search (BM25 + denso)

Indicizzazione BM25 parallela su disco, fusione `Reciprocal Rank Fusion` con i risultati ChromaDB. Aggiunge robustezza per query con termini rari/tecnici.

---

## File modificati

| File | Modifica |
|---|---|
| `rag/embeddings.py` | **Nuovo** — helper, EmbeddingFunction ChromaDB, singleton, fallback graceful |
| `rag/vector_store.py` | `_init_store` con migration check + embedding_function; `add_chunks` con pre-compute "passage:"; `clear` preserva embedding_function |
| `core/kb_chat_indexer.py` | `_get_chroma_collection` con migration check; `index_chat_to_kb` pre-computa embedding "passage:" |
| `config/constants.py` | Aggiunta `DEFAULT_EMBEDDING_MODEL`, bump `VERSION = "1.15.0"` |
| `config/__init__.py` | Esporto `DEFAULT_EMBEDDING_MODEL` |
| `requirements.txt` | `sentence-transformers>=2.2.0` |
| `CHANGELOG.md`, `README.md`, `ROADMAP.md` | Sezione v1.15.0 |
| `docs/SPEC_v1.15.0_multilingual_embeddings.md` | Questo documento |

---

## Workflow Git suggerito

Stesso pattern delle release precedenti.

```bash
git checkout dev
git add rag/embeddings.py rag/vector_store.py core/kb_chat_indexer.py \
        config/constants.py config/__init__.py requirements.txt \
        CHANGELOG.md README.md ROADMAP.md \
        docs/SPEC_v1.15.0_multilingual_embeddings.md
git commit -m "feat(rag): embedding multilingua e5-small per qualità retrieval IT (v1.15.0)"
git push origin dev

git checkout main
git merge dev --no-ff -m "merge: dev → main (v1.15.0) — embedding multilingua per RAG"
git tag v1.15.0
git push origin main --tags
git checkout dev
```

GitHub Release con titolo `v1.15.0 — Embedding multilingua per RAG: retrieval italiano potenziato`. Descrizione che evidenzia: re-indicizzazione richiesta, ~118 MB download al primo uso, env var per override, no breaking API.

---

## Lezioni / decisioni di design

### Una modifica RAG, due collection

ChromaDB in DeepAiUG è usato in due posti distinti: `wiki_knowledge_base` (cartelle/wiki/vault) e `deepaiug_chat_kb` (chat epistemica). Trattarli simmetricamente con lo stesso embedding model evita drift tra i due retrieval e mantiene la coerenza. Centralizzare la logica embedding in un nuovo modulo (`rag/embeddings.py`) ha pagato: due call site, una sola fonte di verità.

### Migrazione vs reset hardcoded

Ricreare automaticamente *qualsiasi* collection senza il metadata `embedding_model` sarebbe stata la soluzione "tecnicamente più pulita" ma operativamente brutale (utenti con vault grandi avrebbero perso index inattesamente). Scelto un comportamento conservativo: solo collection con metadata diverso vengono resettate; collection legacy senza metadata sopravvivono ma producono retrieval di scarsa qualità → l'utente nota e re-indicizza manualmente. Trade-off scelto consapevolmente: meno aggressivo, più sicuro.

### Helper + EmbeddingFunction separati

ChromaDB richiede una `EmbeddingFunction` che restituisce embedding per *query*. Avere una sola classe che gestisce sia query sia passage avrebbe richiesto stato globale o parametro al `__call__` (rotto rispetto al contratto ChromaDB). Soluzione: `EmbeddingFunction` per le query (che ChromaDB invoca da sola), `helper.encode_passages` per l'indicizzazione (che chiamiamo esplicitamente). Pattern pulito, prefix corretti senza compromessi.

### Fallback graceful

Se `sentence-transformers` non è installato, il sistema *non crasha* — degrada a default ChromaDB. È importante per sviluppatori che fanno `git clone` senza `pip install -r requirements.txt`, ed è importante per utenti su sistemi air-gapped (no download da HuggingFace possibile). Il warning a console rende il degrado visibile.

### v1.15.0, non v1.14.5

Decisione di numerazione: il cambio di embedding model rompe (semanticamente) la compatibilità degli indici esistenti, aggiunge una dipendenza non triviale (`torch` transitivo), introduce una env var di config. È più di una patch — è una minor feature. Il `15` segna che la v1.x **non è completamente in maintenance mode**: il progetto può ancora ricevere miglioramenti significativi prima del salto a v2.0 (Semantic Layer + Knowledge Graph).

---

## Riferimenti incrociati

- [[SPEC_v1.14.4_kb_sidebar_visibility_and_installer_icons]] — release precedente
- [[SPEC_v1.14.x_chat_kb]] — Chat KB epistemica (collection `deepaiug_chat_kb`, ora con e5)
- [[docs_ollama_gpu_embedding_notes]] — note storiche su Ollama embedding (non utilizzato in DeepAiUG, ma istruttive sul perché CPU/GPU si comportino come si comportano)

---

*Documento generato durante la sessione di lavoro del 2026-05-06.*
