# 🗺️ ROADMAP - DeepAiUG Streamlit Interface

Piano di sviluppo del progetto.

---

## 🧠 Visione: Strumento Socratico

A partire dalla v1.6.1, DeepAiUG abbraccia una nuova filosofia ispirata al **capitale semantico** (Floridi/Quartarone):

> **DeepAiUG non è un oracolo che dà risposte, ma uno strumento che aiuta a costruire SENSO.**

L'AI produce significato plausibile, ma il **senso** lo costruisce l'umano. Le feature "socratiche" stimolano:
1. **Costruzione di senso** - collegare informazioni
2. **Valutazione semantica** - capire cosa conta
3. **Contestualizzazione** - collocare nel contesto giusto
4. **Resistenza alla plausibilità** - non fidarsi del "suona giusto"

### Scelta di Design
L'approccio socratico è **OPZIONALE** (3 livelli: Veloce/Standard/Socratico).
Libertà di scelta = valore fondamentale. **Nessuno forzato.**

---

## 📊 Overview Versioni

```
v1.0.0 ✅ (2026-01-01)          Base interface + Multi-provider
   │
   ├─→ v1.1.0 ✅ (2026-01-02)   + Multi-turn conversations + Persistenza
   │
   ├─→ v1.2.0 ✅ (2026-01-04)   + Export (MD, JSON, TXT, PDF, ZIP)
   │
   ├─→ v1.3.0 ✅ (2026-01-05)   + Knowledge Base RAG + LocalFolder
   │
   ├─→ v1.3.1 ✅ (2026-01-06)   + Fix Ollama + Chunking configurabile
   │
   ├─→ v1.3.2 ✅ (2026-01-07)   + MediaWiki Adapter + YAML config
   │
   ├─→ v1.3.3 ✅ (2026-01-07)   + Ripristino Export completo
   │
   ├─→ v1.4.0 ✅ (2026-01-08)   + Architettura Modulare (27 moduli)
   │
   ├─→ v1.4.1 ✅ (2026-01-09)   + Multi-Wiki (DokuWiki) + UI migliorata
   │
   ├─→ v1.5.0 ✅ (2026-01-11)   + File Upload in Chat + Privacy Protection
   │
   ├─→ v1.5.1 ✅ (2026-01-16)   + Wiki Bugfix + Test Sources
   │
   ├─→ v1.6.0 ✅ (2026-01-25)   + Streaming responses (Ollama/Remote)
   │
   ├─→ v1.6.1 ✅ (2026-01-26)   + 🧠 Socratic Buttons (Genera alternative)
   │
   ├─→ v1.7.0 ✅ (2026-01-27)   + 🧠 Bottoni "Assunzioni" + "Limiti"
   │
   ├─→ v1.7.1 ✅ (2026-01-29)   + 🖥️ Remote YAML + 🔐 Security Settings
   │
   ├─→ v1.8.0 ✅ (2026-02-05)   + 🧠 UI Socratica Completa (5 bottoni + Toggle)
   │
   ├─→ v1.9.0 ✅ (2026-02-06)   + 📋 Socratic History + Persistence
   │
   ├─→ v1.9.1 ✅ (2026-02-11)   + 🎨 UI Polish + ☁️ Cloud Config + 🔒 Privacy Granulare
   │
   ├─→ v1.9.2 ✅ (2026-02-20)   + 🧠 Prompt Epistemologici Potenziati
   │
   ├─→ v1.10.0 ✅ (2026-02-23)  + 📊 Mappa Sessione (F2) — Attrito sul pensiero
   │
   ├─→ v1.11.0 ✅ (2026-02-24)  + 🎨 Branding + UX Polish + Bug Fix parser
   │
   ├─→ v1.11.1 ✅ (2026-02-27)  + 🎨 Matrix Theme
   │
   ├─→ v1.11.2 ✅ (2026-02-28)  + 🚀 Installer multipiattaforma
   │
   ├─→ v1.12.0 ✅ (2026-03-05)  + 🏗️ Architettura Sidebar
   │
   ├─→ v1.13.0 ✅ (2026-03-07)  + 🟣 F3 Vault Support (Obsidian/LogSeq/Notion)
   ├─→ v1.13.1 ✅ (2026-03-08)  + 🟣 Vault nel dropdown custom
   ├─→ v1.13.2 ✅ (2026-03-08)  + 🟣 Vault nel dropdown YAML
   ├─→ v1.13.3 ✅ (2026-03-08)  + 🟣 Banner vault coerente
   ├─→ v1.13.4 ✅ (2026-03-08)  + 🔧 ChromaDB batch fix + progress bar
   ├─→ v1.13.5 ✅ (2026-03-08)  + 🟣 Warning + progress bar caricamento vault
   ├─→ v1.13.6 ✅ (2026-03-09)  + 🔧 Fix progress callback + stima tempo
   ├─→ v1.13.7 ✅ (2026-03-09)  + 🧠 Conferma caricamento vault + icone vault
   ├─→ v1.13.8 ✅ (2026-03-09)  + 🔧 Fix nome modello bottoni socratici
   ├─→ v1.13.9 ✅ (2026-03-09)  + 🔧 Fix modello per esplorazione specifica
   ├─→ v1.14.0 ✅ (2026-03-16)  + 📚 Chat salvate come KB epistemica
   │
   └─→ v2.0.0 🎯 (Q2-Q3 2026)   + Semantic Layer + Knowledge Graph

✅ = Completata
🚧 = In sviluppo
📋 = Pianificata
🎯 = Obiettivo futuro
🧠 = Feature Socratica
```

