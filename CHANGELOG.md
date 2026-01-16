# 📝 CHANGELOG

Tutte le modifiche significative al progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e il progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

---

## [1.5.1] - 2025-01-16

### 🐛 Bug Fix

- **CRITICAL FIX**: Wiki non funzionavano per pacchetti mancanti
  - Problema: `mwclient` e `dokuwiki` non erano installati nel venv
  - Soluzione: Aggiornato README con istruzioni installazione dipendenze
  - Test: Verificata connessione con Wikipedia e altre wiki pubbliche

### ✨ Novità

- **Wiki Pubbliche di Test**: Aggiunte 4 wiki pronte all'uso in `wiki_sources.yaml`
  - 🌍 Wikipedia IT - Intelligenza Artificiale (30 pagine)
  - 🌎 Wikipedia EN - Artificial Intelligence (20 pagine)
  - ✈️ Wikivoyage IT - Guide viaggio Italia (15 pagine)
  - 📚 Wikibooks IT - Manuali Informatica (20 pagine)

### 🔧 Miglioramenti

- Cambiato `default_source` da wiki non esistente a `wikipedia_it`
- Aggiunti script di test: `test_wiki.py` e `test_all_wikis.py`
- Migliorata documentazione setup venv e dipendenze

### 📚 Documentazione

- README aggiornato con sezione "Setup Virtual Environment"
- Istruzioni chiare per installazione dipendenze wiki
- Esempi di utilizzo wiki pubbliche per test

---

## [1.5.0] - 2025-01-11

### ✨ Novità

- **File Upload in Chat**: Possibilità di allegare file direttamente nella chat
  - 📄 Documenti supportati: PDF, TXT, MD, DOCX
  - 🖼️ Immagini supportate: PNG, JPG, JPEG, GIF, WEBP (richiede modello Vision)
  - Anteprima file prima dell'invio
  - Contenuto documenti estratto e aggiunto automaticamente al prompt

- **Privacy-First Upload**: Upload automaticamente disabilitato con Cloud provider
  - Protegge i documenti sensibili dall'invio a servizi esterni
  - Disponibile solo con Ollama locale e Remote host

- **Rilevamento Modelli Vision**: Riconoscimento automatico modelli con supporto immagini
  - LLaVA, Granite3.2-Vision, Moondream, BakLLaVA e altri
  - Warning se si caricano immagini con modello non-Vision

- **🔐 Privacy Dialog per passaggio Local→Cloud**: Protezione dati sensibili
  - Warning automatico quando si passa a Cloud con documenti in memoria
  - Due opzioni: Reset Chat (consigliato) o Procedi con conferma esplicita
  - Banner di promemoria quando si usa Cloud con documenti in sessione

### 🔧 Modifiche Tecniche

- Aggiunto campo `attachments` nei messaggi per tracciare file allegati
- Nuovi moduli: `core/file_processors.py`, `ui/file_upload.py`, `ui/privacy_warning.py`
- Aggiornato `ui/chat.py` per mostrare allegati nei messaggi utente

### 📦 Dipendenze

- Aggiunto: `python-docx>=0.8.0`
- Aggiunto: `Pillow>=10.0.0`

---

## [1.4.1] - 2025-01-09

### ✨ Nuove Funzionalità

- **Supporto Multi-Wiki**: Oltre a MediaWiki, ora supporta anche **DokuWiki**
- **Nuovo formato `wiki_sources.yaml`**: Campo `type` per specificare il tipo di sorgente
- **UI Multi-Tipo**: Selezione sorgenti con icone e raggruppamento per tipo
- **Configurazione YAML estendibile**: Pronto per futuri tipi wiki (Confluence, BookStack)

### Aggiunto

- **rag/adapters/dokuwiki.py** - Nuovo adapter per wiki DokuWiki
  - Connessione via XML-RPC
  - Download pagine con filtro namespace
  - Parsing DokuWiki syntax → testo pulito
  - Cache locale sync info

- **config/constants.py**
  - `WIKI_TYPES` - Dizionario tipi wiki supportati con metadata

- **config/settings.py** - Nuove funzioni:
  - `get_available_sources()` - Lista tutte le sorgenti
  - `get_sources_by_type()` - Filtra per tipo
  - `get_source_adapter_config()` - Config generica
  - `is_source_type_available()` - Verifica dipendenze
  - `get_missing_package()` - Pacchetto mancante

### Modificato

