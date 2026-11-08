# MANUALE DeepAiUG

**DeepAiUG Streamlit LLM Interface — Manuale di installazione, configurazione e utilizzo**

| | |
|---|---|
| **Prodotto** | DeepAiUG Chat 🧠 |
| **Versione documentata** | v1.16.0 |
| **Data manuale** | 2026-11-08 |
| **Repository** | https://github.com/EnzoGitHub27/datapizza-streamlit-interface |
| **Licenza** | MIT |
| **Autore progetto** | Vincenzo Iodice (EnzoGitHub27) — community DeepAiUG |

> Questo manuale è stato scritto e rivisto contro il codice della versione 1.16.0, l'8 novembre 2026. Documenta esclusivamente le funzionalità effettivamente presenti nella versione 1.16.0; le funzionalità pianificate per v2.0.0 (Semantic Layer, Knowledge Graph, Docker, API REST, journaling riflessivo) **non** sono trattate perché non ancora implementate.

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
- [Capitolo 21 — L'ambiente ibrido: rizzo-pii e Annona (v1.16.0)](#capitolo-21--lambiente-ibrido-rizzo-pii-e-annona-v1160)

**Appendici**
- [Appendice A — Tabella dei limiti e valori predefiniti](#appendice-a--tabella-dei-limiti-e-valori-predefiniti)
- [Appendice B — Risoluzione dei problemi](#appendice-b--risoluzione-dei-problemi)
- [Appendice C — Glossario](#appendice-c--glossario)

---

# Capitolo 1 — Che cos'è DeepAiUG

DeepAiUG è un'interfaccia web (basata su Streamlit) per dialogare con modelli linguistici (LLM), progettata secondo due principi fondanti:

1. **Privacy-first.** Il funzionamento predefinito è completamente locale: il modello gira su Ollama sulla macchina dell'utente o su un server della rete locale. L'uso di provider cloud (OpenAI, Anthropic, Google) è possibile ma sorvegliato: con la Knowledge Base attiva l'invio al cloud è bloccato; con documenti caricati nella sessione è richiesta una conferma esplicita; in altri casi (per esempio una chat caricata che contiene dati locali) c'è solo un avviso — vedi Capitolo 20.
2. **Approccio socratico.** L'applicazione non si limita a rispondere: offre strumenti ("bottoni socratici", "Mappa Sessione") che restituiscono attrito cognitivo, aiutando l'utente a esaminare assunzioni, limiti e prospettive alternative invece di delegare il giudizio all'AI. Questi strumenti sono sempre disattivabili: l'attrito ha valore solo se scelto (si veda `PHILOSOPHY.md` nel repository).

**Funzionalità principali in sintesi:**

- Chat multi-turno con risposte in streaming, verso tre tipi di backend: **Ollama locale**, **server remoto** (API compatibile OpenAI, tipicamente Ollama in LAN), **provider cloud** (OpenAI, Anthropic, Google Gemini, endpoint custom). Anthropic e Google richiedono pacchetti aggiuntivi che gli installer non installano (vedi 2.3).
- **Upload di file** in chat (PDF, TXT, MD, DOCX, immagini) con estrazione del testo.
- **Knowledge Base documentale (RAG)**: indicizzazione di cartelle locali, wiki MediaWiki/DokuWiki, vault Obsidian/LogSeq/export Notion, con ricerca semantica multilingua (ChromaDB + embedding `intfloat/multilingual-e5-small`).
- **KB Chat epistemica**: le conversazioni salvate possono essere marcate per rilevanza e reindicizzate come memoria consultabile nelle risposte future.
- **Funzioni socratiche**: 5 bottoni di analisi critica sotto ogni risposta, storico delle esplorazioni, tre livelli di profondità.
- **Mappa Sessione**: analisi su richiesta della "cornice implicita" costruita dalle domande della sessione.
- **Persistenza e export**: salvataggio automatico delle conversazioni, esportazione in Markdown, JSON, TXT, PDF e ZIP batch.
- **Branding personalizzabile** (titolo, icona, banner, tema "Matrix" con pioggia di caratteri).

**Nota sui nomi:** la cartella/repository si chiama `datapizza-streamlit-interface` (usa il framework `datapizza-ai` per i client LLM), ma il prodotto si chiama **DeepAiUG** e l'installer lo colloca in `~/DeepAiUG`. La versione autorevole è quella dichiarata in `config/constants.py` (`VERSION = "1.16.0"`); dalla 1.16.0 anche `pyproject.toml` dice `1.16.0`, ma resta solo metadato del pacchetto Poetry.

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
- Quando Python manca: su **Windows** l'installer scarica Python 3.12.10; su **macOS** usa Homebrew (`python@3.12`) o scarica `python-3.12.10-macos11.pkg`; su **Linux** installa il `python3` della distribuzione (apt/dnf/pacman), qualunque versione sia. Su Windows un Python già presente nel PATH viene usato senza controllarne la versione.
- **Poetry non è un percorso supportato**: `pyproject.toml` (che richiede `python >= 3.12, < 3.14`) non elenca tutte le dipendenze (mancano tra gli altri chromadb, sentence-transformers, pypdf, mwclient, dokuwiki, reportlab, python-docx, Pillow) e ha pin diversi da `requirements.txt`. Usare `requirements.txt`, come fanno gli installer.

## 2.3 Dipendenze principali (`requirements.txt`)

Dalla v1.15.2 il `requirements.txt` **pinna tutte le dipendenze** (`==`) per build riproducibili (fix M4 dell'audit di sicurezza). Il requisito minimo di compatibilità resta `streamlit>=1.28.0`, ma la v1.15.2 pinna `streamlit==1.53.1`. Nella stessa versione il deprecato `PyPDF2` è stato sostituito dal fork manutenuto `pypdf`.

| Area | Pacchetti (pin v1.15.2) |
|---|---|
| Core | `streamlit==1.53.1`, `python-dotenv==1.2.2`, `pyyaml==6.0.3` |
| Framework LLM | `datapizza-ai==0.0.9` (con `datapizza-ai-core`, `datapizza-ai-embedders-openai`, `datapizza-ai-vectorstores-qdrant`, `datapizza-ai-clients-openai`) e `datapizza-ai-clients-openai-like==0.0.11`. Gli installer fanno prima `pip install datapizza-ai` **senza versione** (gli updater con `--upgrade`), poi `requirements.txt` riporta i pin |
| RAG | `chromadb==1.4.1`, `sentence-transformers==5.4.1`, `beautifulsoup4==4.15.0`, `pypdf==6.14.2` |
| Wiki | `mwclient==0.11.0`, `dokuwiki==1.3.3` |
| Export | `reportlab==4.4.9` |
| Upload file | `python-docx==1.2.0`, `Pillow==12.3.0` |

⚠️ **Anthropic e Google Gemini non funzionano con la sola installazione standard**: usano i client `datapizza-ai-clients-anthropic` e `datapizza-ai-clients-google`, che non sono in `requirements.txt` e non vengono installati dagli installer. Senza di essi, scegliendo quei provider la domanda resta in chat segnata «⚠️ **Non inviata** — ImportError: …». Per usarli: `pip install datapizza-ai-clients-anthropic datapizza-ai-clients-google` dentro il venv (`~/DeepAiUG/venv`). OpenAI e gli endpoint compatibili OpenAI funzionano senza pacchetti aggiuntivi.

⚠️ **Ordine di installazione critico**: `datapizza-ai` va installato **prima** di `requirements.txt`, perché `datapizza-ai-clients-openai-like` ne dipende. Gli installer ufficiali rispettano già quest'ordine.

⚠️ **Spazio disco**: `sentence-transformers` trascina `torch` come dipendenza (≈ 888 MB su Linux, ≈ 250 MB su Mac). Al primo utilizzo del RAG viene inoltre scaricato da HuggingFace il modello di embedding `intfloat/multilingual-e5-small` (≈ 118 MB, cache in `~/.cache/huggingface/hub/`); dalla 1.16.0, se è già sul disco, si carica senza nessuna richiesta di rete (Cap. 9.3).

## 2.4 Ollama e hardware

- **Ollama** è il motore LLM locale. Gli installer lo installano automaticamente (Linux: `curl -fsSL https://ollama.com/install.sh | sh`; macOS: Homebrew, script o zip in `/Applications/`).
- **GPU: non richiesta.** L'embedding RAG gira dentro il processo Streamlit: sulla GPU solo se la build di torch installata la supporta, altrimenti in CPU (dalla v1.15.4; prima, su schede come la MX250, l'indicizzazione falliva con «no kernel image»). `DEEPAIUG_EMBEDDINGS_DEVICE=cpu` o `cuda` forza la scelta; il device scelto compare una volta nel terminale («🧮 Embedding … su cpu: …»).
- Modello LLM suggerito dagli installer in base alla RAM:

| RAM | Modello suggerito | Alternative |
|---|---|---|
| < 8 GB | `phi3:mini` | `tinyllama` |
| 8–15 GB | `llama3.2:3b` | `phi3`, `phi3:mini` |
| 16–31 GB | `mistral:7b` | `llama3.2:3b`, `gemma2:9b` |
| ≥ 32 GB | `llama3.1:8b` | `mistral:7b`, `gemma2:9b` |

---

# Capitolo 3 — Installazione

Gli script si trovano nella cartella `installer/`. I file `install.sh` e `install.bat` nella root sono solo un rimando informativo.

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

## 3.3 Installazione su Windows 11 — `installer/INSTALLA_DeepAiUG.bat`

- Tasto destro su `INSTALLA_DeepAiUG.bat` → **«Esegui come amministratore»**: lo script verifica i permessi (`net session`) e si ferma se mancano.
- Installa in `%USERPROFILE%\DeepAiUG`, con log in `%USERPROFILE%\DeepAiUG_install_log.txt`.
- Se mancano, scarica **Python 3.12.10** (python.org) e **Ollama** (`OllamaSetup.exe`).
- Crea il launcher `%USERPROFILE%\DeepAiUG\DeepAiUG.bat` e l'**icona DeepAiUG sul Desktop** (`DeepAiUG.lnk`) per l'avvio.
- Aggiornamento: `installer/AGGIORNA_DeepAiUG.bat`; diagnostica: `installer/CHECK_DeepAiUG.bat` (vedi anche `installer/INIZIA-QUI.txt`).

## 3.4 Cosa fare dopo l'installazione

1. Avviare dal menu applicazioni (Linux), dal `.app`/`.command` (macOS) o dall'icona sul Desktop (Windows): il browser si apre in 20–30 secondi.
2. (Facoltativo) Personalizzare i file YAML di configurazione — vedi Capitolo 6.
3. (Facoltativo) Configurare le chiavi API cloud — vedi Capitolo 7.

---

# Capitolo 4 — Aggiornamento e diagnostica

## 4.1 Aggiornamento — `aggiorna_deepaiug_linux.sh` / `aggiorna_deepaiug_mac.sh` / `AGGIORNA_DeepAiUG.bat`

Gli script di aggiornamento (log in `~/DeepAiUG_update_log.txt`; gli script Linux e Mac sono uguali salvo i testi; quello Windows va lanciato come amministratore):

1. Verificano la presenza di `~/DeepAiUG` e del virtualenv.
2. Leggono la versione installata da `config/constants.py`.
3. **Eseguono un backup di `conversations/`** in `~/DeepAiUG_backup_conversations` (Windows: `%USERPROFILE%\DeepAiUG_backup_conversations`). È una cartella unica, senza data: a ogni aggiornamento i file con lo stesso nome vengono sovrascritti.
4. Scaricano ed estraggono il nuovo ZIP da GitHub.
5. **Aggiornano solo il codice**: `app.py`, `requirements.txt`, `pyproject.toml` e le cartelle `config/`, `core/`, `ui/`, `rag/`, `export/`, `installer/`, `.streamlit/`. Copiano soltanto: i file tolti a monte restano sul disco. **Non** copiano documentazione e test: `docs/` (compresa `docs/SPEC_v1.16.0_hybrid.md`), `tests/`, `examples/`, `README.md`, `MANUALE_DeepAiUG.md`, `CHANGELOG.md`, `NOTICE`, `LICENSE`, `requirements-dev.txt`. Per leggerli, usa il repository su GitHub.
6. **Preservano** (non toccano mai): `conversations/`, `secrets/`, `.env`, `branding.yaml`, `cloud_models.yaml`, `remote_servers.yaml`, `security_settings.yaml`, `wiki_sources.yaml`. ⚠️ `.streamlit/` invece **viene sovrascritta**: un tema personalizzato o una sezione `[server]` aggiunta a `.streamlit/config.toml` si perdono a ogni aggiornamento (meglio passare le opzioni server sulla riga di comando, Cap. 5.2).
7. Aggiornano `datapizza-ai` e le dipendenze (`pip install -r requirements.txt --upgrade --prefer-binary`, output visibile).
8. Mostrano un riepilogo con vecchia e nuova versione.

⚠️ **Aggiornando alla 1.16.0 da una versione precedente: la sezione `hybrid:` non c'è.** Poiché `security_settings.yaml` viene preservato, chi aggiorna tiene il proprio file, senza la sezione dell'ambiente ibrido. È giusto così: senza sezione l'ibrido resta **spento** e l'app si comporta come la 1.15.4 (salvo la regola della destinazione reale, Cap. 21.4). Per accenderlo:

1. apri `~/DeepAiUG/security_settings.yaml` con un editor di testo;
2. aggiungi in fondo il blocco `hybrid:` del Capitolo 21.3 (lo stesso del file `security_settings.yaml` nel repository su GitHub), rispettando i rientri di due spazi;
3. installa e avvia rizzo-pii (ed eventualmente Annona) come nel Capitolo 21.2, poi metti `enabled: true` dove serve;
4. riavvia DeepAiUG. Se il blocco è scritto male, l'app non lo ignora: blocca gli invii verso fuori casa con «🛡️ Configurazione ibrida non valida, messaggio non inviato: …» finché non lo correggi.

⚠️ **Dopo l'aggiornamento a v1.15.0 o successive** da una versione precedente: il modello di embedding è cambiato, quindi le collection ChromaDB esistenti vengono automaticamente svuotate al primo avvio (migration check). Gli utenti devono **ri-indicizzare** le proprie sorgenti (cartelle/wiki/vault) e premere "🔄 Aggiorna KB Chat". Il primo utilizzo scarica il nuovo modello (~118 MB).

## 4.2 Diagnostica — `check_deepaiug.sh`

Script unico per Linux e macOS (rileva l'OS con `uname -s`); su Windows si usa `installer/CHECK_DeepAiUG.bat`. Verifica: Python ≥ 3.10, presenza di Ollama (nel PATH o in `/Applications/Ollama.app`), esistenza di `~/DeepAiUG`, del venv e di `requirements.txt`; elenca i modelli con `ollama list` e mostra le ultime 20 righe del log di installazione. Al termine stampa il conteggio errori e l'esito.

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
- `.streamlit/config.toml` contiene **solo il tema** ("Matrix": `primaryColor = "#00d4aa"`, sfondo `#020c06`, testo `#c8ffd4`, font monospace). **Non** contiene alcuna sezione `[server]`: valgono i default di Streamlit, incluso il limite upload widget di **200 MB**: è il limite reale per file. Il valore `MAX_FILE_SIZE_MB = 10` di `config/constants.py` compare solo nel testo d'aiuto del widget e **non viene controllato** dal codice.
- Per cambiare porta o binding si possono usare le normali opzioni Streamlit, ad es. `streamlit run app.py --server.port 8502 --server.address 127.0.0.1`.

⚠️ **L'applicazione non ha autenticazione né isolamento per-utente**: chiunque raggiunga la porta 8501 è "l'utente". Non esporre la porta su reti non fidate senza un reverse proxy con autenticazione (vedi Capitolo 10).

---

# Capitolo 6 — File di configurazione

Tutti i file YAML risiedono nella **root del progetto** (per tutti tranne `branding.yaml` è accettato anche `config/<nome>.yaml`); sono letti con `yaml.safe_load`. Se un file manca o è malformato si usano i default, con un avviso nel terminale (es. «⚠️ Errore lettura security settings: …»). **Eccezione:** la sezione `hybrid:` di `security_settings.yaml` non ricade mai in silenzio sui default: un errore blocca gli invii verso fuori casa (Cap. 21.3). Nessuno di questi file viene sovrascritto dagli script di aggiornamento.

## 6.1 `branding.yaml` — personalizzazione dell'aspetto

```yaml
app:
  title: "DeepAiUG Chat"     # titolo dell'app (default)
  icon: "🧠"                  # icona (default)
  subtitle: ""                # sottotitolo; vuoto = nascosto
news_banner:
  enabled: true               # banner novità in alto
  # text: "..."               # testo personalizzato (commentato = default di versione)
  # version: "..."            # se assente vale VERSION di config/constants.py
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
    icon: "🟢"
    base_url: "https://api.openai.com/v1"
    models:
      - {id: "gpt-4o", name: "GPT-4o"}
      - {id: "gpt-4o-mini", name: "GPT-4o Mini"}
      - {id: "o3-mini", name: "o3-mini"}
    default_model: "gpt-4o-mini"
  anthropic:
    name: "Anthropic (Claude)"
    icon: "🟣"
    base_url: "https://api.anthropic.com/v1"
    models: [...]             # claude-sonnet-4-5-20250929, claude-haiku-4-5-20251001
    default_model: "claude-sonnet-4-5-20250929"
  google:
    name: "Google Gemini"
    icon: "🔵"
    base_url: "https://generativelanguage.googleapis.com/v1beta/openai"
    models: [...]             # gemini-2.0-flash, gemini-2.5-pro-preview-06-05
    default_model: "gemini-2.0-flash"
  custom:
    name: "Custom"
    icon: "⚙️"
    base_url: ""              # da scrivere qui: la UI non ha un campo Base URL
    models: []
    default_model: ""
```

Regole da sapere:

- **Il client si sceglie dal `name`**: solo `"OpenAI"`, `"Anthropic (Claude)"` e `"Google Gemini"`, scritti esattamente così, usano i client nativi, e per loro il `base_url` del file **non conta**. Un provider rinominato o aggiunto (es. `mistral`) passa dal client compatibile OpenAI con il `base_url` scritto qui.
- **La chiave di un provider aggiunto** si legge da `<ID>_API_KEY` (id in maiuscolo: `mistral` → `MISTRAL_API_KEY`) o da `secrets/<id>_key.txt`.
- ⚠️ Per **Custom** la UI non ha un campo Base URL: vale il `base_url` scritto qui dal sistemista. **Nel file fornito è vuoto**, e un URL vuoto conta come destinazione non verificabile, cioè «fuori casa»: finché il sistemista non lo compila, Custom non è utilizzabile.

Se il file manca, la UI usa i provider hardcoded in `config/constants.py` (OpenAI → `gpt-4o-mini`, Anthropic → `claude-sonnet-4-20250514`, Google → `gemini-1.5-pro`, Custom).

## 6.3 `remote_servers.yaml` — server Ollama remoti

```yaml
mode: "custom_allowed"        # "fixed" | "selectable" | "custom_allowed"
default_server: "proxmox_p6000"
servers:
  proxmox_p6000:
    name: "Proxmox P6000 24GB"
    icon: "🚀"                # default nel codice: 🖥️
    host: "192.168.1.10"      # default: localhost
    port: 11434               # default: 11434
    description: "..."
  dopey:
    name: "Dopey 8GB"
    icon: "🤖"
    host: "192.168.1.151"
    port: 11434
settings:
  connection_timeout: 10      # letto ma senza effetto: il timeout è fisso a 10 s
  show_refresh_button: true   # mostra "🔄 Aggiorna modelli"
```

Significato di `mode`:
- `fixed` — l'utente usa solo il `default_server`, nessuna scelta;
- `selectable` — scelta dalla lista `servers`;
- `custom_allowed` — lista + possibilità di inserire un host manualmente (default se il file è assente).

## 6.4 `security_settings.yaml` — impostazioni di sicurezza

```yaml
cloud_api_keys:
  show_saved_keys: false      # default SICURO: chiavi salvate nascoste in UI
  hidden_message: "✅ Key salvata (nascosta per sicurezza)"
  visible_message: "✅ Key salvata (visibile)"
hybrid:                       # v1.16.0, tutto spento: vedi il Capitolo 21.3
  ...
# remote_servers:             # placeholder NON implementato
#   require_authentication: ...
#   log_connections: ...
```

`show_saved_keys` decide se la chiave salvata compare nella UI (in un campo password, mascherata ma rivelabile con l'occhio) o resta nascosta. La sezione `hybrid:` (dalla 1.16.0, spenta per default) è descritta nel Capitolo 21.3; chi aggiorna da una versione precedente non ce l'ha (Cap. 4.1). La sezione `remote_servers` è un segnaposto commentato senza effetto.

## 6.5 `wiki_sources.yaml` — sorgenti wiki e documentali

Definisce le sorgenti della Knowledge Base offerte all'utente. Struttura di primo livello:

```yaml
mode: "selectable"            # fixed | selectable | custom (Cap. 14.2); senza chiave: selectable; senza file: custom
default_source: "wikipedia_it"
sources:                      # (retrocompatibile con la vecchia chiave "wikis")
  <id>:
    name: "..."
    icon: "🌐"
    description: "..."
    type: mediawiki | dokuwiki | local
    url: ...                  # wiki; per type: local la chiave è folder_path
    api_path: "/w/api.php"    # MediaWiki
    namespaces: [0]
    max_pages: 30
    timeout: 30
    exclude_categories: [...] # o exclude_namespaces per DokuWiki
    requires_auth: false
    password: "${DOKUWIKI_PASS}"  # credenziali via variabili d'ambiente ${VAR}
global_settings:
  cache_dir: "wiki_cache"     # relativo alla cartella da cui si avvia l'app
  cache_ttl_hours: 24         # letto ma senza effetto
  request_delay: 0.5          # pausa tra richieste HTTP (rispetto dei server)
  batch_size: 50
  strip_wiki_markup: true
  include_metadata: true      # letto ma senza effetto
  user_agent: "DatapizzaBot/1.4.1 (...)"
```

Il file di esempio contiene 9 sorgenti: 2 MediaWiki interne/di test, 2 DokuWiki, 1 cartella locale, e 4 wiki pubbliche di prova (Wikipedia IT/EN, Wikivoyage IT, Wikibooks IT). Le credenziali (`username`, `password`, `api_key`, `token`) possono essere espresse come `${NOME_VARIABILE}` e vengono espanse dalle variabili d'ambiente; il valore deve essere **tutto** `${…}` (niente testo prima o dopo).

## 6.6 Variabili d'ambiente riconosciute

| Variabile | Effetto |
|---|---|
| `OPENAI_API_KEY` | Chiave OpenAI |
| `ANTHROPIC_API_KEY` | Chiave Anthropic |
| `GOOGLE_API_KEY` | Chiave Google Gemini |
| `CUSTOM_API_KEY` | Chiave per provider custom |
| `<ID>_API_KEY` | Chiave di un provider aggiunto in `cloud_models.yaml` (es. `MISTRAL_API_KEY`) |
| `DEEPAIUG_EMBEDDING_MODEL` | Override del modello di embedding RAG (es. `intfloat/multilingual-e5-base`) |
| `DEEPAIUG_EMBEDDINGS_DEVICE` | `cpu` o `cuda`: forza il device degli embedding (Cap. 2.4) |
| `${VAR}` nei YAML wiki | Credenziali wiki espanse a runtime |

È supportato un file **`.env`** nella root (caricato con `python-dotenv`), ma viene letto **solo quando la sidebar cerca una chiave cloud**: vale per le chiavi API. Le variabili `DEEPAIUG_*` e le `${VAR}` delle wiki vanno impostate nell'ambiente prima di avviare l'app (per esempio nel launcher), non in `.env`.

---

# Capitolo 7 — Gestione delle chiavi API

Le chiavi dei provider cloud **non** stanno in `cloud_models.yaml`. Sono lette in quest'ordine di precedenza:

1. **Variabile d'ambiente** (o `.env` nella root): `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `CUSTOM_API_KEY`.
2. **File secrets**: `secrets/<provider>_key.txt` (es. `secrets/openai_key.txt`, `secrets/anthropic_key.txt`).
3. **Interfaccia web**: l'utente inserisce la chiave nella sidebar; il bottone "💾 Salva" la scrive in `secrets/<provider>_key.txt` (la cartella viene creata al bisogno).

⚠️ Se la variabile d'ambiente è impostata, vince sempre: una chiave salvata dalla UI viene scritta nel file ma **non usata**, anche se la UI conferma il salvataggio. E la UI mostra «✅ Key salvata (…)» anche quando la chiave viene dall'ambiente.

**Precauzioni per l'amministratore:**

- `secrets/` è esclusa da git (`.gitignore`), ma i file sono salvati **in chiaro**. Dalla v1.15.2 le chiavi salvate dalla UI hanno permessi **0600** (solo il proprietario); controllare i permessi solo dei file creati a mano (`chmod 600 secrets/*.txt`) e preferire variabili d'ambiente o `.env` con permessi ristretti.
- La cartella `secrets/` viene creata con i permessi di default del sistema: restringila a mano (`chmod 700 secrets`) su macchine condivise.
- La visualizzazione delle chiavi salvate nella UI è disattivata di default (`show_saved_keys: false` in `security_settings.yaml`); lasciarla così salvo necessità.
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
| `wiki_cache/` | File `sync_<hash dell'URL>.json` / `sync_doku_<hash>.json`: **solo statistiche** dell'ultimo sync wiki (pagine totali/caricate, URL, timestamp) — non contengono le pagine | |
| `secrets/` | Chiavi API in file di testo | In chiaro — vedi Cap. 7 |
| `.env` | Variabili d'ambiente opzionali | |
| `~/.cache/huggingface/hub/` | Cache del modello di embedding scaricato | Fuori dal progetto |
| `~/DeepAiUG_install_log.txt`, `~/DeepAiUG_update_log.txt` | Log di installazione e aggiornamento | Fuori dal progetto |
| `~/DeepAiUG_backup_conversations/` | Backup delle conversazioni fatto dall'updater | Fuori dal progetto, sovrascritto a ogni aggiornamento |
| Launcher | `avvia_deepaiug.sh` + `~/.local/share/applications/deepaiug.desktop` (Linux), `DeepAiUG.command`/`DeepAiUG.app` (Mac), `DeepAiUG.bat` + `DeepAiUG.lnk` sul Desktop (Windows) | Creati dall'installer |

**Contenuto di un file conversazione**: `conversation_id`, `created_at`, `last_updated`, `model` e `provider` (dell'ultima risposta; `models_used` se hanno risposto più modelli), i messaggi completi, `stats` (`total_messages`, `tokens_estimate`), le impostazioni della Knowledge Base usata (`knowledge_base`), lo storico delle esplorazioni socratiche, i metadati KB (`kb_metadata`: `includi_in_kb`, `rilevanza`, `tipo`, `note`) e il flag `vault_used` (true se la chat è stata condotta con un vault attivo). Dalla 1.16.0, se è stato usato rizzo-pii, anche `pii_guard` e, nei messaggi, `pii_removed`: **solo il numero** dei dati tolti, mai i valori.

**L'ambiente ibrido non crea file**: la tabella segnaposto → valore vive solo in memoria (Cap. 21.5); il registro di Annona è del servizio Annona, che DeepAiUG legge via HTTP. Su disco restano solo la sezione `hybrid:` di `security_settings.yaml` e i conteggi nel JSON.

---

# Capitolo 9 — Il motore RAG in dettaglio

Riferimento tecnico per il sistemista; l'uso dal punto di vista dell'utente è nei Capitoli 14–15.

## 9.1 Pipeline

`Adapter (sorgente) → Chunker → Embedding → ChromaDB → Retrieval top-k → contesto iniettato nel prompt`

L'orchestrazione è in `rag/manager.py` (`KnowledgeBaseManager`). Ogni indicizzazione **svuota e ricostruisce** l'unica collection della KB documentale: una sorgente nuova **sostituisce** la precedente (non si possono combinare, per esempio, una wiki e un vault) e non esiste aggiornamento incrementale.

## 9.2 Chunking

- Unità: **caratteri** (non token). Default: **chunk 1000, overlap 200** (regolabili da UI: 200–3000 a passi di 100 / 0–500 a passi di 50).
- Split gerarchico sui separatori in ordine di priorità: intestazioni Markdown (`\n## `, `\n### `), sezioni (`\n\n\n`), paragrafi (`\n\n`), righe, frasi (`. `, `! `, `? `, `; `), virgole, spazi. I chunk non vengono mai tagliati prima di 1/3 della dimensione target.
- ⚠️ Gli slider permettono un overlap uguale o maggiore della dimensione del chunk (es. chunk 200, overlap 500): in quel caso i chunk diventano moltissimi e quasi identici. Tieni l'overlap ben sotto la dimensione del chunk.
- La **KB Chat** ha un suo chunker fisso (1000/200, separatori: turni della conversazione, paragrafi, righe, frasi, spazi), non regolabile dalla UI.

## 9.3 Embedding

- Modello di default: **`intfloat/multilingual-e5-small`** (384 dimensioni, multilingua, ~118 MB, CPU-friendly), via `sentence-transformers`, vettori normalizzati, con prefissi e5 (`passage:` per i documenti, `query:` per le query). Le collection usano la distanza di default di ChromaDB (L2): con vettori normalizzati l'ordine dei risultati è lo stesso del coseno.
- Override con `DEEPAIUG_EMBEDDING_MODEL`; alternative note: `intfloat/multilingual-e5-base` (768 dim), `intfloat/multilingual-e5-large` (1024 dim), `paraphrase-multilingual-MiniLM-L12-v2` (384 dim).
- **Fallback**: se `sentence-transformers` non è disponibile, il sistema non si blocca: ChromaDB usa la propria embedding function di default (`all-MiniLM-L6-v2`, orientata all'inglese, qualità inferiore sull'italiano). La UI lo segnala ("🔤 Embedding: ChromaDB default (MiniLM-L6, EN)").
- **Migrazione automatica**: ogni collection (KB documentale e KB Chat) memorizza il tag del modello di embedding; se al riavvio il tag non coincide (o è assente, caso pre-1.15.0), la collection viene svuotata e va ri-indicizzata manualmente. ⚠️ Se il modello e5 non si carica (anche per un problema passeggero), il tag diventa quello del fallback (`chromadb_default`) e lo svuotamento scatta lo stesso: vedi Appendice B.
- **Rete** (dalla 1.16.0): il modello si scarica da `huggingface.co` solo al primo uso, con una riga nel terminale («🌐 … primo uso, lo scarico da huggingface.co»); se è già nella cache sul disco si carica senza nessuna richiesta di rete. Con la cache incompleta lo riscarica, e lo dice.
- Gli embedding **non usano Ollama**: girano nel processo Streamlit, di solito in CPU (CPU al 100% durante l'indicizzazione è normale); la GPU solo se torch la supporta (vedi §2.4).

## 9.4 Vector store e retrieval

- **ChromaDB persistente** su disco (vedi Cap. 8); fallback in memoria con ricerca keyword se ChromaDB non è installato.
- Indicizzazione in batch da **500** chunk.
- Retrieval: **top-k = 5** di default (regolabile 1–10 da UI, slider visibile solo con la KB documentale attiva e indicizzata). **Non esistono soglie di similarità né reranker**: vengono restituiti sempre i k risultati più vicini.
- KB Chat: stesso top-k, retrieval con **boost per rilevanza** (distanza divisa per 1.0/1.15/1.30 per rilevanza bassa/media/alta). Senza filtro si prendono i k risultati più vicini e il boost li **riordina** soltanto; con il **filtro per tipo** si prendono 3×k risultati e si filtrano dopo, quindi possono uscirne meno di k (anche nessuno).

## 9.5 Client LLM e scoperta modelli

- Client costruiti con la libreria `datapizza` (`ClientFactory`): provider nativi per OpenAI/Anthropic/Google, `OpenAILikeClient` per Ollama locale, host remoti ed endpoint custom.
- Modelli locali: rilevati con `ollama list` (subprocess, timeout 5 s). Modelli remoti: endpoint HTTP `/api/tags` del server Ollama (timeout 10 s). In caso di errore la lista risulta semplicemente vuota.

## 9.6 Sincronizzazione wiki

- Adapter MediaWiki (`mwclient`) e DokuWiki; pausa di **0,5 s** tra le richieste (`request_delay`), timeout 30 s, batch da 50, strip del markup wiki.
- **User-agent**: solo l'adapter MediaWiki ne imposta uno (`DeepAiUGBot/<versione>`); per le sorgenti di `wiki_sources.yaml` vale quello di `global_settings.user_agent`, che nel file fornito è ancora `DatapizzaBot/1.4.1 (...)`. L'adapter DokuWiki non ne imposta.
- A fine sync viene scritto un file di statistiche in `wiki_cache/` (`sync_<id>.json` per MediaWiki, `sync_doku_<id>.json` per DokuWiki): non è una cache dei contenuti.

---

# Capitolo 10 — Sicurezza e raccomandazioni operative

Sintesi dell'audit statico `SECURITY_AUDIT.md` (v1.15.1, 2026-07-07): **nessun RCE** (assenti `pickle`/`eval`/`exec`/`os.system`; YAML sempre con `safe_load`; unico subprocess `ollama list` senza shell; upload mai scritti su disco; export senza zip-slip; nessuna chiave hardcoded). Rilevati 0 Critical, 4 High, 4 Medium, 4 Low. **La v1.15.2 corregge i finding H1–H3 e M1–M4** (blocco endpoint metadati cloud, blocco cloud esteso a KB Chat, banner basati sulla destinazione reale, renderer della chat senza HTML grezzo, chiavi API a permessi 0600, migrazione a `pypdf`, dipendenze pinnate); **H4** (lettura di cartelle indicate dall'utente) è un rischio accettato, vedi il punto 5 (`SECURITY_AUDIT_RESOLUTION.md`).

## 10.1 Modello di minaccia

L'app è pensata per **uso mono-utente locale**. Non ha login: "utente" è chiunque raggiunga la porta Streamlit. In LAN condivisa o esposta a Internet i rischi aumentano sensibilmente.

## 10.2 Raccomandazioni pratiche

1. **Non esporre la porta 8501** fuori dall'host o dalla LAN fidata; per accessi multipli usare un reverse proxy con autenticazione (es. nginx + basic auth/SSO) e binding su `127.0.0.1`.
2. **Chiavi API**: `chmod 600 secrets/*.txt`; preferire `.env`/variabili d'ambiente; `show_saved_keys: false`.
3. **Blocco privacy** (findings H2/H3, corretti in v1.15.2): il blocco verso il cloud copre ora sia la Knowledge Base documentale sia il toggle "Usa KB Chat"; i banner di connessione riflettono la destinazione reale dell'URL (classificatore, Cap. 20.0) e avvisano se un host "Remote"/"Local" risolve a un indirizzo esterno. **Dalla 1.16.0** con KB o KB Chat attiva ogni destinazione «fuori casa» è bloccata, compresi un Remote host su IP pubblico e un URL non risolvibile (Cap. 21.4); senza KB l'host esterno resta usabile, con il banner giallo. Al contrario, un cloud «Custom» su localhost o LAN conta come «in casa». Istruire comunque gli utenti a non puntare host "remote" verso endpoint Internet.
4. **SSRF (H1, mitigato in v1.15.2)**: gli URL (server remoti, wiki, base_url) sono classificati e gli endpoint metadati cloud (`169.254.0.0/16`) sono bloccati; gli altri indirizzi interni restano raggiungibili per design (Ollama locale/LAN). Su host esposti a terzi limitare comunque la rete in uscita.
5. **Percorsi cartelle RAG (H4)**: l'utente può indicizzare qualunque cartella leggibile dal processo; in contesti multi-utente eseguire l'app con un utente di sistema dedicato con permessi minimi.
6. **Dipendenze (M4, corretto in v1.15.2)**: `PyPDF2` (deprecato) è stato sostituito da `pypdf` e le dipendenze sono pinnate (`==`) in `requirements.txt`; mantenere scansioni periodiche (`pip-audit`).
7. Dopo gli aggiornamenti, verificare l'installazione con `installer/check_deepaiug.sh`.

---

# PARTE II — MANUALE UTENTE

# Capitolo 11 — Primi passi: l'interfaccia

## 11.1 Cosa vedi all'avvio

All'apertura del browser (di norma `http://localhost:8501`) trovi:

- **Tema "Matrix"**: sfondo verde scurissimo, testo verde-teal, titoli con effetto glitch e, se abilitata, la "pioggia" di caratteri in sottofondo (personalizzabile o disattivabile dal sistemista via `branding.yaml`).
- **Titolo dinamico** che indica il backend attivo: `🧠 DeepAiUG Chat → Ollama 1.16.0` (locale), `→ Remote` o `→ {provider}` (cloud). Dalla 1.16.0, se il testo va «fuori casa» il titolo aggiunge « ☁️»: `→ OpenAI ☁️`, `→ Remote esterno ☁️` per un Remote host su Internet, `→ Ollama ☁️` per un Base URL locale che punta fuori.
- **Banner novità** («✨ **Novità 1.16.0**: …») con le note della versione; con la Knowledge Base attiva al suo posto c'è il banner della KB (Cap. 14.1).
- **Indicatore di connessione** — dalla v1.15.2 per Local/Remote riflette la **destinazione reale** dell'URL (Cap. 20.0), non l'etichetta della modalità:
  - `🔒 Rete fidata - i dati restano nella tua rete ({host})` (verde: loopback, LAN, Tailscale)
  - `⚠️ Host esterno - i dati escono dalla tua rete verso {host}` (giallo: IP pubblico)
  - `🔒 Connessione bloccata - endpoint metadati cloud` (rosso: 169.254.x, connessione rifiutata)
  - `ℹ️ URL non valido o non risolvibile - verifica l'indirizzo` (informativo)
  - `☁️ Cloud - Dati esterni (KB e Upload disabilitati)` (giallo, per i provider cloud fuori casa)
  - `🔒 Rete fidata - endpoint «Custom» nella tua rete ({host})` (verde, per un provider «Custom» su loopback o LAN)
- **Quattro contatori**: `📝 Messaggi` (totale), `👤 Domande` (tuoi messaggi), `🪙 Token` (stima del solo testo dei messaggi, ~4 caratteri per token: esclusi allegati, contesto KB e system prompt), `🆔 ID` (ultimi 8 caratteri dell'identificativo della conversazione, es. `8_143022`).
- L'**area conversazione** (vuota: "👋 Inizia una conversazione!") e in fondo la sezione **✍️ Messaggio** con allegati e campo di invio.
- A sinistra la **sidebar**, in quest'ordine: expander ⚙️ Configurazione (chiuso), expander 📚 Knowledge Base (Wiki / Vault) (aperto), 💬 Conversazione, 📚 Includi nella Knowledge Base, 🔄 Aggiorna KB Chat, 📚 Gestione Knowledge Base, 🧭 Annona (solo con l'ambiente ibrido), 📚 Usa KB Chat, 📊 Mappa sessione, 🧠 Modalità Socratica con 📋 Esplorazioni socratiche, 📤 Export e 🗂️ Batch Export.

Il bordo superiore della pagina è **verde** quando il testo resta «in casa» e **rosso** quando va «fuori casa» (cloud, ma anche un Remote host su Internet): un colpo d'occhio sulla privacy. Un provider «Custom» su loopback o LAN ha il bordo verde.

## 11.2 Il flusso di base

1. Scegli (o lascia) il backend nella sidebar → ⚙️ Configurazione (default: Ollama locale).
2. Scrivi nel campo "Scrivi il tuo messaggio..." e premi **🚀 Invia**.
3. La risposta appare **in streaming**: prima tre pallini animati ("sta scrivendo"), poi il testo che cresce con un cursore `▌`, con scorrimento automatico della pagina.
4. Sotto ogni risposta trovi i **bottoni socratici** (Capitolo 16), salvo modalità "Veloce"; senza modello selezionato sono disattivati.
5. Con **Auto-save** attivo (default) la conversazione si salva da sola a ogni messaggio.

Ogni messaggio appare in una "bolla": la tua con avatar 👤 e sfondo blu, quella dell'AI con avatar 🤖, il nome del modello e l'orario. Le risposte supportano Markdown completo (tabelle, blocchi di codice).

---

# Capitolo 12 — Connessione e scelta del modello

Sidebar → expander **⚙️ Configurazione** → selettore **"Tipo connessione"** con tre opzioni.

## 12.1 Local (Ollama) — `### 🖥️ Locale`

Modalità predefinita, massima privacy: tutto resta sul tuo computer.

- **Base URL**: default `http://localhost:11434/v1`.
- **🔄 Aggiorna**: rileva i modelli installati in Ollama (accanto compare il conteggio). L'elenco si carica anche da solo all'avvio. ℹ️ Usa `ollama list` sulla macchina dell'app e **ignora il Base URL**: se lo cambi, l'elenco resta quello locale.
- **Modello**: selezione dall'elenco; se non viene trovato nulla puoi digitare il nome (default proposto `llama3.2`).

## 12.2 Remote host — `### 🌐 Remote`

Per usare un server Ollama nella tua rete locale (es. una macchina con GPU).

- A seconda della configurazione del sistemista: server fisso (un riquadro con nome e descrizione, nessuna scelta), elenco di server (**"Server"**), oppure elenco più inserimento manuale (**"✏️ Inserisci manualmente..."** → campo **Host**, es. `http://192.168.1.10:11434/v1`). Senza `remote_servers.yaml` compare direttamente il campo **Host**.
- **API Key (opzionale)** se il server la richiede.
- **🔄 Aggiorna modelli** interroga il server e popola l'elenco **Modello**. Se l'elenco è vuoto, o il bottone è disattivato dal sistemista, **Modello** è un campo di testo (default `llama3.2`). ℹ️ Cambiando server, l'elenco resta quello del server precedente finché non premi di nuovo il bottone.
- ⚠️ Dalla 1.16.0 un Remote host che risolve a un **IP pubblico** si comporta come il cloud (Cap. 21.4).

## 12.3 Cloud provider — `### ☁️ Cloud`

Per usare OpenAI, Anthropic (Claude), Google Gemini o un endpoint custom.

> ⚠️ Anthropic e Google funzionano solo se il sistemista ha installato i loro client nel venv (Capitolo 2.3); altrimenti la domanda resta in chat segnata «⚠️ **Non inviata** — ImportError: …».

- **Provider**: elenco configurato dal sistemista, con icona («🟢 OpenAI», «🟣 Anthropic (Claude)», «🔵 Google Gemini», «⚙️ Custom»), o i quattro predefiniti se `cloud_models.yaml` manca. «Custom» non ha un campo Base URL: funziona solo se il sistemista l'ha scritto nel file (Cap. 6.2).
- **API Key**: se non ne hai una salvata, scrivila nel campo «API Key» e premi **💾 Salva** (compare dopo che hai scritto; verrà ricordata). Se ne esiste una salvata vedrai "✅ Key salvata (nascosta per sicurezza)" e il bottone **🔄 Usa altra key**, che apre il campo «Nuova API Key» con **💾 Salva** / **❌ Annulla**. Se il sistemista rende visibili le chiavi, vedrai «✅ Key salvata (visibile)», il campo «API Key» e **💾 Salva modifiche**. Conta come «salvata» anche una chiave presa dall'ambiente (Cap. 7).
- **Modello**: dall'elenco del provider; se abilitato, l'opzione **✏️ Altro...** apre il campo «Nome modello» per un modello non in lista.

⚠️ Fuori casa **l'upload di file e la Knowledge Base sono disabilitati** per proteggere i tuoi dati (Capitolo 20). Se la Knowledge Base o la KB Chat sono attive, il passaggio viene proprio **bloccato**: «🔒 **Cloud provider bloccato**: Knowledge Base o KB Chat attiva. I tuoi dati locali rimangono privati!», con l'indicazione «Disattiva Knowledge Base e KB Chat, oppure usa una destinazione in casa (Ollama locale, LAN, Tailscale)», e la connessione torna su "Local (Ollama)".

## 12.4 Parametri del modello — expander `⚙️ Parametri`

| Parametro | Range | Default | Significato |
|---|---|---|---|
| System Prompt | testo libero | "Sei un assistente utile. Rispondi in modo chiaro e preciso." | Istruzioni permanenti date al modello. Con rizzo-pii attivo, verso fuori casa gli si aggiunge (senza che compaia nel campo) una riga che chiede al modello di usare i segnaposto così come sono (Cap. 21.7) |
| Temperature | 0.0 – 2.0 (step 0.1) | 0.7 | Creatività: bassa = risposte prevedibili, alta = più varie |
| Max messaggi | 10 – 100 (step 10) | 50 | Quanti messaggi recenti restano nel contesto. Vale solo **senza** contesto KB: quando la Knowledge Base o la KB Chat trovano risultati, la domanda viene inviata con il solo contesto dei documenti, senza la cronologia |

Non ci sono altri parametri (per esempio niente «max token»). I bottoni socratici e la Mappa Sessione non usano il tuo System Prompt ma un prompt fisso.

---

# Capitolo 13 — La chat: messaggi e allegati

## 13.1 Allegare file — `📎 Allega file (opzionale)`

Sopra il campo messaggio puoi trascinare o selezionare **più file**:

| Tipo | Formati | Cosa succede |
|---|---|---|
| Documenti | PDF, TXT, MD, DOCX | Il testo viene estratto e aggiunto al tuo messaggio (solo a quello: vedi sotto) |
| Immagini | PNG, JPG, JPEG, GIF, WEBP | Richiedono un modello "Vision" (vedi sotto) |

**Limiti**: il widget indica «Max 10MB per file», ma è solo un'indicazione: il limite effettivo è quello di Streamlit, **200 MB**. File grandi rallentano l'estrazione e allungano molto il messaggio; il testo estratto da un documento viene troncato a **50.000 caratteri** (con nota esplicita nel messaggio). Dai PDF viene estratto il testo pagina per pagina (`[Pagina N]`); dai DOCX paragrafi e tabelle; i PDF di sole immagini vengono segnalati come privi di testo estraibile.

Ogni file allegato appare in un'**anteprima** sotto l'intestazione «**📎 N file allegati:**», un expander per file «{icona} {nome} ({dimensione})»: thumbnail per le immagini, primi 500 caratteri per i documenti, con icona per tipo (📕 PDF, 📘 DOCX, 📄 TXT, 📝 MD, 🖼️ immagine). Sotto compare «📎 N file pronti per l'invio».

ℹ️ **Il testo di un documento arriva al modello solo nel messaggio in cui lo alleghi.** Nella cronologia si salva solo quello che hai scritto tu (più i nomi dei file): nei turni successivi il modello non vede più il documento, se non nella risposta che ha già dato.

**Modelli Vision**: le immagini sono accettate solo se il nome del modello contiene uno dei nomi riconosciuti (LLaVA e varianti, Granite3-Vision, Moondream, BakLLaVA, CogVLM, Fuyu, MiniCPM-V). Modelli vision con altri nomi (es. `llama3.2-vision`, `qwen2.5vl`, `gemma3`) **non** vengono riconosciuti. Con un modello non riconosciuto compare «⚠️ **Immagini rilevate** ma il modello `{modello}` non supporta Vision. Le immagini verranno **ignorate**…» e le immagini non compaiono nell'anteprima.

> ✅ **Novità v1.15.3 (Vision local-only)**: con un modello Vision le immagini allegate vengono **inviate davvero al modello** insieme al testo (nelle versioni precedenti venivano preparate ma non inviate). Funziona solo verso destinazioni «in casa»: **Local (Ollama)** e **Remote host** in LAN o Tailscale — mai verso il cloud, dove l'upload resta disabilitato. Dalla 1.16.0 anche un Remote host che punta a un indirizzo Internet conta come «fuori casa»: allegati e immagini sono disabilitati come per il cloud (Cap. 21.4). Le immagini sono **effimere**: non vengono salvate in conversazioni, KB o vault; nella cronologia restano solo i nomi dei file allegati.

**Fuori casa** (cloud o host su Internet) l'upload è disabilitato: «📎 **Upload file disabilitato per privacy** — Il modello è fuori dalla tua rete (Cloud provider o host su internet)…».

## 13.2 Inviare e ricevere

- Scrivi nel campo (placeholder "Scrivi il tuo messaggio...", oppure "Chiedi qualcosa sui tuoi documenti..." se la KB è attiva) e premi **🚀 Invia**.
- Prima dell'invio l'app verifica: modello selezionato («❌ Seleziona un modello!»), chiave API per il cloud («❌ Inserisci API key!»), blocco KB fuori casa («🔒 Cloud provider bloccato con Knowledge Base o KB Chat attiva!», oppure «🔒 host esterno ({host}) bloccato…»), URL bloccato («🔒 Connessione bloccata per sicurezza: …»), configurazione ibrida («🛡️ Configurazione ibrida non valida, messaggio non inviato: …»). Il messaggio d'errore compare in rosso sopra la casella.
- **Dalla 1.16.0 il testo resta nella casella** dopo un blocco (questi, e quelli di rizzo-pii, Cap. 21.4), anche se poi tocchi la sidebar, finché non invii di nuovo o non la svuoti tu. Dopo un invio partito la casella si svuota; durante lo streaming la domanda resta nella casella finché la risposta non è finita. ⚠️ Il messaggio rosso invece sparisce alla prima interazione successiva (limite noto, Appendice B).
- **Se l'invio fallisce** dopo la partenza (chiave sbagliata, rete, errore del fornitore, pacchetto mancante), la domanda resta in chat con «⚠️ **Non inviata** — {tipo}: {errore}» o, se il fornitore aveva cominciato a rispondere, «⛔ **Rifiutata** dal fornitore — …». Vale per ogni destinazione; la domanda si salva così segnata e non viene rimandata al modello nei turni successivi.
- Le risposte con **blocchi di codice** si possono copiare con l'icona in alto a destra del blocco.

> ✅ **Novità v1.15.4**: i blocchi di codice restano interi anche dopo la fine dello streaming e nelle conversazioni ricaricate. Prima, un blocco con righe vuote (quasi tutto il codice Python) veniva spezzato e, copiandolo, negli appunti comparivano scritte «[object Object]».

- Se la Knowledge Base è attiva vedrai gli spinner "🔍 Ricerca documenti rilevanti..." e/o "📚 Ricerca nella KB Chat...", con il conteggio dei documenti trovati («📎 Trovati N documenti KB», «📚 Trovati N risultati dalla KB Chat»); le **fonti** usate compaiono sotto la risposta nell'expander **"📎 Fonti (N)"**.
- Il bottone **🔄 Nuova** azzera e apre una conversazione nuova (messaggi, contatori, storico socratico, mappa sessione, metadati KB della chat, e dalla 1.16.0 la memoria dei dati tolti e il riquadro «👁️ Cosa ha visto il modello»). Non spegne la Knowledge Base.
- ⚠️ **Limite noto:** il riquadro degli allegati **non si svuota** da solo, né dopo l'invio né con «🔄 Nuova». Prima del messaggio successivo togli a mano i file dal riquadro (la ✕ accanto a ciascuno) o ricarica la pagina, altrimenti potrebbero essere allegati di nuovo.

---

# Capitolo 14 — Knowledge Base documentale (cartelle, wiki, vault)

La Knowledge Base (KB) permette all'AI di rispondere **sui tuoi documenti**: l'app cerca i passaggi più pertinenti alla tua domanda e li fornisce al modello come contesto, chiedendogli di citare le fonti.

Sidebar → expander **📚 Knowledge Base (Wiki / Vault)** (aperto di default). Con la KB spenta una riga elenca le sorgenti disponibili.

## 14.1 Attivazione

Spunta **"🔍 Usa Knowledge Base"**. Comparirà:
- `🔒 Privacy reale - dati e chat restano nella tua rete` se la destinazione è «in casa» (Ollama locale, Remote host in LAN o Tailscale);
- `🔒 Cloud provider: KB bloccata per privacy!` se sei su un provider cloud;
- dalla 1.16.0, `🔒 host esterno ({host}): KB bloccata per privacy!` se il Remote host risolve a un indirizzo Internet, `🔒 destinazione non verificabile ({host}): KB bloccata per privacy!` se l'indirizzo non si risolve, `🔒 Connessione bloccata - endpoint metadati cloud` per un indirizzo link-local.

In tutti i casi «fuori casa» la sidebar riporta la connessione su «Local (Ollama)» (Cap. 20.1 e 21.4).

Nell'area principale:
- KB attiva e indicizzata: `📚 Knowledge Base ATTIVA - N documenti | N chunks`;
- KB attiva ma vuota: `📚 Knowledge Base attivata ma non indicizzata. Configura una cartella nella sidebar.`;
- a chat vuota: `👋 Knowledge Base attiva! Fai una domanda sui tuoi documenti.`

## 14.2 Sorgenti disponibili — `📁 Sorgente Documenti`

Il menu dipende da `mode` in `wiki_sources.yaml` (Cap. 6.5):

- **`selectable`** (file fornito): menu **"Seleziona sorgente"** con le sorgenti del file, ciascuna con l'icona scritta nel YAML (es. «📁 Documenti Locali», le wiki con 🌐 🖥️ 🌍 📘 📗…), più in coda **🟣 Vault Obsidian**, **🟤 Vault LogSeq** e **⬛ Export Notion**. Per le sorgenti del YAML si preme solo **🔄 Sincronizza**.
- **`custom`**, o file senza sorgenti: menu **"Tipo sorgente"** con i tipi liberi — 📁 Cartella Locale, 🌐 MediaWiki, 📘 DokuWiki e i tre vault — e i campi per inserire URL o percorso. Per le wiki c'è l'expander **⚙️ Opzioni avanzate**: Namespace, «Max pagine» (0 = tutte), «Richiede autenticazione» (username/password).
- **`fixed`**: solo la sorgente predefinita, senza scelta (e senza vault).

| Sorgente | Formati letti | Note |
|---|---|---|
| Cartella Locale | `.md`, `.txt`, `.html`/`.htm`, `.pdf` | checkbox per formato e "📂 Includi sottocartelle" |
| MediaWiki | pagine wiki | richiede il pacchetto `mwclient` |
| DokuWiki | pagine wiki | richiede il pacchetto `dokuwiki` |
| Vault Obsidian | `.md`, `.canvas` | |
| Vault LogSeq | `.md` | i file `.org` vengono contati ma **non** letti |
| Export Notion | `.md` | riconosciuto dai file `_index*.csv` |

⚠️ **Le cartelle da ignorare dei vault** (`.obsidian`, `templates`, `.trash`, `.archive` per Obsidian; `logseq/bak`, `logseq/version-files` per LogSeq) nella 1.16.0 valgono solo per il **conteggio** dei file, non per l'indicizzazione: i file `.md` che contengono finiscono anch'essi nella KB (limite noto, Appendice B).

Nel campo **"Percorso cartella"** della Cartella Locale il tipo viene **riconosciuto automaticamente** («🟣 **Vault Obsidian rilevato**», con «N file compatibili trovati»). Nel pannello di un vault scelto dal menu compare «N file trovati (.md, .canvas)»: lì il tipo non viene verificato, si usa quello scelto.

> ℹ️ Il codice prevede anche una voce **"➕ Configura manualmente..."** nel menu `selectable`, ma con le condizioni attuali non compare mai: per inserire sorgenti ad hoc il sistemista imposta `mode: "custom"` (vedi sopra).

## 14.3 Indicizzazione

1. Configura la sorgente (percorso o URL).
2. (Facoltativo) Regola i **⚙️ Parametri Chunking**: dimensione chunk 200–3000 caratteri (default 1000, passi di 100), overlap 0–500 (default 200, passi di 50). Tieni l'overlap sotto la dimensione del chunk (Cap. 9.2).
3. Premi il bottone di indicizzazione: **🔄 Indicizza Documenti** (cartella), **🔄 Indicizza Vault Obsidian** / **🔄 Indicizza Vault LogSeq** / **🔄 Indicizza Export Notion**, **🔄 Sincronizza Wiki** / **🔄 Sincronizza DokuWiki** (modalità custom) o **🔄 Sincronizza** (sorgenti del YAML).
4. Subito dopo il clic compare il **banner di stima** (numero di file/pagine e tempo previsto in base al modello di embedding, con «💡 CPU al 100% durante l'embedding — è normale, non chiudere l'app»; per una wiki senza limite di pagine «⚠️ **Numero pagine non limitato** — durata variabile»), poi la barra di avanzamento («🔄 Avvio sincronizzazione...») fino a "✅ Indicizzazione completata!" (o «❌ Errore indicizzazione»).

Ogni indicizzazione ricostruisce da zero l'intera Knowledge Base: indicizzare una sorgente nuova **sostituisce** quella precedente (una sola sorgente attiva alla volta). Per le wiki già configurate viene mostrata la data dell'ultimo sync e il numero di pagine; dopo una cartella o un vault compare il riquadro «🟣 **Vault Obsidian attivo**» (o «📁 Cartella attivo») con l'ultima sync e il numero di file.

## 14.4 Statistiche e parametri di ricerca

La sezione **📊 Statistiche** mostra: «📄 Documenti» e «📦 Chunks», «🕐 Ultimo update», il tipo di storage («💾 Storage: ChromaDB (persistente)» oppure «⚠️ Storage: Memoria (temporaneo)») e il modello di embedding («🌍 Embedding: `multilingual-e5-small`»; con un indice creato prima della 1.15.0 «⚠️ Embedding: legacy (pre-1.15.0) — re-indicizza per usare e5»). Senza indice: «💡 Configura una sorgente e sincronizza per iniziare».

ℹ️ Il numero di documenti è tenuto solo in memoria: dopo un riavvio dell'app, con l'indice ancora su disco, può comparire «0 documenti» accanto ai chunk giusti.

In **⚙️ Parametri RAG** lo slider **"Documenti per query"** (1–10, default 5) decide quanti passaggi vengono recuperati per ogni domanda, dalla KB documentale e dalla KB Chat. Durante l'invio compaiono «🔍 Ricerca documenti rilevanti...» e «📎 Trovati N documenti KB».

---

# Capitolo 15 — KB Chat: le conversazioni come memoria

Oltre ai documenti, DeepAiUG può usare **le tue conversazioni passate** come base di conoscenza ("KB epistemica", introdotta in v1.14.0): decisioni prese, intuizioni, memoria aziendale.

## 15.1 Includere una chat nella KB — expander `📚 Includi nella Knowledge Base`

Nella sidebar, per la conversazione corrente:

- Checkbox **"Includi questa chat nella Knowledge Base"**;
- **Rilevanza**: `Bassa` / `Media` / `Alta` — le chat più rilevanti salgono nell'ordine dei risultati (boost 1.0 / 1.15 / 1.30, Cap. 9.4);
- **Tipo** (multiselezione): `decisione`, `insight`, `memoria_aziendale`, `riferimento`, `sperimentale`;
- **Note** libere.

Rilevanza, Tipo e Note restano disattivati finché non spunti la checkbox. Se la chat non è ancora salvata su disco, nella sidebar compare: «⚠️ Hai flaggato questa chat per la KB ma non è ancora salvata su disco. Invia un messaggio (o attendi l'auto-save) prima di aggiornare.»

## 15.2 Indicizzare — `🔄 Aggiorna KB Chat`

L'indicizzazione **non è automatica**: dopo aver flaggato le chat premi **"🔄 Aggiorna KB Chat"**. Al termine: «✅ Indicizzate N chat, M chunk totali» e, se ce n'erano, « · 🧹 tolte N chat non più incluse»: dalla 1.15.4 il bottone toglie anche le chat eliminate o non più flaggate. Sotto, la riga «📊 N chat · M chunk indicizzati».

## 15.3 Gestire la KB — expander `📚 Gestione Knowledge Base`

- In testa: «📚 N chat indicizzate · M chunk totali · Ultima indicizzazione: …».
- Elenco delle chat incluse, ciascuna come «data · modello», con stelle di rilevanza (⭐/⭐⭐/⭐⭐⭐), tipi, numero di chunk e note.
- **✏️ Modifica** (rilevanza/tipo/note; **💾 Salva** re-indicizza la chat, **❌ Annulla**) e **🗑️ Rimuovi** («Rimuovere questa chat dalla KB? La chat non verrà eliminata.» → **✅ Conferma** / **❌ No**).
- Sezione **"Flagga chat esistenti"** per aggiungere in blocco vecchie conversazioni: checkbox multiple, «Rilevanza per le selezionate» e **"➕ Aggiungi alla KB (N)"**. Il bottone segna soltanto le chat: per indicizzarle premi poi «🔄 Aggiorna KB Chat».

Eliminando una conversazione (Cap. 18.2) la si toglie anche dalla KB Chat.

## 15.4 Usare la KB Chat nelle risposte — `📚 Usa KB Chat`

Spunta la checkbox **"📚 Usa KB Chat"** per includere le chat indicizzate nel recupero. Con **"Filtra per tipo"** scegli i tipi (vuoto = tutti). Durante l'invio vedrai «📚 Ricerca nella KB Chat...» e «📚 Trovati N risultati dalla KB Chat»; le fonti appaiono come `💬 {identificativo della conversazione}` (le conversazioni non hanno un titolo).

> 🔒 **Privacy**: dalla v1.15.2 «Usa KB Chat» **è coperto dal blocco** come la KB documentale. Nella sidebar: «🔒 **Cloud provider bloccato**: Knowledge Base o KB Chat attiva. I tuoi dati locali rimangono privati!» (dalla 1.16.0 anche «🔒 **host esterno ({host}) bloccato**: …» per un Remote host su IP pubblico), e la connessione torna su Local. All'invio: «🔒 Cloud provider bloccato con Knowledge Base o KB Chat attiva!».

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
| 🪞 **Rifletti** | L'unico che analizza la **tua domanda**, non la risposta: presupposizioni implicite, destinatario implicito, e la "domanda sotto la domanda". Non risponde: ti aiuta a capire se stai facendo la domanda giusta. Compare solo se prima della risposta c'è una tua domanda |

Dettagli utili:
- Ogni bottone mostra uno spinner durante la generazione e poi diventa ✅: «✅ Alternative», «✅ Assunzioni», «✅ Limiti», «✅ Confutato», «✅ Riflettuto». Il risultato si apre in un pannello dedicato («🔄 **Alternative generate** - Esplora prospettive diverse», «🤔 **Assunzioni implicite** - Cosa si dà per scontato?», «⚠️ **Limiti di validità** - Quando NON funziona», «🎭 **Confutazione** - Avvocato del diavolo», «🪞 **Riflessione sulla domanda** - Sfida il tuo perimetro») con una domanda-guida finale (es. "💡 Quale prospettiva ti sembra più utile?").
- I risultati sono **memorizzati** nella sessione: ripremere il bottone non rigenera. In calce compare «🤖 {modello}  •  🕐 HH:MM» (l'ora è quella in cui la pagina viene mostrata, non quella della generazione). Caricando una conversazione i pannelli non ricompaiono: i risultati restano nello storico (16.3).
- In modalità 🧠 Socratico, sotto ogni risposta compare l'invito: «🧠 **Modalità Socratica attiva** - Prima di accettare questa risposta, chiediti: *Quali alternative non ho considerato? Cosa sto dando per scontato?*».
- I bottoni usano il modello corrente: se sei fuori casa, anche queste richieste vanno al fornitore (con rizzo-pii acceso, solo con i segnaposto: Cap. 21.4).

## 16.3 Storico delle esplorazioni — sidebar `📋 Esplorazioni socratiche`

Ogni uso di un bottone viene registrato (tipo, orario, domanda, i primi 200 caratteri della risposta analizzata, risultato) e salvato con la conversazione. Nella sidebar trovi: il **totale** («Totale: N esplorazioni»), il conteggio per tipo (🔄 🤔 ⚠️ 🎭 🪞), l'expander «📜 Ultime N esplorazioni» (fino a 10, voci «{emoji} HH:MM - {domanda}») consultabili una per una, e la cancellazione protetta (checkbox "Conferma cancellazione" + "🗑️ Cancella storico"). Senza esplorazioni: «Nessuna esplorazione ancora.». In modalità 🚀 Veloce la sezione è nascosta.

⚠️ **Limiti noti** (Appendice B): premendo «🗑️ Cancella storico» lo storico si svuota ma può comparire un errore di Streamlit; e la cancellazione non viene salvata da sola: lo storico può ricomparire ricaricando la chat prima di un nuovo messaggio.

---

# Capitolo 17 — La Mappa Sessione

Domanda dopo domanda, ogni sessione costruisce senza accorgersene una **cornice interpretativa** (un "frame") che orienta le domande successive. La Mappa Sessione rende visibile questa cornice — **solo quando la richiedi tu**: per scelta di design non c'è nessuna analisi automatica in background.

## 17.1 Le tre modalità — sidebar `📊 Mappa sessione`

| Modalità | Comportamento |
|---|---|
| 🔄 Progressiva | La mappa si aggiorna dopo ogni risposta e diventa visibile dopo **4** domande |
| 🔔 A soglia *(default)* | Dopo **5** domande compare un invito: «💡 Hai fatto {N} domande in questa sessione. Sai da dove stai guardando il problema?» con il bottone **📊 Mostra mappa sessione**. L'invito resta nella sidebar finché non generi la mappa |
| ⏹️ Disattivata | Nessuna nuova mappa, nessun invito (una mappa già generata resta visibile) |

Le domande si contano **dall'inizio della sessione**: caricando una conversazione il conteggio riparte da zero.

Il popover **"❓ Cos'è la Mappa Sessione?"** accanto al titolo spiega la funzione e i suoi riferimenti teorici (sovrascopo, vincolo teleologico, capitale semantico → `PHILOSOPHY.md`).

## 17.2 Cosa mostra

La mappa (expander **"📊 Mappa della sessione"**) contiene tre elementi:

1. **Frame dominante** — una frase: la cornice implicita che stai presupponendo;
2. **Domande → frame** — per ogni tua domanda, come ha costruito o rinforzato quella cornice;
3. **Frame non esplorati** — 2–3 prospettive alternative, formulate come domande, che la sessione non ha percorso.

La mappa non giudica e non dà consigli. È generata **dallo stesso modello che stai già usando**: è una chiamata in più, che contiene tutte le tue domande della sessione. Se sei su cloud, quelle domande vengono inviate di nuovo al provider; in modalità **Progressiva** la chiamata parte dopo **ogni** risposta. Richiede almeno **2 domande** (con una sola, «📊 Genera mappa» non produce niente e non dice nulla) e può essere rigenerata con **🔄 Rigenera mappa**. **📊 Genera mappa** compare ogni volta che non c'è ancora una mappa e la modalità non è Disattivata, anche su una conversazione caricata. Sotto la mappa: «Mappa generata alle HH:MM  •  🤖 {modello}».

---

# Capitolo 18 — Gestione delle conversazioni

Sidebar → `### 💬 Conversazione`.

## 18.1 Salvataggio automatico

La checkbox **"Auto-save"** (attiva di default) salva la conversazione su disco a ogni messaggio. Dopo un'esplorazione socratica la conversazione viene salvata **anche con Auto-save spento**: con Auto-save spento e senza bottoni socratici, invece, la chat non viene salvata (e la KB Chat non la trova). Non esiste — e non serve — un bottone "Salva" manuale. Le conversazioni non si possono rinominare: il file prende nome da data e ora di creazione, l'elenco mostra la data dell'ultimo aggiornamento.

## 18.2 Caricare una conversazione

Il menu **"Carica"** elenca le conversazioni salvate, dalla più recente, come `{icone} {data ultimo aggiornamento} - {modello} ({N})` (modello tagliato a 12 caratteri, N = numero di messaggi); la prima voce è «-- Seleziona --». Senza conversazioni: «💡 Nessuna conversazione salvata». Le icone raccontano il contenuto:

| Icona | Significato |
|---|---|
| 🧠 | La chat è stata condotta con un vault attivo |
| 📚 | Usava una wiki come KB / inclusa nella KB Chat (📚⭐ rilevanza media, 📚⭐⭐ alta) |
| 📁 🟣 🟤 ⬛ | Usava cartella locale / vault Obsidian / LogSeq / Notion |
| 📎 | Contiene allegati |
| 🔒 | Sei fuori casa e la chat contiene dati locali (wiki, cartella, allegati): caricamento protetto. Compare dopo 🧠 |

Selezionata la conversazione, premi **📂 Carica**:
- se sei **fuori casa** (cloud, o dalla 1.16.0 un Remote host su Internet) e la chat contiene dati locali, il caricamento è **bloccato** per privacy («… Questa conversazione contiene dati locali (…). Non può essere caricata con un provider cloud…»); vale anche per una chat con fonti dalla KB Chat, che però non ha l'icona 🔒;
- se la chat usava una KB locale "pesante" (**≥ 50 file**) viene chiesta conferma, con il numero di file e «⏱️ Ri-indicizzazione stimata» (**✅ Procedi** / **❌ Annulla**);
- al caricamento vengono ripristinati messaggi, contatori, impostazioni KB, storico socratico e metadati (la mappa sessione, il conteggio delle domande e i pannelli socratici ripartono da zero), e, se la chat usava una **cartella locale o un vault** ancora presente, la Knowledge Base viene **ri-indicizzata automaticamente** con barra di avanzamento. Per le **wiki** viene solo riattivata la KB con l'indice già presente, che può essere di un'altra sorgente: in quel caso risincronizza la wiki a mano.

**🗑️ Elimina** chiede conferma («🗑️ Eliminare definitivamente questa conversazione?», con «Verrà tolta anche dalla KB Chat.» se ne faceva parte; **✅ Elimina** / **❌ Annulla**) e poi cancella definitivamente la conversazione dal disco. Dalla **v1.15.4** toglie anche i suoi pezzi dalla **KB Chat**; se la KB Chat non risponde lo dice («⚠️ Conversazione eliminata, ma la KB Chat non ha risposto…») e basta «🔄 Aggiorna KB Chat». ⚠️ Se elimini la conversazione **aperta**, i messaggi restano sullo schermo e l'Auto-save la ricrea al messaggio successivo: dopo l'eliminazione premi «🔄 Nuova». Per le chat eliminate con versioni precedenti, «🔄 Aggiorna KB Chat» toglie ora dalla KB Chat i pezzi delle chat che non esistono più o non sono più incluse.

---

# Capitolo 19 — Esportazione

Sidebar → `### 📤 Export` (attivo appena c'è almeno un messaggio; prima: «💡 Inizia una conversazione per abilitare l'export»).

## 19.1 Esportare la conversazione corrente

1. **Formato Export**: `📝 Markdown (.md)`, `📋 JSON (.json)`, `📄 TXT (.txt)`, `📕 PDF (.pdf)`.
2. **Contenuto**: conversazione completa, oppure ultimi 10 / 20 / 50 messaggi.
3. **Nome file (senza estensione)** — default `conversation_{id}`.
4. **👁️ Anteprima Export** mostra il risultato nell'area principale, con **❌ Chiudi Anteprima** (il PDF non è anteprimabile: «📕 Preview PDF non disponibile…»); **📥 Download** genera il file e fa comparire il bottone di salvataggio **💾 Salva {formato}** (es. «💾 Salva Markdown»).

Contenuto per formato:
- **Markdown**: «# Conversazione LLM» con **Data** (di creazione), **Modello** e **Messaggi**, messaggi con intestazioni `## 👤 Tu - {data ora}` / `## 🤖 AI - {data ora}`, fonti in corsivo, footer «*Generato con DeepAiUG v1.16.0 - …*»;
- **JSON**: struttura completa e rielaborabile (info export + conversazione con id, data di creazione, modello, provider e messaggi integrali);
- **TXT**: testo semplice con `[Tu]` / `[AI]`;
- **PDF**: testo semplice impaginato (richiede `reportlab`): il Markdown non viene interpretato. ⚠️ Senza `reportlab` il bottone non produce niente e non dà errore.

Gli allegati non vengono esportati, solo i loro nomi.

## 19.2 Batch Export — `### 🗂️ Batch Export`

Esporta **tutte** le conversazioni salvate in un colpo solo (la sezione compare con una chat aperta non vuota e almeno una conversazione salvata: «📁 N conversazioni salvate»): scegli il **Formato batch** e premi **📦 Genera ZIP** → «✅ ZIP pronto (N conversazioni, {formato})» → **💾 Download ZIP** (`conversations_batch_{AAAAMMGG_HHMMSS}.zip`, con un file `conversation_{id}.{ext}` per chat). ⚠️ In formato PDF senza `reportlab` lo ZIP esce vuoto.

---

# Capitolo 20 — Privacy: come DeepAiUG protegge i tuoi dati

DeepAiUG applica quattro livelli di protezione quando entrano in gioco provider cloud o connessioni di rete:

## 20.0 Verifica della destinazione reale (novità v1.15.2)

Dalla v1.15.2 un **classificatore URL** (`core/url_validator.py`) verifica dove risolve **davvero** l'host di ogni connessione Local/Remote, indipendentemente dall'etichetta della modalità:

- **Rete fidata** — loopback (`127.x`), rete privata (`10/8`, `172.16/12`, `192.168/16`, e gli altri range che Python considera privati) e range CGNAT/VPN mesh come Tailscale (`100.64.0.0/10`): banner verde "🔒 **Rete fidata** - i dati restano nella tua rete ({host})". ℹ️ Il nome viene risolto solo in IPv4: un indirizzo IPv6 come `[::1]` risulta «non valido»;
- **Host esterno** — l'host risolve a un IP pubblico: banner giallo "⚠️ **Host esterno** - i dati escono dalla tua rete verso {host}";
- **Bloccato** — range link-local `169.254.0.0/16` (endpoint metadati cloud, es. `169.254.169.254`): banner rosso «🔒 **Connessione bloccata** - endpoint metadati cloud»; la connessione è **rifiutata** ovunque (chat, fetch modelli, adapter wiki) come protezione anti-SSRF;
- **URL non valido** — schema non http/https o host non risolvibile: banner informativo.

I banner di connessione riflettono quindi la **destinazione reale** dell'URL, non l'etichetta della modalità: se in "Remote host" inserisci un indirizzo Internet, l'interfaccia te lo segnala. Per i provider cloud il banner è «☁️ **Cloud** - Dati esterni (KB e Upload disabilitati)»; un provider «Custom» su loopback o LAN ha invece «🔒 **Rete fidata** - endpoint «Custom» nella tua rete ({host})». Dalla 1.16.0 la stessa classificazione decide anche i blocchi: «in casa» o «fuori casa» (Cap. 21.4).

## 20.1 Blocco: Knowledge Base + cloud

Con la **Knowledge Base attiva** il passaggio a una destinazione «fuori casa» è **impedito**: «🔒 **Cloud provider bloccato**: Knowledge Base o KB Chat attiva. I tuoi dati locali rimangono privati!» (per un Remote host su Internet «🔒 **host esterno ({host}) bloccato**: …», per un indirizzo non risolvibile «🔒 **destinazione non verificabile ({host}) bloccato**: …»), con l'indicazione «Disattiva Knowledge Base e KB Chat, oppure usa una destinazione in casa (Ollama locale, LAN, Tailscale)», e la connessione torna su Local. Dalla v1.15.2 il blocco copre anche **"📚 Usa KB Chat"** (`use_chat_kb`). Analogamente, fuori casa l'upload di file è disabilitato.

Fino alla 1.15.4 il blocco valeva solo per la modalità «Cloud provider» e un Remote host su Internet riceveva KB e allegati con il solo banner «Host esterno». **Dalla 1.16.0** conta la destinazione reale: un Remote host su IP pubblico si comporta come il cloud (KB, KB Chat, allegati e immagini bloccati), mentre un provider «Custom» su loopback o LAN conta come «in casa» (Capitolo 21.4).

## 20.2 Conferma esplicita: documenti in memoria

Se hai caricato file in chat e poi passi a una destinazione fuori casa, l'interfaccia si blocca sulla pagina **"🔐 Conferma Privacy Richiesta"**, che elenca i file coinvolti e offre tre uscite:

1. **🔄 Reset e usa Cloud** *(consigliato)* — cancella la cronologia e prosegue in sicurezza;
2. **✅ Procedi con Cloud** (riquadro «Procedi comunque») — disponibile solo dopo aver spuntato "Confermo: i documenti non contenevano dati riservati". **Con rizzo-pii attivo nella configurazione** (Cap. 21) diventa **🛡️ Procedi con anonimizzazione**, con la spunta «Ho capito: parte il testo senza i dati personali riconosciuti»; la scelta dipende dalla configurazione, non dal fatto che rizzo-pii risponda in quel momento (se non risponde, l'invio si blocca: Cap. 21.4);
3. **↩️ Torna a Local/Remote** — riporta sempre su «Local (Ollama)».

Ogni nuovo documento caricato azzera un eventuale consenso precedente.

## 20.3 Protezione delle conversazioni salvate

Le chat che contengono dati locali (allegati, KB, vault) sono marcate con 🔒 quando sei fuori casa e **non possono essere caricate** finché resti fuori casa (Cap. 18.2).

⚠️ **Attenzione all'ordine:** se carichi una chat del genere mentre sei in Local/Remote, disattivi la KB e **poi** passi al cloud, non c'è nessun blocco: compare solo un avviso, e al primo messaggio **l'intera cronologia** (comprese le risposte ricavate da documenti locali) viene inviata al provider. La conferma esplicita del 20.2 scatta solo per i file caricati in questa sessione. Per restare privato, apri una **nuova conversazione** prima di passare al cloud.

## 20.4 Cosa è cambiato in v1.15.2 (e cosa devi comunque sapere)

Due dei tre limiti noti documentati per la v1.15.1 sono stati affrontati dall'audit di sicurezza v1.15.2:

- ✅ **RISOLTO** — *"Il toggle 📚 Usa KB Chat non è coperto dal blocco cloud"*: dalla v1.15.2 il blocco cloud copre anche `use_chat_kb`. Con KB Chat attiva il passaggio al cloud è impedito, esattamente come per la KB documentale (vedi 20.1).
- ✅ **MIGLIORATO** — *"Remote host è considerato fidato per definizione"*: ora il classificatore URL (vedi 20.0) verifica l'indirizzo a cui l'host risolve realmente e l'interfaccia ti avvisa con "⚠️ Host esterno" se la destinazione è fuori dalla tua rete; gli endpoint metadati cloud sono bloccati del tutto. Resta tua la decisione finale: l'avviso non impedisce di usare un host esterno.

Limiti ancora validi nella 1.16.0:

- La Mappa Sessione e i bottoni socratici usano il modello corrente: se sei fuori casa, anche quelle richieste vanno al fornitore (con rizzo-pii acceso, a soli segnaposto: Cap. 21.4).
- Una chat caricata e poi usata sul cloud manda tutta la cronologia (vedi 20.3).

Risolto nella 1.16.0: un Remote host su un indirizzo Internet non è più solo avvisato, è bloccato come il cloud (Capitolo 21.4).

---

# Capitolo 21 — L'ambiente ibrido: rizzo-pii e Annona (v1.16.0)

> Questo capitolo descrive una funzione della **1.16.0**, provata dal vivo con rizzo-pii vero e OpenAI. È **opzionale e spenta per default**: con la sezione `hybrid:` assente o spenta, DeepAiUG si comporta come la 1.15.4, salvo la regola della destinazione reale (21.4), che vale sempre. Il dettaglio tecnico è in `docs/SPEC_v1.16.0_hybrid.md`.

L'idea: usare un modello cloud senza mandargli i dati personali. Prima che il testo esca di casa, un programma locale toglie nomi, codici fiscali, indirizzi e simili e li sostituisce con **segnaposto** (`[FULLNAME_1]`, `[CF_1]`…). Il cloud risponde usando i segnaposto e DeepAiUG rimette i valori veri **sul tuo computer**, prima di mostrarti la risposta.

## 21.1 I due programmi

- **rizzo-pii** (licenza MIT, https://github.com/Rizzo-AI-Academy/rizzo-pii) — riconosce i dati personali nel testo italiano e li sostituisce con segnaposto. È il pezzo che serve: **l'ambiente ibrido funziona anche solo con rizzo-pii.** DeepAiUG lo chiama su `http://127.0.0.1:5005`.
- **Annona** (licenza Apache-2.0, https://github.com/akaion-ai/annona) — un «kernel» che decide dove può andare ogni passo, secondo una policy, e tiene un **registro** a catena delle decisioni. È **facoltativo**. DeepAiUG lo chiama su `http://127.0.0.1:7070`.

Entrambi sono **programmi separati**: DeepAiUG non li include, non li scarica e non li installa. Li chiama soltanto via HTTP, e solo su loopback (`127.0.0.1` o `localhost`): un indirizzo diverso viene rifiutato quando l'app prova a chiamarli (in chat la domanda resta «⚠️ **Non inviata** — PIINotLocal: …»; nella sezione Annona «configurazione non valida (AnnonaNotLocal)»). Licenze e note sono nel file `NOTICE`.

> Vincenzo Iodice (Gilles) ha un ruolo non retribuito di Technical Advisor in Akaion, che sviluppa Annona. Annona è opzionale e spenta per default; l'ambiente ibrido funziona anche solo con rizzo-pii, che non ha legami con Akaion.

## 21.2 Installarli (a parte)

Si installano **seguendo i loro README**, non con script di DeepAiUG:

- rizzo-pii: il README del suo repository (sopra). Attenzione: le build già pronte di rizzo-pii (AppImage, `.deb`, `.exe`, `.dmg`) e la sua immagine Docker sono rilasciate sotto **AGPL-3.0** (vedi il `NOTICE`); il codice sorgente è MIT.
- Annona: il README del suo repository (sopra), compresa la scrittura della policy.

Prima di accendere l'ambiente ibrido, verifica che il servizio risponda sul suo indirizzo (`/health`). Con `pii.enabled: true` e rizzo-pii spento, verso fuori casa **non parte niente** (21.4). Con la sola Annona accesa in modo `read` (e `pii.enabled: false`) il testo parte **in chiaro**, come senza ibrido.

**Chi aggiorna da una versione precedente** non ha la sezione `hybrid:` nel suo `security_settings.yaml` (lo script di aggiornamento non lo tocca): va aggiunta a mano, come nel Capitolo 4.1, copiando il blocco del 21.3.

## 21.3 La sezione `hybrid:` di `security_settings.yaml`

```yaml
hybrid:
  pii:
    enabled: false                  # rizzo-pii prima del cloud
    url: "http://127.0.0.1:5005"    # solo loopback
    timeout_s: 30
    exclude_tags: []                # tag lasciati in chiaro, es. ["AMOUNT", "DATE"]; nessuno per default
  annona:
    enabled: false
    url: "http://127.0.0.1:7070"    # solo loopback
    mode: "read"                    # read = sola lettura in sidebar; gateway = sperimentale (21.6)
  on_service_down:
    cloud: "block"                  # fisso: altri valori sono un errore
    local: "proceed"                # accetta proceed|block, ma nella 1.16.0 non ha effetto
```

È lo stesso blocco del `security_settings.yaml` del repository (lì con qualche commento in più): chi aggiorna può copiarlo da qui o da lì, in fondo al proprio file.

- File o sezione assente → tutto spento.
- Tipi sbagliati, YAML illeggibile o `on_service_down.cloud` diverso da `block` → **errore esplicito**, mai «spento» in silenzio: il messaggio della chat verso fuori casa non parte («🛡️ Configurazione ibrida non valida, messaggio non inviato: …») finché la configurazione non è corretta. ⚠️ Nella 1.16.0 il blocco vale **solo per il messaggio della chat**: bottoni socratici, nudge e mappa, con la configurazione illeggibile, partono come senza ibrido (Appendice B).
- L'indirizzo (`url`) non viene controllato quando si legge il file, ma quando l'app chiama il servizio (21.1).
- `on_service_down.local: "block"` è accettato ma nella 1.16.0 non fa nulla: in casa si procede sempre.
- **Dove si anonimizza non si configura**: sempre e solo **fuori casa** (21.4). Una chiave `apply_to` nel file viene ignorata.

## 21.4 «In casa» e «fuori casa»: la destinazione reale

Dalla 1.16.0 i blocchi e l'anonimizzazione guardano **dove va davvero il testo**, non l'etichetta della connessione:

| Destinazione | Esito |
|---|---|
| `Cloud provider` OpenAI, Anthropic, Google | **fuori casa**, sempre |
| Ollama locale, Remote host o cloud «Custom» su loopback, rete privata (LAN) o Tailscale (`100.64.0.0/10`) | **in casa** |
| Remote host, Ollama locale o «Custom» su un **IP pubblico**, indirizzo link-local, nome non risolvibile o URL rotto (anche vuoto) | **fuori casa** (nel dubbio, si blocca) |

**Novità importante, anche con l'ambiente ibrido spento:** un Remote host su un IP pubblico **ora si comporta come il cloud**. Knowledge Base, KB Chat, allegati e immagini verso quell'host sono **bloccati** (prima c'era solo il banner «Host esterno», vedi 20.0 e 20.1). Dialogo privacy, icone 🔒, bordo rosso e titolo seguono la stessa regola.

Che cosa succede in ogni caso:

| Situazione | In casa | Fuori casa |
|---|---|---|
| ambiente ibrido spento | come la 1.15.4 | come la 1.15.4 (con la regola della destinazione reale qui sopra) |
| rizzo-pii acceso e funzionante | il testo parte così com'è | parte **solo il testo con i segnaposto**; la risposta torna con i valori veri |
| rizzo-pii spento, lento o in caricamento | si procede | **si blocca**: «🛡️ rizzo-pii non risponde: il messaggio non è stato inviato fuori dalla tua rete. Avvia rizzo-pii e riprova.» Il testo torna nella casella |
| rizzo-pii in modalità definitiva (senza tabella) | si procede | se nel testo ci sono dati personali si blocca: «🛡️ rizzo-pii è in modalità definitiva (senza tabella): il messaggio non è stato inviato. Riattiva la tabella dei segnaposto nelle impostazioni di rizzo-pii.»; un testo senza dati personali parte |
| rizzo-pii risponde male | si procede | si blocca: «🛡️ rizzo-pii ha risposto con un errore (…)» o «🛡️ Risposta di rizzo-pii non coerente: …» |
| immagine allegata | si procede | **mai fuori casa**: l'upload è già disattivato («📎 Upload file disabilitato per privacy»); se un'immagine arrivasse comunque al guard, si blocca |
| Knowledge Base, KB Chat, allegati | si procede | **restano bloccati** nella 1.16.0, anche con rizzo-pii |
| Annona attivata in modo `read` (accesa o spenta) | si procede; se è giù la sidebar lo dice | si procede come nelle righe sopra (con i segnaposto se rizzo-pii è acceso): Annona non vede i messaggi, e la risposta porta «📒 non registrato in Annona» |
| Annona attivata in modo `gateway` ma giù o senza policy | client di sempre | **si blocca**: «🧭 Annona non risponde o non ha una policy: con il gateway acceso il messaggio non è stato inviato.» |
| `annona.enabled: false` (qualunque `mode`) | client di sempre | il gateway non c'è: valgono le righe di rizzo-pii |
| Annona risponde `held` (gateway) | — | si blocca: «🧭 Annona ha trattenuto il passo (held): {motivo}»; se il passo è annullato, «🧭 Il passo è stato annullato in Annona: nessuna risposta.» |
| gateway acceso: bottoni socratici, nudge, mappa della sessione | client di sempre | con rizzo-pii acceso **passano da rizzo-pii**; con rizzo-pii spento **si bloccano**: «Con il gateway di Annona, questa funzione verso il cloud richiede rizzo-pii» |
| errore del modello (chiave sbagliata, rete, errore del fornitore) | come fuori casa | l'errore **resta visibile in chat** accanto alla domanda, «⚠️ **Non inviata** — …» o «⛔ **Rifiutata** dal fornitore — …», anche ricaricando |
| risposta interrotta a metà | come fuori casa | la parte già arrivata **non si salva**; resta la domanda, di solito segnata «rifiutata» |

In tutti i blocchi: niente verso il fornitore, un messaggio chiaro, nessun testo dell'utente nei log. I blocchi del messaggio della chat compaiono in rosso sopra la casella (e spariscono alla prima interazione successiva, mentre il testo resta: Appendice B); quelli dei bottoni socratici sotto il bottone; quelli della mappa nella sidebar.

## 21.5 Che cosa vedi nella chat

- **Il dialogo privacy**, con rizzo-pii attivo nella configurazione, offre **«🛡️ Procedi con anonimizzazione»** al posto di «✅ Procedi con Cloud» (Cap. 20.2).
- **Il badge** sotto la risposta: «🛡️ N dati tolti prima dell'invio» («1 dato tolto» al singolare; compare anche con 0). Il numero conta i segnaposto diversi in **tutto** il testo partito in quella chiamata (system prompt, cronologia, domanda), non solo nella nuova domanda. Si salva con la conversazione e resta ricaricandola. Con il gateway non c'è; i bottoni socratici non hanno né badge né riquadro.
- **Il riquadro «👁️ Cosa ha visto il modello»**: il testo com'è partito, con i segnaposto (con il gateway, quello che Annona dice di aver mandato). Vale **solo nella sessione corrente**: non si salva, sparisce con «Nuova» e quando carichi una conversazione.
- **Che cosa si salva**: la conversazione salvata contiene, come sempre, la tua domanda e la risposta **con i valori veri**, sul tuo computer; in più solo il numero dei dati tolti. La tabella segnaposto → valore **non si salva mai** (né nei log, né nella KB Chat, né nell'export): vive solo in memoria, per la sessione, e serve a togliere sempre con lo stesso segnaposto i valori già visti (21.7).
- **La sezione «🧭 Annona»** della sidebar (se Annona è attivata): un expander chiuso, «🧭 Annona — sola lettura» o «🧭 Annona — gateway (sperimentale)». Dentro: «🧭 Annona attiva — N regole, N substrati, N decisioni (N held)», le ultime 8 decisioni del registro (numero, classe, esito, → substrato, motivo: mai il testo) e la verifica della catena. Si aggiorna al massimo ogni 20 secondi o con «🔄 Aggiorna». Se Annona è giù la sezione lo dice: in modo `read` «L'app procede: gli invii non vengono registrati in Annona.»; in modo `gateway` «Con il gateway acceso, verso fuori casa non parte niente finché Annona non risponde.»

## 21.6 Il gateway di Annona (sperimentale)

Con `annona.enabled: true` e `annona.mode: "gateway"`, per le destinazioni **fuori casa** non è DeepAiUG a chiamare il modello: manda la domanda ad Annona, che decide, redige secondo la sua policy, chiama il modello e registra il passo. In pagina compare l'avviso «🧭 **Gateway Annona — SPERIMENTALE.** Verso fuori casa decide, redige, chiama il modello e registra Annona. Si perde: …», durante la chiamata la bolla dice «🧭 Gateway Annona — sperimentale» e la risposta porta «🧭 via Annona (sperimentale) · classe · esito · substrato · registrato in Annona».

Che cosa si perde:

- **lo streaming**: la risposta arriva tutta insieme;
- **la scelta del modello**: la fa la policy di Annona, non la sidebar (il modello salvato è `annona:<substrato>`, o `annona:?` se Annona non lo dice; il provider «Annona gateway (sperimentale)»);
- **le chiavi**: quelle dei fornitori stanno nella policy di Annona, non in DeepAiUG. ℹ️ Con «Cloud provider» la sidebar chiede comunque una chiave e un modello («❌ Inserisci API key!»), che il gateway non usa.

Da sapere:

- la domanda arriva ad Annona **in chiaro**, su loopback, insieme al system prompt e alla cronologia: la redazione la fa Annona secondo la sua policy, non rizzo-pii (timeout della chiamata: 180 s);
- se Annona è giù, senza policy, in errore, o trattiene il passo (`held`), **non parte niente** e la domanda resta in chat segnata «non inviata»;
- bottoni socratici, nudge e mappa della sessione **non passano da Annona**: con rizzo-pii acceso passano da rizzo-pii, con rizzo-pii spento si bloccano (21.4);
- in casa il gateway non si usa: resta il client di sempre;
- **Annona 0.1.3 offre sempre gli strumenti al modello** (per esempio `explorer`): `/api/kernel/ask` non ha un campo per toglierli, e anche il profilo `read-nothing` li nega senza toglierli. Un modello piccolo (nella prova `llama3.2:3b`) può tentare uno strumento invece di rispondere: Annona lo trattiene e il testo resta vuoto. La domanda resta in chat con l'avviso **«🧭 Senza risposta»**, che dice quale strumento il modello ha tentato (solo il nome, mai percorsi). Rimedi: un modello più capace nella policy di Annona, oppure la strada senza gateway (rizzo-pii con il client dell'Interface).
- **Il registro di Annona 0.1.3 può contenere dati della domanda.** Quando il modello tenta uno strumento, Annona registra la chiamata trattenuta con i suoi argomenti: i **percorsi di file inventati dal modello** finiscono **in chiaro** nel registro, e il modello li costruisce spesso con parole della domanda (nomi, luoghi, aziende). DeepAiUG non li mostra (la sidebar dà solo il nome dello strumento), ma chi può leggere i file di Annona li vede. È lo stesso rimedio del punto sopra; vale anche il limite generale «Annona scrive il testo del passo in chiaro nel suo log» (21.7).

## 21.7 Limiti onesti

- **Pseudonimizzato non è anonimo** (GDPR): la tabella dei valori veri esiste, sul tuo computer, **in memoria per tutta la sessione**: si azzera con «Nuova», quando carichi una conversazione e quando chiudi o ricarichi la scheda del browser. Non va mai su disco. ⚠️ «🔄 Reset e usa Cloud» del dialogo privacy (Cap. 20.2) **non** la azzera (Appendice B).
- **Il contesto si perde**: il modello cloud vede `[FULLNAME_1]` e non sa se è un cliente o un fornitore. Dentro la sessione un valore già tolto riprende sempre lo stesso segnaposto, anche quando rizzo-pii non lo riconoscerebbe più (es. «**Paolo**» in grassetto nel testo del modello, rimandato da «Limiti»). Vale solo per le forme che rizzo-pii ha già tolto così come sono: un diminutivo o un nome storpiato che rizzo-pii non riconosce esce in chiaro.
- **rizzo-pii lavora bene sul testo italiano, non su codice o testo tecnico**: lì toglie troppo, in modo prudente. Una domanda con codice incollato può tornare piena di segnaposto.
- **Importi, date e URL** vengono tolti per default: in una domanda tecnica il modello perde informazioni utili. Chi vuole li lascia in chiaro con `exclude_tags` (es. `["AMOUNT", "DATE"]`).
- **Annona scrive il testo del passo in chiaro nel suo log**: con il gateway, chi ha accesso al computer vede quei file.
- **Le prestazioni**: rizzo-pii gira sul processore e a ogni turno anonimizza di nuovo tutta la cronologia. Con conversazioni lunghe può essere lento.
- **Knowledge Base e allegati verso il cloud restano bloccati** nella 1.16.0: lo sblocco si valuterà dopo aver misurato rizzo-pii sui documenti veri.

Dalla prova dal vivo (06/11/2026, rizzo-pii vero e OpenAI):

- **Le date spezzate**: «12 novembre» può diventare due segnaposto, e il modello può leggerli come giorno e ora («il 12 alle novembre»). Se la data serve, lasciala in chiaro con `exclude_tags: ["DATE"]` o rileggi la risposta.
- **La seconda passata**: un bottone come «Limiti» manda di nuovo al cloud il testo scritto dal modello, ripristinato. rizzo-pii lo anonimizza di nuovo, ma il modello può aver scritto i dati in forme che rizzo-pii non riconosce (nella prova una data storpiata è uscita in chiaro).
- **I log del fornitore**: il fornitore cloud conserva nei suoi log la domanda e la risposta; con rizzo-pii acceso sono a soli segnaposto.
- **I segnaposto spiegati al modello**: senza istruzioni il modello li commentava («l'uso di segnaposto, ad esempio Mario Rossi»). Dalla 1.16.0 il system prompt ha una riga che gli dice di usarli così come sono; resta un'istruzione, non una garanzia.

---

# Appendice A — Tabella dei limiti e valori predefiniti

| Parametro | Valore | Regolabile da UI |
|---|---|---|
| Dimensione massima file allegato | 200 MB (limite di Streamlit; i «10 MB» del testo d'aiuto non sono controllati) | No |
| Troncamento testo documento | 50.000 caratteri | No |
| Formati upload | pdf, txt, md, docx, png, jpg, jpeg, gif, webp | No |
| Temperature | 0.7 (0.0–2.0) | Sì |
| Max messaggi in contesto | 50 (10–100) | Sì |
| Chunk size RAG | 1000 caratteri (200–3000, passi di 100) | Sì |
| Chunk overlap RAG | 200 caratteri (0–500, passi di 50) | Sì |
| Chunk KB Chat | 1000 / overlap 200 | No |
| Documenti per query (top-k) | 5 (1–10) | Sì |
| Modello embedding | `intfloat/multilingual-e5-small` (384 dim) | Solo via env `DEEPAIUG_EMBEDDING_MODEL` |
| Boost rilevanza KB Chat | 1.0 / 1.15 / 1.30 | Indiretto (livello di rilevanza) |
| Soglia nudge Mappa Sessione | 5 domande | No |
| Visibilità mappa (modalità progressiva) | dopo 4 domande | No |
| Minimo domande per generare la mappa | 2 | No |
| Conferma caricamento KB "pesante" | ≥ 50 file | No |
| Batch indicizzazione ChromaDB | 500 chunk | No |
| Timeout `ollama list` / `/api/tags` | 5 s / 10 s (il `connection_timeout` di `remote_servers.yaml` non ha effetto) | No |
| Pausa tra richieste wiki | 0,5 s | Sì (YAML) |
| Timeout / batch wiki | 30 s / 50 | Sì (YAML) |
| Esplorazioni socratiche in sidebar | ultime 10 | No |
| Porta web | 8501 (default Streamlit) | Sì (opzioni Streamlit) |
| rizzo-pii: indirizzo / timeout | `http://127.0.0.1:5005` / 30 s | Sì (YAML `hybrid:`) |
| Annona: indirizzo | `http://127.0.0.1:7070` | Sì (YAML `hybrid:`) |
| Annona: timeout lettura / gateway | 3 s / 180 s | No |
| Annona: aggiornamento sezione / decisioni mostrate | al massimo ogni 20 s / ultime 8 | No |

# Appendice B — Risoluzione dei problemi

| Sintomo | Causa probabile | Rimedio |
|---|---|---|
| "❌ Seleziona un modello!" | Nessun modello rilevato/scelto | Premere 🔄 Aggiorna; verificare `ollama list`; installare un modello (`ollama pull llama3.2:3b`) |
| Nessun modello locale trovato | Ollama spento | Avviare Ollama (`ollama serve`); il launcher lo fa automaticamente |
| "⚠️ Nessun server configurato in remote_servers.yaml" | YAML mancante/vuoto | Il sistemista deve configurare `remote_servers.yaml` (Cap. 6.3) |
| «🔒 **Cloud provider bloccato**: Knowledge Base o KB Chat attiva…» (o «🔒 host esterno (…) bloccato…») | Comportamento voluto: KB o KB Chat con una destinazione fuori casa | Disattivare la KB documentale e/o «📚 Usa KB Chat», o restare in casa (Local, Remote in LAN/Tailscale) |
| "🔤 Embedding: ChromaDB default (MiniLM-L6, EN)" | `sentence-transformers` non installato o download fallito | Installare la dipendenza / verificare la connessione al primo avvio; qualità in italiano ridotta nel frattempo |
| KB svuotata dopo aggiornamento a v1.15.x | Migrazione automatica per cambio modello embedding | Ri-indicizzare le sorgenti e premere 🔄 Aggiorna KB Chat |
| "⚠️ Storage: Memoria (temporaneo)" | ChromaDB non installato | Installare `chromadb`; senza, l'indice si perde alla chiusura |
| KB documentale e KB Chat svuotate senza aggiornamenti | Il modello e5 non si è caricato (rete, cache): il fallback cambia il tag e scatta la migrazione (Cap. 9.3) | Verificare la cache HuggingFace e la rete, poi re-indicizzare. **Possibile difetto**, da correggere |
| Nella KB finiscono file di `.obsidian/`, `templates/`, `.trash/`, `logseq/bak/` | Le esclusioni dei vault valgono solo per il conteggio (Cap. 14.2) | Limite noto: spostare fuori dal vault i file da non indicizzare |
| «0 documenti» nel banner KB dopo un riavvio, con i chunk giusti | Il numero di documenti è tenuto in memoria | Solo estetico: l'indice c'è; re-indicizzare per riavere il numero |
| Chunk enormemente numerosi, indicizzazione lunghissima | Overlap uguale o maggiore della dimensione del chunk | Tenere l'overlap sotto la dimensione del chunk (Cap. 9.2) |
| CPU al 100% durante l'indicizzazione | Normale: embedding in CPU | Attendere; non chiudere l'app |
| Le immagini allegate vengono ignorate | Modello con un nome non riconosciuto come Vision (anche `llama3.2-vision`, `qwen2.5vl`, `gemma3`) o destinazione fuori casa | Usare un modello vision con nome riconosciuto (llava, moondream, granite3-vision…) in casa (Cap. 13.1) |
| I file allegati prima ricompaiono nel messaggio dopo | Il riquadro allegati non si svuota da solo, né dopo l'invio né con «🔄 Nuova» | Togliere i file con la ✕ o ricaricare la pagina |
| «⚠️ **Non inviata** — …» sotto una domanda | L'invio è fallito (chiave, rete, fornitore, pacchetto Anthropic/Google mancante) | Leggere il tipo d'errore; correggere e reinviare. La domanda segnata non viene rimandata al modello |
| Il messaggio rosso del blocco («🛡️ rizzo-pii non risponde…», «❌ Inserisci API key!»…) sparisce appena tocchi la sidebar, mentre il testo resta nella casella | **Limite noto della 1.16.0**: l'avviso si mostra per un solo giro della pagina | Il testo non è partito: correggere la causa e premere di nuovo «🚀 Invia». La correzione è prevista in una 1.16.x |
| «🛡️ rizzo-pii non risponde: il messaggio non è stato inviato fuori dalla tua rete…» | rizzo-pii spento, lento o in caricamento, con `pii.enabled: true` | Avviare rizzo-pii e verificare `/health` (Cap. 21.2); il testo è rimasto nella casella |
| «🛡️ rizzo-pii è in modalità definitiva (senza tabella)…» | rizzo-pii configurato senza tabella dei segnaposto | Riattivare la tabella nelle impostazioni di rizzo-pii |
| «🛡️ Configurazione ibrida non valida, messaggio non inviato: …» | Sezione `hybrid:` scritta male (tipi, rientri, `on_service_down.cloud`) | Correggere il blocco come nel Cap. 21.3. ⚠️ Finché è sbagliato, bottoni socratici e mappa partono come senza ibrido: **possibile difetto** |
| «⚠️ **Non inviata** — PIINotLocal…» / «configurazione non valida (AnnonaNotLocal)» | `url` di rizzo-pii o Annona non di loopback | Usare `http://127.0.0.1:…` (Cap. 21.1) |
| «🧭 Annona non risponde o non ha una policy…» / «🧭 Annona ha trattenuto il passo (held)…» | Gateway acceso e Annona giù, senza policy, o passo trattenuto | Avviare Annona, controllare la policy, o tornare a `mode: "read"` |
| «🧭 **Senza risposta** — …» | Gateway: il modello ha tentato uno strumento e Annona l'ha fermato (Annona 0.1.3) | Modello più capace nella policy di Annona, o strada senza gateway (Cap. 21.6) |
| Con l'ambiente ibrido acceso aggiornando dalla 1.15.x non succede niente | La sezione `hybrid:` non c'è: l'updater preserva `security_settings.yaml` | Aggiungerla a mano (Cap. 4.1, 21.3) |
| Dopo «🔄 Reset e usa Cloud» il badge e il riquadro «👁️ Cosa ha visto il modello» mostrano ancora dati della chat precedente | Il reset del dialogo privacy non azzera la memoria dei dati tolti né lo stato della chat come «🔄 Nuova». **Possibile difetto** | Premere anche «🔄 Nuova» prima di continuare |
| Errore di Streamlit dopo «🗑️ Cancella storico» | Difetto noto dello storico socratico (Cap. 16.3) | Ricaricare la pagina: lo storico è stato svuotato |
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
| **rizzo-pii** | Programma locale e separato che sostituisce i dati personali con segnaposto prima del cloud (v1.16.0, Capitolo 21) |
| **Segnaposto** | Etichetta come `[FULLNAME_1]` al posto di un dato personale; il valore vero resta sul computer |
| **Annona** | Kernel locale e separato, facoltativo, che decide dove può andare un passo e ne tiene il registro (v1.16.0, Capitolo 21) |
| **In casa / fuori casa** | La destinazione reale del testo: loopback, LAN e Tailscale sono in casa; cloud, IP pubblici e indirizzi non verificabili fuori casa (Capitolo 21.4) |
| **Gateway (Annona)** | Modo sperimentale in cui è Annona, non DeepAiUG, a chiamare il modello fuori casa (Capitolo 21.6) |
| **Destinazione reale** | Dove risolve davvero l'indirizzo di una connessione, indipendentemente dall'etichetta (Capitolo 20.0) |

---

*Manuale generato dall'analisi del codice sorgente DeepAiUG v1.15.2 — 2026-07-13; aggiornato alla v1.15.4 il 2026-11-06 dopo l'audit `docs/AUDIT_pre_v1.16.0.md`; aggiornato alla v1.16.0 (Capitolo 21, ambiente ibrido) il 2026-11-06; rivisto per intero contro il codice della v1.16.0 il 2026-11-08.*
