# 🗺️ ROADMAP - Datapizza Streamlit Interface

Piano di sviluppo del progetto.

---

## 📊 Overview Versioni

```
v1.0.0 ✅ (2025-01-01)          Base interface + Multi-provider
   │
   ├─→ v1.1.0 ✅ (2025-01-02)   + Multi-turn conversations + Persistenza
   │
   ├─→ v1.2.0 ✅ (2025-01-04)   + Export (MD, JSON, TXT, PDF, ZIP)
   │
   ├─→ v1.3.0 ✅ (2025-01-05)   + Knowledge Base RAG + LocalFolder
   │
   ├─→ v1.3.1 ✅ (2025-01-06)   + Fix Ollama + Chunking configurabile
   │
   ├─→ v1.3.2 ✅ (2025-01-07)   + MediaWiki Adapter + YAML config
   │
   ├─→ v1.3.3 ✅ (2025-01-07)   + Ripristino Export completo
   │
   ├─→ v1.4.0 ✅ (2025-01-08)   + Architettura Modulare (27 moduli)
   │
   ├─→ v1.4.1 ✅ (2025-01-09)   + Multi-Wiki (DokuWiki) + UI migliorata
   │
   ├─→ v1.5.0 ✅ (2025-01-11)   + File Upload in Chat + Privacy Protection
   │
   ├─→ v1.5.1 ✅ (2025-01-16)   + Wiki Bugfix + Test Sources
   │
   ├─→ v1.6.0 📋 (Q1 2025)      + Streaming responses
   │
   ├─→ v1.7.0 📋 (Q1 2025)      + Model comparison side-by-side
   │
   ├─→ v1.8.0 📋 (Q2 2025)      + Altri wiki adapters (Confluence, BookStack)
   │
   └─→ v2.0.0 🎯 (Q3 2025)      + Multimodal + Docker + API REST

✅ = Completata
🚧 = In sviluppo
📋 = Pianificata
🎯 = Obiettivo futuro
```

---

## ✅ Completate

### v1.0.0 - Base Interface (2025-01-01)
- [x] Multi-provider: Ollama locale, Remote host, Cloud
- [x] Cloud providers: OpenAI, Anthropic, Google Gemini
- [x] Parametri LLM: System prompt, temperature, modello
- [x] Chat base con invio messaggi
- [x] UI Streamlit moderna
- [x] Gestione API keys (file + env)

### v1.1.x - Conversazioni (2025-01-02/03)
- [x] Conversazioni multi-turno con memoria
- [x] Persistenza su file JSON
- [x] Gestione conversazioni (lista, carica, elimina)
- [x] Auto-save configurabile
- [x] Statistiche (messaggi, token, ID)

### v1.2.0 - Export (2025-01-04)
- [x] Export Markdown
- [x] Export JSON
- [x] Export TXT
- [x] Export PDF
- [x] Batch export ZIP
- [x] Preview export
- [x] Nome file personalizzabile

### v1.3.x - Knowledge Base RAG (2025-01-05/07)
- [x] Sistema RAG completo
- [x] Vector store ChromaDB + fallback memoria
- [x] LocalFolderAdapter (MD, TXT, HTML, PDF)
- [x] MediaWikiAdapter con mwclient
- [x] Chunking intelligente configurabile
- [x] Privacy mode (blocco cloud con KB)
- [x] Configurazione YAML (`wiki_sources.yaml`)
- [x] Citazione fonti nelle risposte

### v1.4.0 - Architettura Modulare (2025-01-08)
- [x] Refactoring da monolite a packages
- [x] 27 moduli in 6 packages
- [x] Entry point: `app.py`
- [x] Import puliti via `__init__.py`
- [x] Archiviazione versioni precedenti in `old/`

### v1.4.1 - Multi-Wiki Support (2025-01-09)
- [x] DokuWikiAdapter
- [x] Nuovo formato YAML con campo `type`
- [x] UI multi-tipo con icone
- [x] Retrocompatibilità vecchio formato
- [x] Verifica dipendenze automatica
- [x] Fix UI cartella locale da YAML