---

## ✅ Completate

### v1.13.x — F3 Vault Support ✅
**Data:** 2026-03-07 / 2026-03-08

**v1.13.0 — Riconoscimento automatico vault**
- Nuovo modulo `rag/vault.py`: detect_vault_type(), scan_vault_files(), parse_canvas_file(), get_files_to_update()
- Banner UI con icona e conteggio file per tipo vault rilevato
- Parser nativo file .canvas Obsidian (JSON → estrazione testo nodi)
- Aggiornamento incrementale basato su mtime file
- Filtri esclusione per tipo vault (.obsidian/, logseq/bak/, ecc.)
- VAULT_TYPES dict + 3 session key in config/constants.py

**v1.13.1 — Vault nel dropdown custom**
- Vault Obsidian, LogSeq, Notion Export visibili in _render_custom_source_selector()
- Nuova funzione _render_vault_config() — UI dedicata senza checkbox manuali

**v1.13.2 — Vault nel dropdown YAML**
- _render_source_selector() estesa: vault types sempre in coda alle sorgenti YAML

**v1.13.3 — Banner coerente**
- Banner "Vault rilevato" ripristinato con st.info in _render_vault_config()

**v1.13.4 — ChromaDB batch fix + progress bar**
- Fix critico: batch da 500 elementi risolve ValueError su corpus grandi
- Testato su 808 file Obsidian / 6693 chunk
- progress_callback architecture: backend puro, progress bar in UI
- CHROMA_BATCH_SIZE = 500 in rag/vector_store.py

**v1.13.5 — Warning + progress bar caricamento conversazioni vault**
- _show_load_warning(): avviso tipo vault + file count + stima tempo prima del caricamento
- Progress bar ChromaDB durante ri-indicizzazione al caricamento conversazione

**v1.13.6 — Fix progress callback + stima tempo**
- _progress_cb con firma universale (*args) compatibile con tutte le fasi
- Stima tempo corretta: ~0.4s per file con formattazione automatica secondi/minuti

**v1.13.7 — Conferma caricamento vault + icone vault**
- Conferma a 2 step (≥50 file): "✅ Procedi" / "❌ Annulla" con avviso e stima
- Icone vault specifiche nelle conversazioni: 🧠🟣 Obsidian, 🧠🟤 LogSeq, 🧠⬛ Notion
- core/persistence.py: kb_folder_path esposto in list_saved_conversations()
- _has_heavy_kb() — soglia 50 file per attivare la conferma