- **wiki_sources.yaml** - Nuovo formato con:
  - `sources:` invece di `wikis:` (retrocompatibile)
  - Campo `type:` obbligatorio (mediawiki, dokuwiki, local)
  - Campo `icon:` per personalizzazione UI
  
- **ui/sidebar/knowledge_base.py** - Riscritto per supporto multi-tipo
  - Fix: Cartella locale da YAML ora mostra tutti i campi configurazione

### 📦 Nuove Dipendenze

- `dokuwiki>=0.1.0` - Client Python per DokuWiki XML-RPC

---

## [1.4.0] - 2025-01-08

### ♻️ Refactoring Completo - Architettura Modulare

Il file monolitico v1.3.3 (2287 righe) è stato completamente riorganizzato in una struttura pulita di packages Python.

### ✨ Nuova Struttura

```
datapizza-streamlit-interface/
├── app.py                    # Entry point principale
├── config/                   # Configurazione (constants, settings)
├── core/                     # LLM client, persistenza, conversazioni
├── rag/                      # RAG: models, chunker, vector_store, adapters
├── export/                   # Export: MD, JSON, TXT, PDF, ZIP
├── ui/                       # Streamlit UI: styles, chat, sidebar
└── old/                      # Versioni archiviate (v1.0 → v1.3.3)
```

### 🔧 Miglioramenti

- **Separazione responsabilità**: Ogni modulo ha un compito specifico
- **Testabilità**: Componenti isolati e facilmente testabili
- **Manutenibilità**: Modifiche localizzate senza impatti globali
- **Riusabilità**: Componenti importabili in altri progetti
- **Import puliti**: Ogni package espone API chiare via `__init__.py`

---

## [1.3.3] - 2025-01-07

### 🐛 Bug Fix

- **Ripristino Export Conversazioni**: La sezione export era stata persa nella v1.3.0+

### ✨ Funzionalità Ripristinate

- **📤 Export Conversazione** nella sidebar
- **👁️ Anteprima Export**: Preview del contenuto prima del download
- **🗂️ Batch Export**: Esportazione di tutte le conversazioni in ZIP

---

## [1.3.2] - 2025-01-07

### ✨ Nuove Funzionalità

- **MediaWikiAdapter**: Nuovo adapter per sincronizzare wiki MediaWiki
- **Configurazione YAML** (`wiki_sources.yaml`)
- **UI MediaWiki in Sidebar**

### 📦 Nuove Dipendenze

- `mwclient>=0.10.0` - Client Python per MediaWiki API
- `pyyaml>=6.0` - Parser YAML per configurazione

---

## [1.3.1] - 2025-01-06

### 🐛 Bug Fix

- **Fix Modelli Ollama** (CRITICO): Ora mostra tutti i modelli Ollama installati
- **Fix Persistenza KB**: Le impostazioni Knowledge Base vengono salvate
- **Fix Ricarica KB**: Ricaricamento automatico della KB

### ✨ Nuove Funzionalità

- **Parametri Chunking Configurabili**
- **Chunking Intelligente**

---

## [1.3.0] - 2025-01-05

### ✨ Nuove Funzionalità

- **📚 Knowledge Base RAG**: Sistema completo di Retrieval-Augmented Generation
- **📁 LocalFolderAdapter**: File locali (MD, TXT, HTML, PDF)
- **🔒 Privacy Mode**: Blocco automatico provider cloud quando KB attiva

### 📦 Nuove Dipendenze

- `chromadb>=0.4.0`
- `beautifulsoup4>=4.12.0`
- `PyPDF2>=3.0.0`

---

## [1.2.0] - 2025-01-04

### ✨ Nuove Funzionalità

- **📥 Export Multi-Formato**: MD, JSON, TXT, PDF
- **🗂️ Batch Export ZIP**

### 📦 Nuove Dipendenze

- `reportlab>=4.0.0`

---

## [1.1.x] - 2025-01-02/03

### ✨ Nuove Funzionalità

- **💬 Conversazioni Multi-Turno**
- **💾 Persistenza Conversazioni**
- **🔄 Auto-Save**

---

## [1.0.0] - 2025-01-01

### 🎉 Release Iniziale

- **🤖 Multi-Provider**: Ollama, Remote, Cloud
- **☁️ Cloud Provider**: OpenAI, Anthropic, Google
- **🎨 UI Streamlit**

---

## Legenda

- ✨ **Nuove Funzionalità**
- 🐛 **Bug Fix**
- 🔧 **Miglioramenti**
- ♻️ **Refactoring**
- 📦 **Dipendenze**

---

*Datapizza Streamlit Interface - DeepAiUG © 2025*
