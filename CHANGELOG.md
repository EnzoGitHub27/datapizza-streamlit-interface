# 📝 CHANGELOG

Tutte le modifiche significative al progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e il progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

---

## [1.3.1] - 2025-01-06

### 🐛 Bug Fix

- **Fix Modelli Ollama** (CRITICO): Ora mostra tutti i modelli Ollama installati, non solo quelli con `-` nel nome
- **Fix Persistenza KB**: Le impostazioni Knowledge Base vengono salvate con la conversazione
- **Fix Ricarica KB**: Ricaricamento automatico della KB quando si carica una conversazione salvata

### ✨ Nuove Funzionalità

- **Parametri Chunking Configurabili**: Nuovi slider per dimensione chunk (200-3000) e overlap (0-500)
- **Chunking Intelligente**: Il chunker ora rispetta la struttura del documento (titoli Markdown, paragrafi, frasi)
- **Ratio Overlap**: Visualizzazione percentuale dell'overlap configurato

### 🔧 Miglioramenti Tecnici

- Normalizzazione whitespace eccessivo nei documenti
- Migliore gestione dei separatori nel chunking
- Safety check per evitare loop infiniti nel chunker

---

## [1.3.0] - 2025-01-05

### ✨ Nuove Funzionalità

- **📚 Knowledge Base RAG**: Sistema completo di Retrieval-Augmented Generation
  - Indicizzazione documenti locali (Markdown, TXT, HTML, PDF)
  - Vector store con ChromaDB (persistente) o fallback in memoria
  - Ricerca semantica nei documenti
  - Contesto automatico iniettato nel prompt
  - Citazione fonti nelle risposte

- **📁 LocalFolderAdapter**: Primo adapter per sorgenti documentali
  - Supporto cartelle ricorsive
  - Filtro per estensioni file
  - Parsing HTML (BeautifulSoup)
  - Estrazione testo PDF (PyPDF2)

- **🔒 Privacy Mode**: Blocco automatico provider cloud quando KB attiva
  - Solo Ollama locale o Remote host permessi
  - Protezione dati sensibili

- **⚙️ Configurazione KB in Sidebar**:
  - Selezione sorgente documenti
  - Scelta formati file
  - Statistiche knowledge base
  - Parametri RAG (top_k documenti)

### 📦 Nuove Dipendenze

- `chromadb>=0.4.0` - Database vettoriale
- `beautifulsoup4>=4.12.0` - Parsing HTML
- `PyPDF2>=3.0.0` - Estrazione testo PDF

---

## [1.2.0] - 2025-01-04

### ✨ Nuove Funzionalità

- **📥 Export Multi-Formato**: Esportazione conversazioni in:
  - Markdown (.md) - per blog, Obsidian, Notion
  - JSON (.json) - per elaborazione programmata
  - TXT (.txt) - backup semplice
  - PDF (.pdf) - documenti stampabili

- **👁️ Preview Export**: Anteprima del contenuto prima del download
- **📝 Nome File Personalizzabile**: Scelta del nome file per l'export
- **📊 Selezione Contenuto**: Export completo o ultimi N messaggi
- **🗂️ Batch Export**: Esportazione di tutte le conversazioni in ZIP

### 📦 Nuove Dipendenze

- `reportlab>=4.0.0` - Generazione PDF

---

## [1.1.1] - 2025-01-03

### 🐛 Bug Fix

- Fix salvataggio conversazioni con caratteri speciali
- Fix caricamento conversazioni corrotte
- Migliorata gestione errori nel salvataggio

### 🔧 Miglioramenti

- Auto-save più affidabile
- Feedback visivo migliorato per operazioni di salvataggio

---

## [1.1.0] - 2025-01-02

### ✨ Nuove Funzionalità

- **💬 Conversazioni Multi-Turno**: Memoria del contesto tra messaggi
- **💾 Persistenza Conversazioni**: Salvataggio automatico su file JSON
- **📂 Gestione Conversazioni**: Lista, caricamento, eliminazione conversazioni salvate
- **📊 Statistiche**: Contatore messaggi, token stimati, ID conversazione
- **🔄 Auto-Save**: Salvataggio automatico configurabile

### 🔧 Miglioramenti

- Nuova sidebar organizzata per sezioni
- Indicatori di stato connessione
- Gestione errori migliorata

---

## [1.0.0] - 2025-01-01

### 🎉 Release Iniziale

- **🤖 Multi-Provider**: Supporto Ollama (locale), Remote host, Cloud
- **☁️ Cloud Provider**: OpenAI, Anthropic (Claude), Google Gemini
- **🎛️ Parametri LLM**: System prompt, temperature, selezione modello
- **💬 Chat Base**: Invio messaggi e ricezione risposte
- **🎨 UI Streamlit**: Interfaccia moderna con tema chiaro/scuro
- **🔑 Gestione API Keys**: Salvataggio sicuro in file locali

---

## Legenda

- ✨ **Nuove Funzionalità** - Nuove feature aggiunte
- 🐛 **Bug Fix** - Correzione di bug
- 🔧 **Miglioramenti** - Miglioramenti a feature esistenti
- 📦 **Dipendenze** - Nuove librerie richieste
- ⚠️ **Breaking Changes** - Modifiche che richiedono azioni
- 🗑️ **Deprecato** - Feature che verranno rimosse
- 🔒 **Sicurezza** - Fix di sicurezza

---

*Datapizza Streamlit Interface - DeepAiUG © 2025*