**v1.13.8 — Fix nome modello bottoni socratici**
- model_used passato esplicitamente a render_socratic_buttons()
- Cambiare modello non altera più il footer delle risposte già generate

**v1.13.9 — Fix modello per esplorazione socratica specifica**
- Cache modello dedicata per ogni esplorazione (socratic_model_{action}_{idx})
- _render_model_timestamp() con priorità: cache specifica → model_used → current_model
- Ogni bottone socratico mostra il modello che ha generato quella specifica esplorazione

### v1.12.0 — Architettura Sidebar ✅
**Data:** 2026-03-05
- Sidebar riorganizzata in 5 sezioni con ordine fisso
- ⚙️ Configurazione in st.expander chiuso di default
- Banner versione dinamico da costante VERSION

### v1.11.1 — Matrix Theme ✅
**Data:** 2026-02-27

**Nuovi file:**
- `.streamlit/config.toml`: Tema Streamlit nativo (primaryColor, bg, font monospace)
- `ui/style.py`: `inject_matrix_style()`, `_inject_css()`, `_inject_matrix_rain()`

**Modifiche:**
- [x] `app.py`: +import `inject_matrix_style`, chiamata subito dopo `st.set_page_config()`
- [x] `ui/__init__.py`: +import e +`__all__` entry per `inject_matrix_style`
- [x] `config/constants.py`: VERSION → 1.11.1, VERSION_DESCRIPTION → "Matrix Theme"
- [x] `config/branding.py`: +`MATRIX_RAIN_ENABLED`, +`MATRIX_RAIN_INTENSITY`, merge scalari in `load_branding()`
- [x] `branding.yaml`: +`matrix_rain` (on/off), +`matrix_rain_intensity` (opacità configurabile)
- [x] CSS completo: scanlines CRT, glitch H1, tipografia (Cinzel/Exo 2/Share Tech Mono)
- [x] Matrix rain canvas nel parent document (escape iframe), opacity configurabile
- [x] Scrollbar teal 3px, padding-top ridotto

### v1.11.0 — Branding + UX Polish ✅
**Data:** 2026-02-24

**Nuovi file:**
- `branding.yaml`: Personalizzazione titolo, icona e banner novità
- `config/branding.py`: `load_branding()` + 6 costanti (APP_TITLE, APP_ICON, APP_SUBTITLE, NEWS_BANNER_*)

**Modifiche:**
- [x] `config/__init__.py`: +12 export (6 branding + 4 session map)
- [x] `app.py`: Hardcoded → costanti branding, nudge spostato in sidebar
- [x] `ui/socratic/buttons.py`: +`_render_model_timestamp()` nei 5 expander
- [x] `ui/socratic/session_map.py`: Parser riscritto con regex + fallback robusto
- [x] `ui/sidebar/session_map_widget.py`: Mappa collassabile, popover tooltip, bottoni genera/rigenera
- [x] `ui/sidebar/conversations.py`: Reset stato F2 su caricamento conversazione
- [x] VERSION → 1.11.0

### v1.10.0 — Mappa Sessione (F2) ✅
**Data:** 2026-02-23
**Filosofia:** Attrito sul pensiero, non sulla risposta.
La Mappa Sessione rende visibile la cornice interpretativa invisibile
che si costruisce domanda dopo domanda (sovrascopo — Ligas).
Generata solo su richiesta esplicita dell'utente (delega consapevole — Quartarone).

**Nuovi file:**
- `ui/socratic/session_map.py`: SessionMapEntry, SessionMap, SessionMapAnalyzer
- `ui/sidebar/session_map_widget.py`: settings, nudge, display, tooltip

