# 🍕 Datapizza Streamlit LLM Interface

> Interfaccia Streamlit modulare per interagire con LLM locali (Ollama), remoti e cloud.
> Progetto Open Source della community **DeepAiUG**.

[![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)](https://github.com/EnzoGitHub27/datapizza-streamlit-interface)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- 🤖 **Multi-provider**: Ollama (locale), Remote host, Cloud (OpenAI, Anthropic, Google)
- 💬 **Conversazioni multi-turno** con memoria del contesto
- 💾 **Persistenza** delle conversazioni su file JSON
- 📥 **Export** in Markdown, JSON, TXT, PDF + Batch ZIP
- 📚 **Knowledge Base RAG** - Interroga documenti locali e wiki MediaWiki!
- 🔒 **Privacy-first** - Blocco automatico cloud quando usi documenti sensibili
- 🎨 **UI moderna** con temi chiaro/scuro
- ♻️ **Architettura modulare** - Codice organizzato in packages (v1.4.0)

---

## 🏗️ Architettura v1.4.0

```
datapizza-streamlit-interface/
├── app.py                    # ⭐ Entry point principale
├── wiki_sources.yaml         # Configurazione wiki MediaWiki
│
├── config/                   # 📁 Configurazione
│   ├── constants.py          # Costanti globali
│   └── settings.py           # Loader settings, API keys
│
├── core/                     # 📁 Logica core
│   ├── llm_client.py         # Factory client LLM
│   ├── conversation.py       # Gestione messaggi
│   └── persistence.py        # Salvataggio/caricamento
│
├── rag/                      # 📁 Sistema RAG
│   ├── models.py             # Document, Chunk
│   ├── chunker.py            # TextChunker intelligente
│   ├── vector_store.py       # ChromaDB + fallback
│   ├── manager.py            # KnowledgeBaseManager
│   └── adapters/             # Sorgenti dati
│       ├── base.py           # WikiAdapter (ABC)
│       ├── local_folder.py   # File locali
│       └── mediawiki.py      # API MediaWiki
│
├── export/                   # 📁 Sistema export
│   └── exporters.py          # MD, JSON, TXT, PDF, ZIP
│
├── ui/                       # 📁 Interfaccia utente
│   ├── styles.py             # CSS
│   ├── chat.py               # Rendering chat
│   └── sidebar/              # Componenti sidebar
│       ├── llm_config.py     # Config LLM
│       ├── knowledge_base.py # Config KB
│       ├── conversations.py  # Gestione salvataggi
│       └── export_ui.py      # UI export
│
├── old/                      # 📁 Versioni archiviate (v1.0-v1.3)
├── conversations/            # 📁 Conversazioni salvate (auto)
├── knowledge_base/           # 📁 Vector store ChromaDB (auto)
├── secrets/                  # 📁 API keys (opzionale)
└── examples/                 # 📁 Tutorial e esempi
```

---

## 🚀 Quick Start

### Prerequisiti

```bash
# Python 3.9+
python --version

# Ollama (per modelli locali)
ollama --version
ollama list  # verifica modelli installati
```

---

## 🚀 Installazione

### Metodo 1: Script Automatico (Consigliato) ⭐

Questo metodo gestisce automaticamente l'ordine di installazione dei pacchetti.

#### Linux/Mac
```bash
git clone https://github.com/EnzoGitHub27/datapizza-streamlit-interface.git
cd datapizza-streamlit-interface
chmod +x install.sh
./install.sh
```

> ⚠️ Se lo script non funziona, usa il **Metodo 2** (installazione manuale).

#### Windows (da testare)
```bash
git clone https://github.com/EnzoGitHub27/datapizza-streamlit-interface.git
cd datapizza-streamlit-interface
install.bat
```

Lo script ti chiederà quali provider cloud installare.

---

### Metodo 2: Installazione Manuale Passo-Passo

Se lo script automatico non funziona o preferisci installare manualmente:

#### 1. Clona il repository
```bash
git clone https://github.com/EnzoGitHub27/datapizza-streamlit-interface.git
cd datapizza-streamlit-interface
```

#### 2. Crea un ambiente virtuale (FORTEMENTE consigliato)
```bash
python3 -m venv deepaiug-interface
source deepaiug-interface/bin/activate  # Su Linux/Mac
# oppure
deepaiug-interface\Scripts\activate  # Su Windows
```

#### 3. Installa le dipendenze nell'ordine corretto

**⚠️ IMPORTANTE: L'ordine di installazione è cruciale!**

```bash
# 3.1 - Dipendenze base
pip install streamlit python-dotenv pyyaml reportlab

# 3.2 - Datapizza AI core (PRIMA dei client!)
pip install datapizza-ai

# 3.3 - Client provider cloud (DOPO datapizza-ai)
# Installa solo quelli che ti servono:

# Per Ollama in Locale
pip install datapizza-ai-clients-openai-like

# Per OpenAI (GPT-4, GPT-3.5, ecc.)
pip install datapizza-ai-clients-openai

# Per Anthropic Claude
pip install datapizza-ai-clients-anthropic

# Per Google Gemini
pip install datapizza-ai-clients-google

# 3.4 - Dipendenze RAG
pip install chromadb beautifulsoup4 PyPDF2

# 3.5 - MediaWiki (opzionale)
pip install mwclient
```

---

### Metodo 3: Usando requirements.txt

⚠️ **Nota**: Alcuni utenti hanno riscontrato problemi con questo metodo. Se fallisce, usa il **Metodo 2**.

```bash
pip install -r requirements.txt
```

Se riscontri errori, segui le istruzioni nel Metodo 2.

---

## 🔧 Configurazione API Keys

### Opzione A: File .env (Consigliata per sviluppo)

Crea un file `.env` nella root del progetto:

```env
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_API_KEY=your-google-gemini-key-here
```

### Opzione B: File secrets (Consigliata per produzione)

```bash
# Crea la cartella secrets se non esiste
mkdir -p secrets

# Crea i file per ogni provider
echo "sk-your-openai-key" > secrets/openai_key.txt
echo "sk-ant-your-anthropic-key" > secrets/anthropic_key.txt
echo "your-gemini-key" > secrets/google_key.txt
```

### Opzione C: Variabili d'ambiente di sistema

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export GOOGLE_API_KEY="your-key-here"

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
$env:GOOGLE_API_KEY="your-key-here"
```

### Opzione D: Interfaccia Web

Puoi anche inserire e salvare le API keys direttamente dall'interfaccia Streamlit!

---

## ▶️ Avvio

```bash
# Avvia l'interfaccia (v1.4.0+)
streamlit run app.py
```

### Versioni Precedenti (archiviate in `old/`)

```bash
# v1.3.3 - MediaWiki RAG + Export (monolitico)
streamlit run old/04_interfaccia_con_mediawiki.py

# v1.3.1 - Wiki RAG
streamlit run old/03_interfaccia_con_wiki_rag.py

# v1.2.0 - Export
streamlit run old/02_interfaccia_con_export.py

# v1.1.1 - Memoria
streamlit run old/01_interfaccia_con_memoria.py

# v1.0.0 - Base
streamlit run old/00_interfaccia_dinamica_datapizza_Streamlit.py
```

---

## 📚 Knowledge Base RAG

La funzionalità **RAG** ti permette di interrogare i tuoi documenti usando LLM!

### Sorgenti Supportate

| Sorgente | Descrizione | Formati |
|----------|-------------|---------|
| **Cartella Locale** | Documenti sul tuo PC | .md, .txt, .html, .pdf |
| **MediaWiki** | Wiki online (Wikipedia-like) | API MediaWiki |

### Come Funziona

```
┌─────────────────────────────────────────────────────────────────┐
│                    TUOI DOCUMENTI                               │
│  (Markdown, TXT, HTML, PDF locali o pagine MediaWiki)           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              INDICIZZAZIONE (ChromaDB)                          │
│  - Chunking intelligente (rispetta titoli/paragrafi)            │
│  - Embeddings vettoriali                                        │
│  - Storage locale persistente                                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CHAT RAG                                   │
│  1. Ricerca documenti rilevanti                                 │
│  2. Contesto iniettato nel prompt                               │
│  3. LLM risponde basandosi sui documenti                        │
│  4. Fonti citate nella risposta                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Setup Knowledge Base

1. **Attiva** "🔍 Usa Knowledge Base" nella sidebar
2. **Scegli sorgente**: Cartella Locale o MediaWiki
3. **Configura** percorso/URL della sorgente
4. **Clicca** "🔄 Indicizza" o "🔄 Sincronizza Wiki"
5. **Fai domande** sui tuoi documenti!

### Configurazione MediaWiki

Modifica `wiki_sources.yaml` per configurare le tue wiki:

```yaml
mode: "selectable"  # fixed | selectable | custom
default_wiki: "mia_wiki"

wikis:
  mia_wiki:
    name: "Wiki Interna"
    url: "https://wiki.example.com"
    api_path: "/w/api.php"
    namespaces: [0]
    max_pages: 100

global_settings:
  user_agent: "DatapizzaBot/1.4.0"
  request_delay: 0.5
```

### Privacy Mode 🔒

Quando la Knowledge Base è attiva:
- ☁️ **Cloud provider BLOCCATO** automaticamente
- 💻 Solo **Ollama locale** o **Remote host** permessi
- 🔒 I tuoi documenti **non escono mai** dal tuo computer

---

## 📤 Export Conversazioni

### Formati Disponibili

| Formato | Estensione | Uso consigliato |
|---------|------------|-----------------|
| Markdown | .md | Blog, Obsidian, Notion |
| JSON | .json | Elaborazione programmata |
| TXT | .txt | Backup semplice |
| PDF | .pdf | Documenti stampabili |

### Batch Export

Esporta **tutte** le conversazioni salvate in un file ZIP!

---

## 📋 Dipendenze

```txt
# Core
streamlit>=1.28.0
python-dotenv>=1.0.0
pyyaml>=6.0
datapizza-ai

# Client LLM
datapizza-ai-clients-openai-like  # Ollama
datapizza-ai-clients-openai       # OpenAI (opzionale)
datapizza-ai-clients-anthropic    # Anthropic (opzionale)
datapizza-ai-clients-google       # Google (opzionale)

# RAG
chromadb>=0.4.0
beautifulsoup4>=4.12.0
PyPDF2>=3.0.0

# MediaWiki (opzionale)
mwclient>=0.10.0

# Export
reportlab>=4.0.0
```

---

## 🔧 Modelli Ollama Consigliati

```bash
# Modelli generali
ollama pull llama3.2
ollama pull mistral
ollama pull qwen2.5

# Modelli per coding
ollama pull qwen2.5-coder

# Modelli multimodali
ollama pull llava
ollama pull granite3.2-vision

# Modello per embeddings (RAG)
ollama pull nomic-embed-text
```

---

## 🗺️ Roadmap

Vedi [ROADMAP.md](ROADMAP.md) per il piano di sviluppo completo.

### Prossime Release

| Versione | Feature | Stato |
|----------|---------|-------|
| v1.4.1 | Bug fix, miglioramenti UI | 📋 Planned |
| v1.5.0 | Streaming risposte | 📋 Planned |
| v1.6.0 | Confronto modelli | 📋 Planned |
| v2.0.0 | Multimodal, Docker, API | 📋 Planned |

---

## 🤝 Contributing

Contribuzioni benvenute! Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per le linee guida.

1. Fork del repository
2. Crea un branch (`git checkout -b feature/nuova-feature`)
3. Commit (`git commit -m 'feat: aggiungi nuova feature'`)
4. Push (`git push origin feature/nuova-feature`)
5. Apri una Pull Request

---

## 📜 License

MIT License - vedi [LICENSE](LICENSE) per dettagli.

---

## 👥 Credits

- **DeepAiUG** - Community italiana AI
- **Datapizza** - Framework LLM
- **Streamlit** - UI Framework

---

## 📞 Contatti

- 🌐 [DeepAiUG](https://deepaiug.it)
- 💬 Issues su GitHub
- 📧 info@deepaiug.it

---

*Made with ❤️ by DeepAiUG Community*
