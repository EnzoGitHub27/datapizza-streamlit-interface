# MANUALE DeepAiUG

**DeepAiUG Streamlit LLM Interface — Manuale di installazione, configurazione e utilizzo**

| | |
|---|---|
| **Prodotto** | DeepAiUG Chat 🧠 |
| **Versione documentata** | v1.15.1 |
| **Data manuale** | 2026-07-12 |
| **Repository** | https://github.com/EnzoGitHub27/datapizza-streamlit-interface |
| **Licenza** | MIT |
| **Autore progetto** | Vincenzo Iodice (EnzoGitHub27) — community DeepAiUG |

> Questo manuale è stato generato analizzando il codice sorgente in sola lettura. Documenta esclusivamente le funzionalità effettivamente presenti nella versione 1.15.1; le funzionalità pianificate per v2.0.0 (Semantic Layer, Knowledge Graph, Docker, API REST, journaling riflessivo) **non** sono trattate perché non ancora implementate.

---

## Indice

**Introduzione**
- [Capitolo 1 — Che cos'è DeepAiUG](#capitolo-1--che-cosè-deepaiug)

**PARTE I — Guida per il sistemista**
- [Capitolo 2 — Requisiti di sistema](#capitolo-2--requisiti-di-sistema)
- [Capitolo 3 — Installazione](#capitolo-3--installazione)
- [Capitolo 4 — Aggiornamento e diagnostica](#capitolo-4--aggiornamento-e-diagnostica)
- [Capitolo 5 — Avvio dell'applicazione](#capitolo-5--avvio-dellapplicazione)
- [Capitolo 6 — File di configurazione](#capitolo-6--file-di-configurazione)
- [Capitolo 7 — Gestione delle chiavi API](#capitolo-7--gestione-delle-chiavi-api)
- [Capitolo 8 — Architettura dati e directory](#capitolo-8--architettura-dati-e-directory)
- [Capitolo 9 — Il motore RAG in dettaglio](#capitolo-9--il-motore-rag-in-dettaglio)
- [Capitolo 10 — Sicurezza e raccomandazioni operative](#capitolo-10--sicurezza-e-raccomandazioni-operative)

**PARTE II — Manuale utente**
- [Capitolo 11 — Primi passi: l'interfaccia](#capitolo-11--primi-passi-linterfaccia)
- [Capitolo 12 — Connessione e scelta del modello](#capitolo-12--connessione-e-scelta-del-modello)
- [Capitolo 13 — La chat: messaggi e allegati](#capitolo-13--la-chat-messaggi-e-allegati)
- [Capitolo 14 — Knowledge Base documentale (cartelle, wiki, vault)](#capitolo-14--knowledge-base-documentale-cartelle-wiki-vault)
- [Capitolo 15 — KB Chat: le conversazioni come memoria](#capitolo-15--kb-chat-le-conversazioni-come-memoria)
- [Capitolo 16 — Le funzioni socratiche](#capitolo-16--le-funzioni-socratiche)
- [Capitolo 17 — La Mappa Sessione](#capitolo-17--la-mappa-sessione)
- [Capitolo 18 — Gestione delle conversazioni](#capitolo-18--gestione-delle-conversazioni)
- [Capitolo 19 — Esportazione](#capitolo-19--esportazione)
- [Capitolo 20 — Privacy: come DeepAiUG protegge i tuoi dati](#capitolo-20--privacy-come-deepaiug-protegge-i-tuoi-dati)

**Appendici**
- [Appendice A — Tabella dei limiti e valori predefiniti](#appendice-a--tabella-dei-limiti-e-valori-predefiniti)
- [Appendice B — Risoluzione dei problemi](#appendice-b--risoluzione-dei-problemi)
- [Appendice C — Glossario](#appendice-c--glossario)

---

# Capitolo 1 — Che cos'è DeepAiUG

DeepAiUG è un'interfaccia web (basata su Streamlit) per dialogare con modelli linguistici (LLM), progettata secondo due principi fondanti:

1. **Privacy-first.** Il funzionamento predefinito è completamente locale: il modello gira su Ollama sulla macchina dell'utente o su un server della rete locale. L'uso di provider cloud (OpenAI, Anthropic, Google) è possibile ma sorvegliato: quando sono in gioco documenti locali o Knowledge Base, l'invio al cloud viene bloccato o richiede conferma esplicita.
2. **Approccio socratico.** L'applicazione non si limita a rispondere: offre strumenti ("bottoni socratici", "Mappa Sessione") che restituiscono attrito cognitivo, aiutando l'utente a esaminare assunzioni, limiti e prospettive alternative invece di delegare il giudizio all'AI. Questi strumenti sono sempre disattivabili: l'attrito ha valore solo se scelto (si veda `PHILOSOPHY.md` nel repository).

**Funzionalità principali in sintesi:**

- Chat multi-turno con risposte in streaming, verso tre tipi di backend: **Ollama locale**, **server remoto** (API compatibile OpenAI, tipicamente Ollama in LAN), **provider cloud** (OpenAI, Anthropic, Google Gemini, endpoint custom).
- **Upload di file** in chat (PDF, TXT, MD, DOCX, immagini) con estrazione del testo.
- **Knowledge Base documentale (RAG)**: indicizzazione di cartelle locali, wiki MediaWiki/DokuWiki, vault Obsidian/LogSeq/export Notion, con ricerca semantica multilingua (ChromaDB + embedding `intfloat/multilingual-e5-small`).
- **KB Chat epistemica**: le conversazioni salvate possono essere marcate per rilevanza e reindicizzate come memoria consultabile nelle risposte future.
- **Funzioni socratiche**: 5 bottoni di analisi critica sotto ogni risposta, storico delle esplorazioni, tre livelli di profondità.
- **Mappa Sessione**: analisi su richiesta della "cornice implicita" costruita dalle domande della sessione.
- **Persistenza e export**: salvataggio automatico delle conversazioni, esportazione in Markdown, JSON, TXT, PDF e ZIP batch.
- **Branding personalizzabile** (titolo, icona, banner, tema "Matrix" con pioggia di caratteri).

**Nota sui nomi:** la cartella/repository si chiama `datapizza-streamlit-interface` (usa il framework `datapizza-ai` per i client LLM), ma il prodotto si chiama **DeepAiUG** e l'installer lo colloca in `~/DeepAiUG`. La versione autorevole è quella dichiarata in `config/constants.py` (`VERSION = "1.15.1"`); il campo `version = "0.1.0"` in `pyproject.toml` è solo metadato del pacchetto Poetry e va ignorato.

---

# PARTE I — GUIDA PER IL SISTEMISTA

# Capitolo 2 — Requisiti di sistema

## 2.1 Sistemi operativi supportati

| OS | Supporto | Note |
|---|---|---|
| Linux | ✅ Installer dedicato | Debian/Ubuntu/Mint (`apt`), Fedora/RHEL/CentOS (`dnf`), Arch/Manjaro (`pacman`) |
| macOS | ✅ Installer dedicato | Con o senza Homebrew; richiede Xcode Command Line Tools |
| Windows 11 | ✅ Installer `.bat` | Documentato in `installer/README_installer.md` |

## 2.2 Python

- **Requisito operativo verificato dagli script**: Python **≥ 3.10**.
- Gli installer, quando Python manca, installano **Python 3.12** (su macOS scaricano `python-3.12.10-macos11.pkg`).
- Se si installa via Poetry, `pyproject.toml` richiede `python >= 3.12, < 3.14`.

## 2.3 Dipendenze principali (`requirements.txt`)

| Area | Pacchetti |
|---|---|
| Core | `streamlit>=1.28.0`, `python-dotenv>=1.0.0`, `pyyaml>=6.0` |
| Framework LLM | `datapizza-ai` (da installare **prima**), `datapizza-ai-clients-openai-like` |
| RAG | `chromadb>=0.4.0`, `sentence-transformers>=2.2.0`, `beautifulsoup4>=4.12.0`, `PyPDF2>=3.0.0` |
| Wiki | `mwclient>=0.10.0`, `dokuwiki>=0.1.0` |
| Export | `reportlab>=4.0.0` |
| Upload file | `python-docx>=0.8.0`, `Pillow>=10.0.0` |

⚠️ **Ordine di installazione critico**: `datapizza-ai` va installato **prima** di `requirements.txt`, perché `datapizza-ai-clients-openai-like` ne dipende. Gli installer ufficiali rispettano già quest'ordine.

⚠️ **Spazio disco**: `sentence-transformers` trascina `torch` come dipendenza (≈ 888 MB su Linux, ≈ 250 MB su Mac). Al primo utilizzo del RAG viene inoltre scaricato da HuggingFace il modello di embedding `intfloat/multilingual-e5-small` (≈ 118 MB, cache in `~/.cache/huggingface/hub/`).

## 2.4 Ollama e hardware

- **Ollama** è il motore LLM locale. Gli installer lo installano automaticamente (Linux: `curl -fsSL https://ollama.com/install.sh | sh`; macOS: Homebrew, script o zip in `/Applications/`).
- **GPU: non richiesta.** L'embedding RAG gira in CPU dentro il processo Streamlit; la GPU viene rilevata dagli installer a solo scopo informativo.
- Modello LLM suggerito dagli installer in base alla RAM:

| RAM | Modello suggerito | Alternative |
|---|---|---|
| < 8 GB | `phi3:mini` | `tinyllama` |
| 8–15 GB | `llama3.2:3b` | `phi3`, `phi3:mini` |
| 16–31 GB | `mistral:7b` | `llama3.2:3b`, `gemma2:9b` |
| ≥ 32 GB | `llama3.1:8b` | `mistral:7b`, `gemma2:9b` |

---

# Capitolo 3 — Installazione

Gli script si trovano nella cartella `installer/`. Il file `install.sh` nella root è solo un rimando informativo.

**Percorsi e costanti comuni a tutti gli script:**

| Variabile | Valore |
|---|---|
| Cartella di installazione | `~/DeepAiUG` |
| Virtualenv | `~/DeepAiUG/venv` |
| Sorgente | ZIP del branch `main` da GitHub |
| Log installazione | `~/DeepAiUG_install_log.txt` |

## 3.1 Installazione su Linux — `installer/installa_deepaiug_linux.sh`

Lo script esegue 11 passi, con conferma iniziale (`s/n`):

1. Disclaimer e conferma dell'utente.
2. Rilevamento del package manager (apt/dnf/pacman), della RAM (`free`) e della GPU (`lspci`).
3. Verifica/installazione di Python ≥ 3.10 (su apt installa anche `python3-venv`).
4. Verifica/installazione di `curl` e `unzip`.
5. Verifica/installazione di Ollama.
6. Creazione di `~/DeepAiUG`, download dello ZIP in `/tmp`, estrazione e copia dei file.
7. Creazione del virtualenv, aggiornamento di pip, installazione di `datapizza-ai` e poi `pip install -r requirements.txt --prefer-binary` con output visibile a schermo (via `tee`, novità v1.15.1). In caso di errore pip lo script termina con errore.
8. Suggerimento del modello LLM in base alla RAM (INVIO = accetta il default).
9. Avvio di `ollama serve` in background e `ollama pull` del modello scelto (non bloccante se fallisce).
10. Creazione del launcher `~/DeepAiUG/avvia_deepaiug.sh` (avvia Ollama se spento, attiva il venv, lancia Streamlit) e della voce di menu `~/.local/share/applications/deepaiug.desktop` (nome "DeepAiUG", icona `deepaiug-logo.png`, terminale visibile).
11. Riepilogo finale con percorso del log.

## 3.2 Installazione su macOS — `installer/installa_deepaiug_mac.sh`

Stessa logica in 12 passi, con queste differenze:

- Rilevamento hardware con `sysctl hw.memsize`, `system_profiler`, `sw_vers`.
- Verifica/installazione delle **Xcode Command Line Tools** (`xcode-select --install`).
- **Homebrew opzionale**: se presente (o se l'utente acconsente a installarlo) viene usato per Python e Ollama; altrimenti download diretto (`.pkg` da python.org, zip di Ollama in `/Applications/`).
- Launcher: `~/DeepAiUG/DeepAiUG.command` e, in modalità best-effort, un bundle `~/DeepAiUG/DeepAiUG.app` con icona `.icns` generata dal logo (via `sips` + `iconutil`) e rimozione della quarantena.
- **Nota Gatekeeper**: alla prima esecuzione può servire tasto destro → "Apri".

## 3.3 Cosa fare dopo l'installazione

1. Avviare dal menu applicazioni (Linux) o dal `.app`/`.command` (macOS): il browser si apre in 20–30 secondi.
2. (Facoltativo) Personalizzare i file YAML di configurazione — vedi Capitolo 6.
3. (Facoltativo) Configurare le chiavi API cloud — vedi Capitolo 7.

---

# Capitolo 4 — Aggiornamento e diagnostica

## 4.1 Aggiornamento — `aggiorna_deepaiug_linux.sh` / `aggiorna_deepaiug_mac.sh`

Gli script di aggiornamento (log in `~/DeepAiUG_update_log.txt`):

1. Verificano la presenza di `~/DeepAiUG` e del virtualenv.
2. Leggono la versione installata da `config/constants.py`.
3. **Eseguono un backup di `conversations/`** in `~/DeepAiUG_backup_conversations`.
4. Scaricano ed estraggono il nuovo ZIP da GitHub.
5. **Aggiornano solo il codice**: `app.py`, `requirements.txt`, `pyproject.toml` e le cartelle `config/`, `core/`, `ui/`, `rag/`, `export/`, `installer/`, `.streamlit/`.
6. **Preservano** (non toccano mai): `conversations/`, `secrets/`, `.env`, `branding.yaml`, `cloud_models.yaml`, `remote_servers.yaml`, `security_settings.yaml`, `wiki_sources.yaml`. Le personalizzazioni sopravvivono quindi agli aggiornamenti.
7. Aggiornano `datapizza-ai` e le dipendenze (`pip install -r requirements.txt --upgrade --prefer-binary`, output visibile).
8. Mostrano un riepilogo con vecchia e nuova versione.

⚠️ **Dopo l'aggiornamento a v1.15.0 o successive** da una versione precedente: il modello di embedding è cambiato, quindi le collection ChromaDB esistenti vengono automaticamente svuotate al primo avvio (migration check). Gli utenti devono **ri-indicizzare** le proprie sorgenti (cartelle/wiki/vault) e premere "🔄 Aggiorna KB Chat". Il primo utilizzo scarica il nuovo modello (~118 MB).

## 4.2 Diagnostica — `check_deepaiug.sh`

Script unico per Linux e macOS (rileva l'OS con `uname -s`). Verifica: Python ≥ 3.10, presenza di Ollama (nel PATH o in `/Applications/Ollama.app`), esistenza di `~/DeepAiUG`, del venv e di `requirements.txt`; elenca i modelli con `ollama list` e mostra le ultime 20 righe del log di installazione. Al termine stampa il conteggio errori e l'esito.

---

# Capitolo 5 — Avvio dell'applicazione

## 5.1 Comando di avvio

```bash
cd ~/DeepAiUG
source venv/bin/activate
streamlit run app.py        # oppure: python -m streamlit run app.py
```

I launcher creati dall'installer fanno esattamente questo, avviando prima Ollama se non è in esecuzione.

## 5.2 Porta e parametri server

- **Porta: 8501** (default Streamlit — non è configurata esplicitamente nel progetto).
- `.streamlit/config.toml` contiene **solo il tema** ("Matrix": `primaryColor = "#00d4aa"`, sfondo `#020c06`, testo `#c8ffd4`, font monospace). **Non** contiene alcuna sezione `[server]`: valgono i default di Streamlit, incluso il limite upload widget di 200 MB (il limite applicativo reale per file è però 10 MB, imposto dal codice).
- Per cambiare porta o binding si possono usare le normali opzioni Streamlit, ad es. `streamlit run app.py --server.port 8502 --server.address 127.0.0.1`.

⚠️ **L'applicazione non ha autenticazione né isolamento per-utente**: chiunque raggiunga la porta 8501 è "l'utente". Non esporre la porta su reti non fidate senza un reverse proxy con autenticazione (vedi Capitolo 10).

---

# Capitolo 6 — File di configurazione

Tutti i file YAML risiedono nella **root del progetto** (con percorso alternativo `config/<nome>.yaml`); sono letti con `yaml.safe_load`. Se un file manca o è malformato si usano i default senza errori. Nessuno di questi file viene sovrascritto dagli script di aggiornamento.

## 6.1 `branding.yaml` — personalizzazione dell'aspetto

```yaml
app:
  title: "DeepAiUG Chat"     # titolo dell'app (default)
  icon: "🧠"                  # icona (default)
  subtitle: ""                # sottotitolo; vuoto = nascosto
news_banner:
  enabled: true               # banner novità in alto
  # text: "..."               # testo personalizzato (commentato = default di versione)
  # version: "1.15.1"
matrix_rain: true             # effetto "pioggia Matrix" sullo sfondo
matrix_rain_intensity: 0.055  # opacità; range consigliato 0.01–0.20
```

## 6.2 `cloud_models.yaml` — provider cloud e modelli

Definisce i provider e i modelli mostrati nella UI **senza toccare il codice**. Non contiene chiavi API.

```yaml
settings:
  allow_custom_models: true   # se true, l'utente può digitare un modello non in lista ("✏️ Altro...")
providers:
  openai:
    name: "OpenAI"
    base_url: "https://api.openai.com/v1"
    models:
      - {id: "gpt-4o", name: "GPT-4o"}
      - {id: "gpt-4o-mini", name: "GPT-4o mini"}
      - {id: "o3-mini", name: "o3-mini"}
    default_model: "gpt-4o-mini"
  anthropic:
    name: "Anthropic (Claude)"
    base_url: "https://api.anthropic.com/v1"
    models: [...]             # claude-sonnet-4-5-20250929, claude-haiku-4-5-20251001
    default_model: "claude-sonnet-4-5-20250929"
  google:
    name: "Google Gemini"
    base_url: "https://generativelanguage.googleapis.com/v1beta/openai"
    models: [...]             # gemini-2.0-flash, gemini-2.5-pro-preview-06-05
    default_model: "gemini-2.0-flash"
  custom: {}                  # base_url e modelli liberi
```

Se il file manca, la UI usa i provider hardcoded in `config/constants.py` (OpenAI → `gpt-4o-mini`, Anthropic → `claude-sonnet-4-20250514`, Google → `gemini-1.5-pro`, Custom).

## 6.3 `remote_servers.yaml` — server Ollama remoti

```yaml
mode: "custom_allowed"        # "fixed" | "selectable" | "custom_allowed"
default_server: "proxmox_p6000"
servers:
  proxmox_p6000:
    name: "Proxmox P6000"
    icon: "🖥️"
    host: "192.168.1.10"      # default: localhost
    port: 11434               # default: 11434
    description: "..."
  dopey:
    host: "192.168.1.151"
settings:
  connection_timeout: 10      # secondi
  show_refresh_button: true   # mostra "🔄 Aggiorna modelli"
```

Significato di `mode`:
- `fixed` — l'utente usa solo il `default_server`, nessuna scelta;
- `selectable` — scelta dalla lista `servers`;
- `custom_allowed` — lista + possibilità di inserire un host manualmente (default se il file è assente).

## 6.4 `security_settings.yaml` — impostazioni di sicurezza

```yaml
cloud_api_keys:
  show_saved_keys: false      # default SICURO: chiavi salvate mascherate in UI
  hidden_message: "✅ Key salvata (nascosta per sicurezza)"
  visible_message: "✅ Key salvata (visibile)"
# remote_servers:             # placeholder NON implementato
#   require_authentication: ...
#   log_connections: ...
```

L'unica impostazione attiva oggi è `show_saved_keys`. La sezione `remote_servers` è un segnaposto commentato senza effetto.

## 6.5 `wiki_sources.yaml` — sorgenti wiki e documentali

Definisce le sorgenti della Knowledge Base offerte all'utente. Struttura di primo livello:

```yaml
mode: "selectable"            # come remote_servers: fixed | selectable | custom
default_source: "wikipedia_it"
sources:                      # (retrocompatibile con la vecchia chiave "wikis")
  <id>:
    name: "..."
    type: mediawiki | dokuwiki | local_folder
    url / path: ...
    api_path: "/w/api.php"    # MediaWiki
    namespaces: [0]
    max_pages: 30
    timeout: 30
    exclude_categories: [...] # o exclude_namespaces per DokuWiki
    username: "${WIKI_USER}"  # credenziali via variabili d'ambiente ${VAR}
global_settings:
  cache_dir: "wiki_cache"
  cache_ttl_hours: 24
  request_delay: 0.5          # pausa tra richieste HTTP (rispetto dei server)
  batch_size: 50
  strip_wiki_markup: true
  include_metadata: true
```

Il file di esempio contiene 9 sorgenti: 2 MediaWiki interne/di test, 2 DokuWiki, 1 cartella locale, e 4 wiki pubbliche di prova (Wikipedia IT/EN, Wikivoyage IT, Wikibooks IT). Le credenziali (`username`, `password`, `api_key`, `token`) possono essere espresse come `${NOME_VARIABILE}` e vengono espanse dalle variabili d'ambiente.

## 6.6 Variabili d'ambiente riconosciute

| Variabile | Effetto |
|---|---|
| `OPENAI_API_KEY` | Chiave OpenAI |
| `ANTHROPIC_API_KEY` | Chiave Anthropic |
| `GOOGLE_API_KEY` | Chiave Google Gemini |
| `CUSTOM_API_KEY` | Chiave per provider custom |
| `DEEPAIUG_EMBEDDING_MODEL` | Override del modello di embedding RAG (es. `intfloat/multilingual-e5-base`) |
| `${VAR}` nei YAML wiki | Credenziali wiki espanse a runtime |

È supportato un file **`.env`** nella root (caricato con `python-dotenv`).

---

# Capitolo 7 — Gestione delle chiavi API

Le chiavi dei provider cloud **non** stanno in `cloud_models.yaml`. Sono lette in quest'ordine di precedenza:

1. **Variabile d'ambiente** (o `.env` nella root): `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `CUSTOM_API_KEY`.
2. **File secrets**: `secrets/<provider>_key.txt` (es. `secrets/openai_key.txt`, `secrets/anthropic_key.txt`).
3. **Interfaccia web**: l'utente inserisce la chiave nella sidebar; il bottone "💾 Salva" la scrive in `secrets/<provider>_key.txt` (la cartella viene creata al bisogno).

**Precauzioni per l'amministratore:**

- `secrets/` è esclusa da git (`.gitignore`), ma i file sono salvati **in chiaro** e possono nascere con permessi larghi (664). Su macchine condivise applicare `chmod 600 secrets/*.txt` e preferire variabili d'ambiente o `.env` con permessi ristretti.
- La visualizzazione in chiaro delle chiavi salvate nella UI è disattivata di default (`show_saved_keys: false` in `security_settings.yaml`); lasciarla così salvo necessità.
- Non lasciare copie di backup dei file chiave in cartelle sincronizzate o mondo-leggibili.

---

# Capitolo 8 — Architettura dati e directory

Tutti i percorsi sono relativi alla cartella di installazione (`~/DeepAiUG` con l'installer).

| Percorso | Contenuto | Note |
|---|---|---|
| `conversations/` | Conversazioni salvate, un JSON per chat: `conv_YYYYMMDD_HHMMSS.json` | Backuppata dagli script di update |
| `knowledge_base/vectorstore/` | Vector store ChromaDB della KB documentale (wiki/cartelle/vault) — `chroma.sqlite3` + cartelle UUID | Collection: `wiki_knowledge_base` |
| `knowledge_base/chat_kb_vectorstore/` | Vector store ChromaDB della KB Chat | Collection: `deepaiug_chat_kb` |
| `knowledge_base/chat_kb_meta.json` | Metadati indicizzazione KB Chat (`last_indexed`, `chats_indexed`, `total_chunks`) | |
| `wiki_cache/` | File `sync_<id>.json` / `sync_doku_<id>.json`: **solo statistiche** dell'ultimo sync wiki (pagine totali/caricate, URL, timestamp) — non contengono le pagine | |
| `secrets/` | Chiavi API in file di testo | In chiaro — vedi Cap. 7 |
| `.env` | Variabili d'ambiente opzionali | |
| `~/.cache/huggingface/hub/` | Cache del modello di embedding scaricato | Fuori dal progetto |

**Contenuto di un file conversazione**: messaggi completi, statistiche (token stimati), impostazioni della Knowledge Base usata, storico delle esplorazioni socratiche, metadati KB (`kb_metadata`: `includi_in_kb`, `rilevanza`, `tipo`, `note`) e il flag `vault_used` (true se la chat è stata condotta con un vault attivo).

---

# Capitolo 9 — Il motore RAG in dettaglio

Riferimento tecnico per il sistemista; l'uso dal punto di vista dell'utente è nei Capitoli 14–15.

## 9.1 Pipeline

`Adapter (sorgente) → Chunker → Embedding → ChromaDB → Retrieval top-k → contesto iniettato nel prompt`

L'orchestrazione è in `rag/manager.py` (`KnowledgeBaseManager`). Ogni indicizzazione **svuota e ricostruisce** la collection (non è incrementale, salvo il rilevamento dei file modificati per i vault).

## 9.2 Chunking

- Unità: **caratteri** (non token). Default: **chunk 1000, overlap 200** (regolabili da UI: 200–3000 / 0–500).
- Split gerarchico sui separatori in ordine di priorità: intestazioni Markdown (`\n## `, `\n### `), paragrafi (`\n\n`), righe, frasi (`. `, `! `, `? `, `; `), virgole, spazi. I chunk non vengono mai tagliati prima di 1/3 della dimensione target.

## 9.3 Embedding

- Modello di default: **`intfloat/multilingual-e5-small`** (384 dimensioni, multilingua, ~118 MB, CPU-friendly), via `sentence-transformers`, vettori normalizzati per cosine similarity, con prefissi e5 (`passage:` per i documenti, `query:` per le query).
- Override con `DEEPAIUG_EMBEDDING_MODEL`; alternative note: `intfloat/multilingual-e5-base` (768 dim), `intfloat/multilingual-e5-large` (1024 dim), `paraphrase-multilingual-MiniLM-L12-v2` (384 dim).
- **Fallback**: se `sentence-transformers` non è disponibile, il sistema non si blocca: ChromaDB usa la propria embedding function di default (`all-MiniLM-L6-v2`, orientata all'inglese, qualità inferiore sull'italiano). La UI lo segnala ("🔤 Embedding: ChromaDB default (MiniLM-L6, EN)").
- **Migrazione automatica**: la collection memorizza il tag del modello di embedding; se al riavvio il tag non coincide (o è assente, caso pre-1.15.0), la collection viene svuotata e va ri-indicizzata manualmente.
- Gli embedding **non usano Ollama né GPU**: girano in CPU nel processo Streamlit (CPU al 100% durante l'indicizzazione è normale).

## 9.4 Vector store e retrieval

- **ChromaDB persistente** su disco (vedi Cap. 8); fallback in memoria con ricerca keyword se ChromaDB non è installato.
- Indicizzazione in batch da **500** chunk.
- Retrieval: **top-k = 5** di default (regolabile 1–10 da UI). **Non esistono soglie di similarità né reranker**: vengono restituiti sempre i k risultati più vicini.
- KB Chat: retrieval con **boost per rilevanza** (distanza divisa per 1.0/1.15/1.30 per rilevanza bassa/media/alta) e filtro opzionale per tipo.

## 9.5 Client LLM e scoperta modelli

- Client costruiti con la libreria `datapizza` (`ClientFactory`): provider nativi per OpenAI/Anthropic/Google, `OpenAILikeClient` per Ollama locale, host remoti ed endpoint custom.
- Modelli locali: rilevati con `ollama list` (subprocess, timeout 5 s). Modelli remoti: endpoint HTTP `/api/tags` del server Ollama (timeout 10 s). In caso di errore la lista risulta semplicemente vuota.

## 9.6 Sincronizzazione wiki

- Adapter MediaWiki (`mwclient`) e DokuWiki; pausa di **0,5 s** tra le richieste (`request_delay`), user-agent dedicato, strip del markup wiki.
- A fine sync viene scritto un file di statistiche in `wiki_cache/` (non è una cache dei contenuti).

---

# Capitolo 10 — Sicurezza e raccomandazioni operative

Sintesi dell'audit statico `SECURITY_AUDIT.md` (v1.15.1, 2026-07-07): **nessun RCE** (assenti `pickle`/`eval`/`exec`/`os.system`; YAML sempre con `safe_load`; unico subprocess `ollama list` senza shell; upload mai scritti su disco; export senza zip-slip; nessuna chiave hardcoded). Rilevati 0 Critical, 4 High, 4 Medium, 4 Low.

## 10.1 Modello di minaccia

L'app è pensata per **uso mono-utente locale**. Non ha login: "utente" è chiunque raggiunga la porta Streamlit. In LAN condivisa o esposta a Internet i rischi aumentano sensibilmente.

## 10.2 Raccomandazioni pratiche

1. **Non esporre la porta 8501** fuori dall'host o dalla LAN fidata; per accessi multipli usare un reverse proxy con autenticazione (es. nginx + basic auth/SSO) e binding su `127.0.0.1`.
2. **Chiavi API**: `chmod 600 secrets/*.txt`; preferire `.env`/variabili d'ambiente; `show_saved_keys: false`.
3. **Consapevolezza dei limiti del blocco privacy** (findings H2/H3): il blocco verso il cloud è ancorato alla Knowledge Base documentale; il toggle "Usa KB Chat" non è incluso nel blocco, e gli URL di "Remote host"/"Local" sono testo libero trattato come fidato. Istruire gli utenti a non puntare host "remote" verso endpoint Internet e a disattivare "Usa KB Chat" prima di passare al cloud se le chat indicizzate sono sensibili.
4. **SSRF (H1)**: gli URL (server remoti, wiki, base_url) non sono validati; su host esposti o in cloud questo permette scansioni interne. Limitare la rete in uscita dell'host se l'app è raggiungibile da terzi.
5. **Percorsi cartelle RAG (H4)**: l'utente può indicizzare qualunque cartella leggibile dal processo; in contesti multi-utente eseguire l'app con un utente di sistema dedicato con permessi minimi.
6. **Dipendenze (M4)**: `PyPDF2` è deprecato e le dipendenze non sono pinnate; valutare lock file e scansioni periodiche (`pip-audit`).
7. Dopo gli aggiornamenti, verificare l'installazione con `installer/check_deepaiug.sh`.

---

# PARTE II — MANUALE UTENTE

# Capitolo 11 — Primi passi: l'interfaccia

## 11.1 Cosa vedi all'avvio

All'apertura del browser (di norma `http://localhost:8501`) trovi:

- **Tema "Matrix"**: sfondo verde scurissimo, testo verde-teal, titoli con effetto glitch e, se abilitata, la "pioggia" di caratteri in sottofondo (personalizzabile o disattivabile dal sistemista via `branding.yaml`).
- **Titolo dinamico** che indica il backend attivo: `🧠 DeepAiUG Chat → Ollama v1.15.1` (locale), `→ Remote` o `→ {provider}` (cloud).
- **Banner novità** con le note della versione (se non è attiva la Knowledge Base).
- **Indicatore di connessione**:
  - `💻 Locale - Privacy totale` (verde)
  - `🌐 Remote - Rete locale` (azzurro)
  - `☁️ Cloud - Dati esterni (KB e Upload disabilitati)` (giallo)
- **Quattro contatori**: `📝 Messaggi` (totale), `👤 Domande` (tuoi messaggi), `🪙 Token` (stima, ~4 caratteri per token), `🆔 ID` (identificativo della conversazione).
- L'**area conversazione** (vuota: "👋 Inizia una conversazione!") e in fondo la sezione **✍️ Messaggio** con allegati e campo di invio.
- A sinistra la **sidebar** con tutte le impostazioni: ⚙️ Configurazione, 📚 Knowledge Base, 💬 Conversazione, 🧠 Modalità Socratica, 📊 Mappa sessione, 📤 Export.

Il bordo superiore della pagina è **verde** quando lavori in locale/remoto e **rosso** quando sei su cloud: un colpo d'occhio sulla privacy.

## 11.2 Il flusso di base

1. Scegli (o lascia) il backend nella sidebar → ⚙️ Configurazione (default: Ollama locale).
2. Scrivi nel campo "Scrivi il tuo messaggio..." e premi **🚀 Invia**.
3. La risposta appare **in streaming**: prima tre pallini animati ("sta scrivendo"), poi il testo che cresce con un cursore `▌`, con scorrimento automatico della pagina.
4. Sotto ogni risposta trovi i **bottoni socratici** (Capitolo 16), salvo modalità "Veloce".
5. Con **Auto-save** attivo (default) la conversazione si salva da sola a ogni messaggio.

Ogni messaggio appare in una "bolla": la tua con avatar 👤 e sfondo blu, quella dell'AI con avatar 🤖, il nome del modello e l'orario. Le risposte supportano Markdown completo (tabelle, blocchi di codice).

---

# Capitolo 12 — Connessione e scelta del modello

Sidebar → expander **⚙️ Configurazione** → selettore **"Tipo connessione"** con tre opzioni.

## 12.1 Local (Ollama) — `### 🖥️ Locale`

Modalità predefinita, massima privacy: tutto resta sul tuo computer.

- **Base URL**: default `http://localhost:11434/v1`.
- **🔄 Aggiorna**: rileva i modelli installati in Ollama (accanto compare il conteggio).
- **Modello**: selezione dall'elenco; se non viene trovato nulla puoi digitare il nome (default proposto `llama3.2`).

## 12.2 Remote host — `### 🌐 Remote`

Per usare un server Ollama nella tua rete locale (es. una macchina con GPU).

- A seconda della configurazione del sistemista: server fisso, elenco di server (**"Server"**), oppure elenco più inserimento manuale (**"✏️ Inserisci manualmente..."** → campo **Host**, es. `http://192.168.1.10:11434/v1`).
- **API Key (opzionale)** se il server la richiede.
- **🔄 Aggiorna modelli** interroga il server e popola l'elenco **Modello**.

## 12.3 Cloud provider — `### ☁️ Cloud`

Per usare OpenAI, Anthropic (Claude), Google Gemini o un endpoint custom.

- **Provider**: elenco configurato dal sistemista (o i quattro predefiniti).
- **API Key**: se non ne hai una salvata, inseriscila e premi **💾 Salva** (verrà ricordata). Se ne esiste una salvata vedrai "✅ Key salvata (nascosta per sicurezza)" e il bottone **🔄 Usa altra key** per sostituirla.
- **Modello**: dall'elenco del provider; se abilitato, l'opzione **✏️ Altro...** permette di digitare un modello non in lista.

⚠️ In modalità cloud **l'upload di file e la Knowledge Base sono disabilitati** per proteggere i tuoi dati (Capitolo 20). Se la Knowledge Base è attiva, il passaggio al cloud viene proprio **bloccato** e la connessione torna su "Local (Ollama)".

## 12.4 Parametri del modello — expander `⚙️ Parametri`

| Parametro | Range | Default | Significato |
|---|---|---|---|
| System Prompt | testo libero | "Sei un assistente utile. Rispondi in modo chiaro e preciso." | Istruzioni permanenti date al modello |
| Temperature | 0.0 – 2.0 (step 0.1) | 0.7 | Creatività: bassa = risposte prevedibili, alta = più varie |
| Max messaggi | 10 – 100 (step 10) | 50 | Quanti messaggi recenti restano nel contesto |

---

# Capitolo 13 — La chat: messaggi e allegati

## 13.1 Allegare file — `📎 Allega file (opzionale)`

Sopra il campo messaggio puoi trascinare o selezionare **più file**:

| Tipo | Formati | Cosa succede |
|---|---|---|
| Documenti | PDF, TXT, MD, DOCX | Il testo viene estratto e aggiunto al tuo messaggio |
| Immagini | PNG, JPG, JPEG, GIF, WEBP | Richiedono un modello "Vision" (vedi sotto) |

**Limiti**: massimo **10 MB per file**; il testo estratto da un documento viene troncato a **50.000 caratteri** (con nota esplicita nel messaggio). Dai PDF viene estratto il testo pagina per pagina (`[Pagina N]`); dai DOCX paragrafi e tabelle; i PDF di sole immagini vengono segnalati come privi di testo estraibile.

Ogni file allegato appare in un'**anteprima** richiudibile: thumbnail per le immagini, primi 500 caratteri per i documenti, con icona per tipo (📕 PDF, 📘 DOCX, 📄 TXT, 📝 MD, 🖼️ immagine).

**Modelli Vision**: le immagini sono accettate solo se il nome del modello è riconosciuto come multimodale (LLaVA e varianti, Granite3-Vision, Moondream, BakLLaVA, CogVLM, Fuyu, MiniCPM-V). Con un modello non-Vision compare l'avviso "⚠️ Immagini rilevate ma il modello non supporta Vision" e le immagini vengono ignorate.

> ℹ️ **Limite noto (v1.15.1)**: anche con un modello Vision le immagini vengono preparate ma **non ancora inviate** al modello — l'integrazione dell'API Vision è segnata come TODO nel codice. Ciò che arriva effettivamente all'LLM è il testo dei documenti.

**Su cloud** l'upload è disabilitato: "📎 Upload file disabilitato per privacy".

## 13.2 Inviare e ricevere

- Scrivi nel campo (placeholder "Scrivi il tuo messaggio...", oppure "Chiedi qualcosa sui tuoi documenti..." se la KB è attiva) e premi **🚀 Invia**.
- Prima dell'invio l'app verifica: modello selezionato ("❌ Seleziona un modello!"), chiave API per il cloud ("❌ Inserisci API key!"), blocco KB+cloud ("🔒 Cloud bloccato con Knowledge Base attiva!").
- Se la Knowledge Base è attiva vedrai gli spinner "🔍 Ricerca documenti rilevanti..." e/o "📚 Ricerca nella KB Chat...", con il conteggio dei documenti trovati; le **fonti** usate compaiono sotto la risposta nell'expander **"📎 Fonti (N)"**.
- Il bottone **🔄 Nuova** azzera tutto e apre una conversazione nuova (messaggi, contatori, allegati, storico socratico, mappa sessione).

---

# Capitolo 14 — Knowledge Base documentale (cartelle, wiki, vault)

La Knowledge Base (KB) permette all'AI di rispondere **sui tuoi documenti**: l'app cerca i passaggi più pertinenti alla tua domanda e li fornisce al modello come contesto, chiedendogli di citare le fonti.

Sidebar → expander **📚 Knowledge Base** (aperto di default).

## 14.1 Attivazione

Spunta **"🔍 Usa Knowledge Base"**. Comparirà:
- `🔒 Privacy OK - Dati locali` se sei in Local/Remote;
- `🔒 Cloud provider bloccato per privacy!` se sei su cloud (la KB non funziona con il cloud, per scelta di design).

Quando la KB è attiva e indicizzata, nell'area principale appare il banner: `📚 Knowledge Base ATTIVA - N documenti | N chunks`.

## 14.2 Sorgenti disponibili — `📁 Sorgente Documenti`

| Sorgente | Icona | Formati/Note |
|---|---|---|
| Cartella Locale | 📁 | `.md`, `.txt`, `.html`(+`.htm`), `.pdf` — con checkbox per formato e "📂 Includi sottocartelle" |
| MediaWiki | 🌐 | wiki tipo Wikipedia; richiede il pacchetto `mwclient` |
| DokuWiki | 📘 | richiede il pacchetto `dokuwiki` |
| Vault Obsidian | 🟣 | `.md`, `.canvas`; ignora `.obsidian`, `templates`, `.trash`, `.archive` |
| Vault LogSeq | 🟤 | `.md`, `.org`; ignora le cartelle di backup di LogSeq |
| Export Notion | ⬛ | `.md` |

Il tipo di vault viene **riconosciuto automaticamente** dal percorso ("🟣 Obsidian rilevato — N file compatibili trovati"). Oltre alle sorgenti predisposte dal sistemista (in `wiki_sources.yaml`), l'opzione **"➕ Configura manualmente..."** permette di inserire URL wiki o percorsi ad hoc, con opzioni avanzate (namespace, numero massimo di pagine, autenticazione username/password).

## 14.3 Indicizzazione

1. Configura la sorgente (percorso o URL).
2. (Facoltativo) Regola i **⚙️ Parametri Chunking**: dimensione chunk 200–3000 caratteri (default 1000), overlap 0–500 (default 200).
3. Leggi il **banner di stima**: numero di file/pagine e tempo previsto in base al modello di embedding ("💡 CPU al 100% durante l'embedding — è normale, non chiudere l'app").
4. Premi il bottone di indicizzazione (**🔄 Indicizza Documenti**, **🔄 Indicizza Obsidian**, **🔄 Sincronizza Wiki**, ecc.) e segui la barra di avanzamento fino a "✅ Indicizzazione completata!".

Ogni indicizzazione ricostruisce da zero l'indice della sorgente. Per le wiki già configurate viene mostrata la data dell'ultimo sync e il numero di pagine.

## 14.4 Statistiche e parametri di ricerca

La sezione **📊 Statistiche** mostra: documenti e chunk indicizzati, data ultimo aggiornamento, tipo di storage ("💾 ChromaDB (persistente)" oppure "⚠️ Memoria (temporaneo)") e il modello di embedding in uso ("🌍 Embedding: intfloat/multilingual-e5-small").

In **⚙️ Parametri RAG** lo slider **"Documenti per query"** (1–10, default 5) decide quanti passaggi vengono recuperati per ogni domanda.

---

# Capitolo 15 — KB Chat: le conversazioni come memoria

Oltre ai documenti, DeepAiUG può usare **le tue conversazioni passate** come base di conoscenza ("KB epistemica", introdotta in v1.14.0): decisioni prese, intuizioni, memoria aziendale.

## 15.1 Includere una chat nella KB — expander `📚 Includi nella Knowledge Base`

Nella sidebar, per la conversazione corrente:

- Checkbox **"Includi questa chat nella Knowledge Base"**;
- **Rilevanza**: `Bassa` / `Media` / `Alta` — le chat più rilevanti pesano di più nelle ricerche (boost 1.0 / 1.15 / 1.30);
- **Tipo** (multiselezione): `decisione`, `insight`, `memoria_aziendale`, `riferimento`, `sperimentale`;
- **Note** libere.

Se la chat non è ancora salvata su disco compare l'avviso di inviare un messaggio (o attendere l'auto-save) prima di indicizzare.

## 15.2 Indicizzare — `🔄 Aggiorna KB Chat`

L'indicizzazione **non è automatica**: dopo aver flaggato le chat premi **"🔄 Aggiorna KB Chat"**. Al termine: "✅ Indicizzate N chat, M chunk totali".

## 15.3 Gestire la KB — expander `📚 Gestione Knowledge Base`

- Elenco delle chat incluse, con data, modello, stelle di rilevanza (⭐/⭐⭐/⭐⭐⭐), tipi, numero di chunk e note.
- **✏️ Modifica** (rilevanza/tipo/note, con re-indicizzazione) e **🗑️ Rimuovi** (con conferma: la chat esce dalla KB ma **non** viene cancellata).
- Sezione **"Flagga chat esistenti"** per aggiungere in blocco vecchie conversazioni (checkbox multiple + "➕ Aggiungi alla KB (N)").

## 15.4 Usare la KB Chat nelle risposte — `📚 Usa KB Chat`

Attiva il toggle **"📚 Usa KB Chat"** per includere le chat indicizzate nel recupero. Puoi **filtrare per tipo** (es. solo `decisione`). Durante l'invio vedrai "📚 Ricerca nella KB Chat..." e le fonti appariranno come `💬 {titolo della chat}`.

> ⚠️ **Attenzione privacy**: a differenza della KB documentale, il toggle "Usa KB Chat" **non blocca automaticamente il cloud** (limite noto v1.15.1). Se le tue chat indicizzate contengono informazioni riservate, disattivalo prima di passare a un provider cloud.

---

# Capitolo 16 — Le funzioni socratiche

Le funzioni socratiche sono il tratto distintivo di DeepAiUG: strumenti per **esaminare criticamente** le risposte dell'AI (e le tue domande) invece di accettarle passivamente. Non assegnano punteggi né giudizi automatici: restituiscono materiale su cui riflettere.

## 16.1 Le tre modalità — sidebar `### 🧠 Modalità Socratica`

Selettore **"Profondità analisi"**:

| Modalità | Comportamento |
|---|---|
| 🚀 Veloce | Nessun bottone socratico — risposte immediate |
| ⚖️ Standard *(default)* | Bottoni socratici visibili sotto le risposte |
| 🧠 Socratico | Bottoni + invito esplicito a riflettere dopo ogni risposta |

## 16.2 I 5 bottoni sotto ogni risposta

**Gruppo "Analizza la risposta:"**

| Bottone | Cosa produce |
|---|---|
| 🔄 **Alternative** | Tre tipi di alternative: di *soluzione* (altri approcci allo stesso obiettivo), di *framing* (riformulazioni del problema), di *assunzione* (cosa cambia se cambiano le premesse) — con l'indicazione di quando ciascuna sarebbe preferibile |
| 🤔 **Assunzioni** | Classifica il contenuto in *Fatti* (verificabili), *Inferenze* (probabilistiche) e *Valutazioni* (giudizi); per le inferenze chiave applica il "Test della Premessa": se fosse errata, quali conclusioni reggerebbero? |
| ⚠️ **Limiti** | Quando la risposta NON funziona: *limiti di dominio* (campo instabile o controverso), *di contesto* (informazioni mancanti su di te), *del modello* (a chi la risposta non è adatta) |
| 🎭 **Confuta** | Avvocato del diavolo su due livelli: obiezioni alle *conclusioni* e attacco alla *struttura* (se le premesse fossero false, cosa collassa?) — volutamente senza ammorbidire |

**Gruppo "Sfida la domanda:"**

| Bottone | Cosa produce |
|---|---|
| 🪞 **Rifletti** | L'unico che analizza la **tua domanda**, non la risposta: presupposizioni implicite, destinatario implicito, e la "domanda sotto la domanda". Non risponde: ti aiuta a capire se stai facendo la domanda giusta |

Dettagli utili:
- Ogni bottone mostra uno spinner durante la generazione e poi diventa ✅ (es. "✅ Alternative"); il risultato si apre in un pannello dedicato con una domanda-guida finale (es. "💡 Quale prospettiva ti sembra più utile?").
- I risultati sono **memorizzati**: ripremere il bottone non rigenera. In calce compare il modello e l'ora di generazione.
- In modalità 🧠 Socratico, dopo i bottoni compare l'invito: *"Prima di accettare questa risposta, chiediti: quali alternative non ho considerato? Cosa sto dando per scontato?"*.

## 16.3 Storico delle esplorazioni — sidebar `📋 Esplorazioni socratiche`

Ogni uso di un bottone viene registrato (tipo, orario, domanda, risposta analizzata, risultato) e salvato con la conversazione. Nella sidebar trovi: il **totale**, il conteggio per tipo (🔄 🤔 ⚠️ 🎭 🪞), l'elenco delle **ultime 10 esplorazioni** consultabili una per una, e la cancellazione protetta (checkbox "Conferma cancellazione" + "🗑️ Cancella storico").

---

# Capitolo 17 — La Mappa Sessione

Domanda dopo domanda, ogni sessione costruisce senza accorgersene una **cornice interpretativa** (un "frame") che orienta le domande successive. La Mappa Sessione rende visibile questa cornice — **solo quando la richiedi tu**: per scelta di design non c'è nessuna analisi automatica in background.

## 17.1 Le tre modalità — sidebar `📊 Mappa sessione`

| Modalità | Comportamento |
|---|---|
| 🔄 Progressiva | La mappa si aggiorna dopo ogni risposta e diventa visibile dopo **4** domande |
| 🔔 A soglia *(default)* | Dopo **5** domande compare un invito (una sola volta per sessione): *"Hai fatto 5 domande in questa sessione. Sai da dove stai guardando il problema?"* con il bottone **📊 Mostra mappa sessione** |
| ⏹️ Disattivata | Nessuna mappa, nessun invito |

Il popover **"❓ Cos'è la Mappa Sessione?"** accanto al titolo spiega la funzione e i suoi riferimenti teorici (sovrascopo, vincolo teleologico, capitale semantico → `PHILOSOPHY.md`).

## 17.2 Cosa mostra

La mappa (expander **"📊 Mappa della sessione"**) contiene tre elementi:

1. **Frame dominante** — una frase: la cornice implicita che stai presupponendo;
2. **Domande → frame** — per ogni tua domanda, come ha costruito o rinforzato quella cornice;
3. **Frame non esplorati** — 2–3 prospettive alternative, formulate come domande, che la sessione non ha percorso.

La mappa non giudica e non dà consigli. È generata **dallo stesso modello che stai già usando** (nessun invio aggiuntivo verso l'esterno), richiede almeno **2 domande** e può essere rigenerata con **🔄 Rigenera mappa** (o creata su una conversazione caricata con **📊 Genera mappa**).

---

# Capitolo 18 — Gestione delle conversazioni

Sidebar → `### 💬 Conversazione`.

## 18.1 Salvataggio automatico

La checkbox **"Auto-save"** (attiva di default) salva la conversazione su disco a ogni messaggio (e dopo ogni esplorazione socratica). Non esiste — e non serve — un bottone "Salva" manuale. Le conversazioni non si possono rinominare: sono identificate da data e ora di creazione.

## 18.2 Caricare una conversazione

Il menu **"Carica"** elenca le conversazioni salvate come `{icone} {data} - {modello} ({N messaggi})`. Le icone raccontano il contenuto:

| Icona | Significato |
|---|---|
| 🧠 | La chat è stata condotta con un vault attivo |
| 📚 | Usava una wiki come KB / inclusa nella KB Chat (📚⭐ rilevanza media, 📚⭐⭐ alta) |
| 📁 🟣 🟤 ⬛ | Usava cartella locale / vault Obsidian / LogSeq / Notion |
| 📎 | Contiene allegati |
| 🔒 (prefisso) | Sei su cloud e la chat contiene dati locali: caricamento protetto |

Selezionata la conversazione, premi **📂 Carica**:
- se sei su **cloud** e la chat contiene dati locali, il caricamento è **bloccato** per privacy;
- se la chat usava una KB locale "pesante" (**≥ 50 file**) viene chiesta conferma, con stima del tempo di ri-indicizzazione (**✅ Procedi** / **❌ Annulla**);
- al caricamento vengono ripristinati messaggi, contatori, impostazioni KB, storico socratico e metadati, e la Knowledge Base viene **ri-indicizzata automaticamente** con barra di avanzamento.

**🗑️ Elimina** cancella definitivamente la conversazione dal disco.

---

# Capitolo 19 — Esportazione

Sidebar → `### 📤 Export` (attivo appena c'è almeno un messaggio).

## 19.1 Esportare la conversazione corrente

1. **Formato Export**: `📝 Markdown (.md)`, `📋 JSON (.json)`, `📄 TXT (.txt)`, `📕 PDF (.pdf)`.
2. **Contenuto**: conversazione completa, oppure ultimi 10 / 20 / 50 messaggi.
3. **Nome file** (senza estensione; default `conversation_{id}`).
4. **👁️ Anteprima Export** mostra il risultato nell'area principale (il PDF non è anteprimabile); **📥 Download** genera il file e fa comparire il bottone di salvataggio **💾 Salva**.

Contenuto per formato:
- **Markdown**: titolo, data, modello, messaggi con intestazioni `## 👤 Tu / 🤖 AI` e orari, fonti in corsivo, footer con versione;
- **JSON**: struttura completa e rielaborabile (info export + conversazione con id, date, modello, provider e messaggi integrali);
- **TXT**: testo semplice con `[Tu]` / `[AI]`;
- **PDF**: documento impaginato (richiede `reportlab`).

## 19.2 Batch Export — `### 🗂️ Batch Export`

Esporta **tutte** le conversazioni salvate in un colpo solo: scegli il **Formato batch** e premi **📦 Genera ZIP** → **💾 Download ZIP** (`conversations_batch_{data}.zip`).

---

# Capitolo 20 — Privacy: come DeepAiUG protegge i tuoi dati

DeepAiUG applica tre livelli di protezione quando entrano in gioco provider cloud:

## 20.1 Blocco totale: Knowledge Base + cloud

Con la **Knowledge Base attiva** il passaggio a un provider cloud è **impedito**: "🔒 Cloud bloccato: Knowledge Base attiva. I tuoi documenti rimangono privati!" e la connessione torna su Local. Analogamente, su cloud l'upload di file è disabilitato.

## 20.2 Conferma esplicita: documenti in memoria

Se hai caricato file in chat e poi passi al cloud, l'interfaccia si blocca sulla pagina **"🔐 Conferma Privacy Richiesta"**, che elenca i file coinvolti e offre tre uscite:

1. **🔄 Reset e usa Cloud** *(consigliato)* — cancella la cronologia e prosegue in sicurezza;
2. **✅ Procedi con Cloud** — disponibile solo dopo aver spuntato "Confermo: i documenti non contenevano dati riservati";
3. **↩️ Torna a Local/Remote**.

Ogni nuovo documento caricato azzera un eventuale consenso precedente.

## 20.3 Protezione delle conversazioni salvate

Le chat che contengono dati locali (allegati, KB, vault) sono marcate con 🔒 quando sei su cloud e **non possono essere caricate** finché non torni in locale/remoto.

## 20.4 Cosa devi comunque sapere (limiti noti in v1.15.1)

- Il toggle **"📚 Usa KB Chat"** non è coperto dal blocco cloud: disattivalo prima di usare il cloud se le chat indicizzate sono riservate.
- "Remote host" è considerato fidato per definizione: assicurati che l'host inserito sia davvero nella tua rete.
- La Mappa Sessione e i bottoni socratici usano il modello corrente: se sei su cloud, anche quelle richieste vanno al provider cloud.

---

# Appendice A — Tabella dei limiti e valori predefiniti

| Parametro | Valore | Regolabile da UI |
|---|---|---|
| Dimensione massima file allegato | 10 MB | No |
| Troncamento testo documento | 50.000 caratteri | No |
| Formati upload | pdf, txt, md, docx, png, jpg, jpeg, gif, webp | No |
| Temperature | 0.7 (0.0–2.0) | Sì |
| Max messaggi in contesto | 50 (10–100) | Sì |
| Chunk size RAG | 1000 caratteri (200–3000) | Sì |
| Chunk overlap RAG | 200 caratteri (0–500) | Sì |
| Documenti per query (top-k) | 5 (1–10) | Sì |
| Modello embedding | `intfloat/multilingual-e5-small` (384 dim) | Solo via env `DEEPAIUG_EMBEDDING_MODEL` |
| Boost rilevanza KB Chat | 1.0 / 1.15 / 1.30 | Indiretto (livello di rilevanza) |
| Soglia nudge Mappa Sessione | 5 domande | No |
| Visibilità mappa (modalità progressiva) | dopo 4 domande | No |
| Minimo domande per generare la mappa | 2 | No |
| Conferma caricamento KB "pesante" | ≥ 50 file | No |
| Batch indicizzazione ChromaDB | 500 chunk | No |
| Timeout `ollama list` / `/api/tags` | 5 s / 10 s | No |
| Pausa tra richieste wiki | 0,5 s | Sì (YAML) |
| Porta web | 8501 (default Streamlit) | Sì (opzioni Streamlit) |

# Appendice B — Risoluzione dei problemi

| Sintomo | Causa probabile | Rimedio |
|---|---|---|
| "❌ Seleziona un modello!" | Nessun modello rilevato/scelto | Premere 🔄 Aggiorna; verificare `ollama list`; installare un modello (`ollama pull llama3.2:3b`) |
| Nessun modello locale trovato | Ollama spento | Avviare Ollama (`ollama serve`); il launcher lo fa automaticamente |
| "⚠️ Nessun server configurato in remote_servers.yaml" | YAML mancante/vuoto | Il sistemista deve configurare `remote_servers.yaml` (Cap. 6.3) |
| "🔒 Cloud bloccato con Knowledge Base attiva!" | Comportamento voluto | Disattivare la KB o restare su Local/Remote |
| "🔤 Embedding: ChromaDB default (MiniLM-L6, EN)" | `sentence-transformers` non installato o download fallito | Installare la dipendenza / verificare la connessione al primo avvio; qualità in italiano ridotta nel frattempo |
| KB svuotata dopo aggiornamento a v1.15.x | Migrazione automatica per cambio modello embedding | Ri-indicizzare le sorgenti e premere 🔄 Aggiorna KB Chat |
| "⚠️ Storage: Memoria (temporaneo)" | ChromaDB non installato | Installare `chromadb`; senza, l'indice si perde alla chiusura |
| CPU al 100% durante l'indicizzazione | Normale: embedding in CPU | Attendere; non chiudere l'app |
| Le immagini allegate vengono ignorate | Modello non-Vision, o limite noto v1.15.1 (Vision API non integrata) | Usare il testo dei documenti; le immagini non raggiungono ancora il modello |
| "❌ Pacchetto `mwclient` non installato" | Dipendenza wiki mancante | `pip install mwclient` (o `dokuwiki`) nel venv |
| PDF non esportabile | `reportlab` mancante | `pip install reportlab` nel venv |
| Verifica generale dell'installazione | — | Eseguire `installer/check_deepaiug.sh` |

# Appendice C — Glossario

| Termine | Definizione |
|---|---|
| **Ollama** | Runtime open source per eseguire LLM in locale; espone un'API compatibile OpenAI sulla porta 11434 |
| **RAG** (Retrieval-Augmented Generation) | Tecnica che recupera passaggi pertinenti dai tuoi documenti e li fornisce al modello come contesto |
| **Chunk** | Frammento di documento (qui: ~1000 caratteri) indicizzato singolarmente |
| **Embedding** | Rappresentazione numerica del testo che consente la ricerca per somiglianza di significato |
| **ChromaDB** | Database vettoriale usato per memorizzare gli embedding su disco |
| **Vault** | Raccolta di note personali (Obsidian, LogSeq, export Notion) indicizzabile come KB |
| **KB Chat / KB epistemica** | Le conversazioni salvate e marcate come rilevanti, usate come memoria consultabile |
| **Bottoni socratici** | I 5 strumenti di analisi critica (Alternative, Assunzioni, Limiti, Confuta, Rifletti) |
| **Frame / sovrascopo** | La cornice interpretativa implicita costruita dalle domande di una sessione; resa visibile dalla Mappa Sessione |
| **Nudge** | L'invito non invasivo che propone la Mappa Sessione dopo 5 domande |
| **Top-k** | Numero di passaggi recuperati dalla KB per ogni domanda (default 5) |
| **System Prompt** | Istruzioni permanenti date al modello all'inizio di ogni scambio |
| **Temperature** | Parametro che regola la variabilità delle risposte del modello |

---

*Manuale generato dall'analisi del codice sorgente DeepAiUG v1.15.1 — 2026-07-12. Nessun file di codice è stato modificato.*