**Modifiche:**
- [x] `config/constants.py`: +SESSION_MAP_MODES, +3 costanti, VERSION → 1.10.0
- [x] `ui/socratic/__init__.py`: +6 export F2
- [x] `app.py`: +4 session_state keys, logica post-risposta, nudge sidebar, reset
- [x] 3 modalità: Progressiva / A soglia (default) / Disattivata
- [x] Nudge una sola volta per sessione
- [x] Tooltip "?" con crediti filosofici
- [x] Privacy-first: stesso client LLM, nessuna rete esterna aggiuntiva

### v1.9.2 — Prompt Epistemologici Potenziati ✅
**Data:** Febbraio 2026
**Filosofia:** Profondità epistemologica senza automazione.
I 5 prompt socratici riscritti con framework esplicito (Floridi/Eco/Quartarone).
Il test epistemologico resta all'umano: nessun validatore automatico AI-su-AI.

**Modifiche:**
- `ui/socratic/prompts.py`: 5 template potenziati
  - Alternative → 3 tipi distinti (Soluzione / Framing / Assunzione)
  - Assunzioni → tri-classificazione Fatti / Inferenze / Valutazioni + Test della Premessa
  - Limiti → Dominio / Contesto / Modello (Lettore Implicito da Eco)
  - Confuta → 2 livelli (Conclusioni + Struttura argomentativa)
  - Rifletti → 3 dimensioni (Presupposizioni / Destinatario Implicito / Domanda sotto la Domanda)

Nessun altro file modificato.

### v1.9.1 - 🎨 UI Polish + Cloud Config + Privacy Granulare (2026-02-11)
- [x] Chat bubble rendering unificato: singola `st.markdown()` con `markdown-it-py`
- [x] Colori dark/light professionali: dark default, light via `@media (prefers-color-scheme: light)`
- [x] Tipografia HTML completa dentro bolle (p, strong, a, code, pre, table, ul/ol)
- [x] `cloud_models.yaml`: config modelli cloud YAML-based (pattern `remote_servers.yaml`)
- [x] Sezione Cloud riscritta: YAML-first con selectbox modelli + fallback hardcoded
- [x] Parametri LLM in `st.expander` collassabile
- [x] `conversation_has_sensitive_content()` con euristica wiki/folder/attachments
- [x] Icone granulari conversazioni: 📚 Wiki, 📁 Cartella, 📎 Allegati, 🔒 su cloud
- [x] Warning cambio provider: avviso quando si passa a Cloud con dati sensibili in sessione
- [x] 3 livelli protezione privacy: Dialog → Warning → Hard block

### v1.9.0 - 📋 Socratic History + Persistence (2026-02-06)
- [x] `SocraticExploration` dataclass (7 campi: timestamp, button_type, original_question, ai_response_snippet, socratic_result, session_id, msg_index)
- [x] `SocraticHistory` classe con 8 metodi statici (add, get, stats, clear, serialize, load)
- [x] Widget sidebar: conteggi, breakdown per tipo, ultime 10 esplorazioni, cancellazione con conferma
- [x] Persistenza esplorazioni nel JSON conversazione (save/load/restore)
- [x] Auto-save dopo ogni esplorazione socratica (dirty flag pattern)
- [x] Sync cache UI: pulizia + ricostruzione cache expander al caricamento
- [x] Retrocompatibilità con conversazioni senza socratic_history
- [x] Privacy-first: dati in session_state + file locale JSON

### v1.8.0 - 🧠 UI Socratica Completa (2026-02-05)
- [x] Bottone "🎭 Confuta" - Avvocato del diavolo (punti deboli, falle logiche, controesempi)
- [x] Bottone "🪞 Rifletti" - Sfida la DOMANDA utente (perimetro decisionale, assunzioni non dette)
- [x] Toggle Modalità Socratica (sidebar): Veloce / Standard / Socratico
- [x] UI raggruppata in 2 sezioni: "Analizza la risposta" + "Sfida la domanda"
- [x] SOCRATIC_MODES dict in config/constants.py
- [x] Passaggio user_question a render_socratic_buttons per "Rifletti"
- [x] Rebranding completo: "Datapizza" → "DeepAiUG" in tutti i commenti