### v1.5.0 - File Upload + Privacy Protection (2025-01-11)
- [x] Upload file in chat (PDF, DOCX, TXT, MD)
- [x] Upload immagini per modelli Vision
- [x] Privacy-First: Upload bloccato su Cloud provider
- [x] Privacy Dialog per passaggio Local→Cloud
- [x] Banner warning con documenti in memoria
- [x] Rilevamento automatico modelli Vision
- [x] File processors modulari

### v1.5.1 - Wiki Bugfix + Test Sources (2025-01-16)
- [x] CRITICAL FIX: Wiki non funzionavano (mwclient/dokuwiki mancanti)
- [x] Aggiunte 4 wiki pubbliche di test (Wikipedia IT/EN, Wikivoyage, Wikibooks)
- [x] Script test: test_wiki.py e test_all_wikis.py
- [x] Fix default_source in wiki_sources.yaml
- [x] Documentazione migliorata setup venv

---

## 📋 Pianificate

### v1.6.0 - Streaming Responses
- [ ] Streaming token-by-token
- [ ] Progress indicator durante generazione
- [ ] Stop generation button
- [ ] Migliore UX per risposte lunghe

### v1.7.0 - Model Comparison
- [ ] Confronto side-by-side
- [ ] Stesso prompt a modelli diversi
- [ ] Metriche comparazione (tempo, token, qualità)
- [ ] Export comparazione

### v1.8.0 - Wiki Adapters Aggiuntivi
- [ ] ConfluenceAdapter (Atlassian)
- [ ] BookStackAdapter
- [ ] NotionAdapter
- [ ] Wiki.js Adapter

### v1.9.0 - Analytics & Stats
- [ ] Dashboard statistiche uso
- [ ] Grafici token consumati
- [ ] History query RAG
- [ ] Performance metrics

---

## 🎯 Obiettivi Futuri (v2.0.0)

### Multimodal
- [ ] Supporto immagini in chat
- [ ] Vision models (LLaVA, GPT-4V)
- [ ] Analisi documenti con immagini
- [ ] OCR integrato

### Docker & Deployment
- [ ] Dockerfile ottimizzato
- [ ] Docker Compose con Ollama
- [ ] Deployment one-click
- [ ] Configurazione via env vars

### API REST
- [ ] Endpoint REST per integrazioni
- [ ] Authentication API
- [ ] Rate limiting
- [ ] Documentazione OpenAPI

### Avanzate
- [ ] Plugin system
- [ ] Temi personalizzabili
- [ ] Multi-utente con profili
- [ ] Backup cloud conversazioni

---

## 🛠️ Architettura Attuale (v1.5.1)

```
datapizza-streamlit-interface/
├── app.py                    # Entry point
├── wiki_sources.yaml         # Config sorgenti
│
├── config/                   # Configurazione
│   ├── constants.py          # VERSION, PATHS, WIKI_TYPES
│   └── settings.py           # Loaders, API keys
│
├── core/                     # Logica core
│   ├── llm_client.py         # Factory LLM
│   ├── conversation.py       # Messaggi
│   ├── persistence.py        # Salvataggio
│   └── file_processors.py    # ✨ File upload extraction
│
├── rag/                      # Sistema RAG
│   ├── models.py             # Document, Chunk
│   ├── chunker.py            # TextChunker
│   ├── vector_store.py       # ChromaDB
│   ├── manager.py            # Orchestrazione
│   └── adapters/
│       ├── local_folder.py   # File locali
│       ├── mediawiki.py      # MediaWiki
│       └── dokuwiki.py       # DokuWiki ✨ NEW
│
├── export/                   # Export
│   └── exporters.py          # MD, JSON, TXT, PDF, ZIP
│
└── ui/                       # Interfaccia
    ├── styles.py
    ├── chat.py
    ├── file_upload.py        # ✨ File upload widget
    ├── privacy_warning.py    # ✨ Privacy dialog
    └── sidebar/
        ├── llm_config.py
        ├── knowledge_base.py # Multi-wiki support
        ├── conversations.py
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

---

## 🤝 Come Contribuire

1. Scegli una feature dalla roadmap
2. Apri una Issue per discuterne
3. Fork → Branch → PR
4. Segui le convenzioni del progetto

Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per dettagli.

---

*Ultimo aggiornamento: 2025-01-16*
*Datapizza Streamlit Interface - DeepAiUG © 2025*
