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
   └─→ v2.0.0 🎯 (Q2-Q3 2026)   + Semantic Layer + Knowledge Graph

✅ = Completata
🚧 = In sviluppo
📋 = Pianificata
🎯 = Obiettivo futuro
🧠 = Feature Socratica
```

---

## ✅ Completate

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

## 🛠️ Architettura Attuale (v1.9.0)

```
datapizza-streamlit-interface/
├── app.py                    # Entry point
├── wiki_sources.yaml         # Config sorgenti
├── remote_servers.yaml       # Config server remoti
├── security_settings.yaml    # Impostazioni sicurezza
│
├── config/                   # Configurazione
│   ├── constants.py          # VERSION, PATHS, WIKI_TYPES, SOCRATIC_MODES
│   └── settings.py           # Loaders, API keys
│
├── core/                     # Logica core
│   ├── llm_client.py         # Factory LLM
│   ├── conversation.py       # Messaggi
│   ├── persistence.py        # Salvataggio (+ socratic_history)
│   └── file_processors.py    # File upload extraction
│
├── rag/                      # Sistema RAG
│   ├── models.py             # Document, Chunk
│   ├── chunker.py            # TextChunker
│   ├── vector_store.py       # ChromaDB
│   ├── manager.py            # Orchestrazione
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
    ├── chat.py               # Integrato con socratic
    ├── file_upload.py
    ├── privacy_warning.py
    ├── socratic/             # 🧠 v1.9.0 - 5 bottoni + history
    │   ├── __init__.py
    │   ├── prompts.py        # 5 template (alternative, assumptions, limits, confute, reflect)
    │   ├── buttons.py        # 5 bottoni + registrazione esplorazioni
    │   ├── history.py        # ⭐ SocraticExploration + SocraticHistory
    │   └── history_widget.py # ⭐ Widget sidebar storico esplorazioni
    └── sidebar/
        ├── llm_config.py
        ├── knowledge_base.py
        ├── conversations.py  # + load socratic history
        └── export_ui.py
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

*Ultimo aggiornamento: 2026-02-06*
*DeepAiUG Streamlit Interface © 2026*