### v1.7.1 - 🖥️ Remote Servers + Security (2026-01-29)
- [x] `remote_servers.yaml` - Configurazione centralizzata server Ollama remoti
- [x] 3 modalità operative: fixed, selectable, custom_allowed
- [x] Lista modelli dinamica con bottone "🔄 Aggiorna modelli"
- [x] Funzioni loader in `config/settings.py` (pattern wiki_sources)
- [x] `security_settings.yaml` - Controllo visibilità API Keys Cloud
- [x] Default sicuro: keys nascoste, non copiabili
- [x] Bottone "🔄 Usa altra key" per cambio senza visualizzazione
- [x] Rebranding: "🍕 Datapizza" → "🧠 DeepAiUG"
- [x] Bugfix: Cloud API Key ora modificabile

### v1.7.0 - 🧠 Socratic Expansion (2026-01-27)
- [x] Bottone "🤔 Assunzioni" - Mostra assunzioni implicite della risposta
- [x] Bottone "⚠️ Limiti" - Mostra quando la risposta non funziona
- [x] Layout 3 bottoni indipendenti con cache separata
- [x] 3 expander con caption contestuali
- [x] Funzioni generate_assumptions() e generate_limits()

### v1.6.1 - 🧠 Socratic Buttons (2026-01-26)
- [x] Nuovo modulo `ui/socratic/`
- [x] Bottone "🔄 Genera alternative" sotto ogni risposta AI
- [x] Genera 3 interpretazioni alternative con presupposti diversi
- [x] Cache risposte socratiche in session_state
- [x] Integrazione con streaming esistente

### v1.6.0 - Streaming Responses (2026-01-25)
- [x] Streaming token-by-token per Ollama locale
- [x] Streaming token-by-token per Remote host
- [x] Implementazione con client.stream_invoke()
- [x] UI aggiornata con st.write_stream()
- [x] Footer rinominato: 🤖 DeepAiUG by Gilles

### v1.5.x - File Upload + Privacy (2026-01-11/16)
- [x] Upload file in chat (PDF, DOCX, TXT, MD)
- [x] Upload immagini per modelli Vision
- [x] Privacy-First: Upload bloccato su Cloud provider
- [x] Privacy Dialog per passaggio Local→Cloud
- [x] Wiki Bugfix + 4 wiki pubbliche di test

### v1.4.x - Architettura Modulare (2026-01-08/09)
- [x] Refactoring da monolite a packages (27 moduli)
- [x] DokuWikiAdapter + Multi-Wiki support
- [x] Entry point: `app.py`

### v1.3.x - Knowledge Base RAG (2026-01-05/07)
- [x] Sistema RAG completo con ChromaDB
- [x] LocalFolderAdapter + MediaWikiAdapter
- [x] Chunking intelligente configurabile
- [x] Privacy mode (blocco cloud con KB)

### v1.0.0 → v1.2.0 - Base (2026-01-01/04)
- [x] Multi-provider: Ollama, Remote, Cloud
- [x] Conversazioni multi-turno + Persistenza
- [x] Export: MD, JSON, TXT, PDF, ZIP

---

## 📋 Pianificate

### v2.0.0 - Preparazione Semantic Layer
- [ ] Metadati JSON-LD sui documenti
- [ ] Export RDF base
- [ ] Template ontologie per settore
- [ ] Wizard "Definisci la tua semantica"

---

## 🎯 Obiettivi Futuri (v2.0.0)

### Semantic Layer Completo
- [ ] Knowledge Graph con NetworkX/Neo4j
- [ ] Validazione SHACL
- [ ] Query SPARQL
- [ ] RAG ibrido (vector + graph)

### Journaling Riflessivo
- [ ] Salvataggio riflessioni utente
- [ ] Tracking crescita capitale semantico
- [ ] Report settimanale apprendimento

### Docker & Deployment
- [ ] Dockerfile ottimizzato
- [ ] Docker Compose con Ollama
- [ ] Deployment one-click

### API REST
- [ ] Endpoint REST per integrazioni
- [ ] Authentication API
- [ ] Documentazione OpenAPI

---

## 🛠️ Architettura Attuale (v1.14.0)

```
datapizza-streamlit-interface/
├── app.py                    # Entry point
├── .streamlit/config.toml    # Tema Streamlit nativo (NEW v1.11.1)
├── wiki_sources.yaml         # Config sorgenti
├── remote_servers.yaml       # Config server remoti
├── cloud_models.yaml         # Config modelli cloud (NEW v1.9.1)
├── security_settings.yaml    # Impostazioni sicurezza
├── branding.yaml             # Personalizzazione UI + Matrix rain (v1.11.0/v1.11.1)
│
├── config/                   # Configurazione
│   ├── constants.py          # VERSION, PATHS, WIKI_TYPES, SOCRATIC_MODES
│   ├── settings.py           # Loaders, API keys
│   └── branding.py           # load_branding() + 8 costanti (v1.11.0/v1.11.1)
│
├── core/                     # Logica core
│   ├── llm_client.py         # Factory LLM
│   ├── conversation.py       # Messaggi
│   ├── persistence.py        # Salvataggio (+ socratic_history + sensitivity detection)
│   └── file_processors.py    # File upload extraction
│
├── rag/                      # Sistema RAG
│   ├── models.py             # Document, Chunk
│   ├── chunker.py            # TextChunker
│   ├── vector_store.py       # ChromaDB
│   ├── manager.py            # Orchestrazione
│   └── vault.py              # ⭐ F3: detect, scan, parse canvas, update (v1.13.0)
│   └── adapters/
│       ├── local_folder.py   # File locali
│       ├── mediawiki.py      # MediaWiki
│       └── dokuwiki.py       # DokuWiki
│
├── export/                   # Export
│   └── exporters.py          # MD, JSON, TXT, PDF, ZIP
│
└── ui/                       # Interfaccia
    ├── styles.py
    ├── style.py              # Matrix Theme CSS + rain (NEW v1.11.1)
    ├── chat.py               # Integrato con socratic
    ├── file_upload.py
    ├── privacy_warning.py
    ├── socratic/             # 🧠 5 bottoni + history + session map
    │   ├── __init__.py
    │   ├── prompts.py        # 5 template (alternative, assumptions, limits, confute, reflect)
    │   ├── buttons.py        # 5 bottoni + registrazione esplorazioni
    │   ├── history.py        # SocraticExploration + SocraticHistory
    │   ├── history_widget.py # Widget sidebar storico esplorazioni
    │   └── session_map.py    # ⭐ SessionMap + SessionMapAnalyzer (F2)
    └── sidebar/
        ├── llm_config.py
        ├── knowledge_base.py
        ├── conversations.py  # + load socratic history
        ├── export_ui.py
        └── session_map_widget.py  # ⭐ Widget mappa sessione (F2)
```

---

## 📦 Dipendenze per Feature

| Feature | Pacchetti |
|---------|-----------|
| Core | streamlit, datapizza-ai |
| RAG | chromadb, beautifulsoup4, PyPDF2 |
| MediaWiki | mwclient |
| DokuWiki | dokuwiki |
| Export PDF | reportlab |
| File Upload | python-docx, Pillow |
| Semantic (futuro) | rdflib, pyshacl, networkx |

---

## 🤝 Come Contribuire

1. Scegli una feature dalla roadmap
2. Apri una Issue per discuterne
3. Fork → Branch → PR
4. Segui le convenzioni del progetto

Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per dettagli.

---

*Ultimo aggiornamento: 2026-03-09*
*DeepAiUG Streamlit Interface © 2026*
