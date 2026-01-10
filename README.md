# 🍕 Datapizza Streamlit LLM Interface

> Interfaccia Streamlit modulare per interagire con LLM locali (Ollama), remoti e cloud.
> Progetto Open Source della community **DeepAiUG**.

[![Version](https://img.shields.io/badge/version-1.4.1-blue.svg)](https://github.com/EnzoGitHub27/datapizza-streamlit-interface)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- 🤖 **Multi-provider**: Ollama (locale), Remote host, Cloud (OpenAI, Anthropic, Google)
- 💬 **Conversazioni multi-turno** con memoria del contesto
- 💾 **Persistenza** delle conversazioni su file JSON
- 📥 **Export** in Markdown, JSON, TXT, PDF + Batch ZIP
- 📚 **Knowledge Base RAG** - Interroga documenti locali e wiki!
- 🌐 **Multi-Wiki** - MediaWiki + DokuWiki support ⭐ NEW
- 🔒 **Privacy-first** - Blocco automatico cloud quando usi documenti sensibili
- 🎨 **UI moderna** con temi chiaro/scuro
- ♻️ **Architettura modulare** - Codice organizzato in packages

---

## 🏗️ Architettura v1.4.1

```
datapizza-streamlit-interface/
├── app.py                    # ⭐ Entry point principale
├── wiki_sources.yaml         # Configurazione sorgenti wiki
│
├── config/                   # 📁 Configurazione
│   ├── constants.py          # Costanti, WIKI_TYPES
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
│       ├── local_folder.py   # File locali
│       ├── mediawiki.py      # API MediaWiki
│       └── dokuwiki.py       # DokuWiki ⭐ NEW
│
├── export/                   # 📁 Sistema export
│   └── exporters.py          # MD, JSON, TXT, PDF, ZIP
│
├── ui/                       # 📁 Interfaccia utente
│   ├── styles.py             # CSS
│   ├── chat.py               # Rendering chat
│   └── sidebar/              # Componenti sidebar
│
└── old/                      # 📁 Versioni archiviate
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
pip install streamlit python-dotenv reportlab pyyaml

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
```

#### 4. Dipendenze per Wiki RAG (v1.3.0+)
```bash
pip install chromadb beautifulsoup4 PyPDF2
```

#### 5. Dipendenze per Wiki Adapters (v1.3.2+)
```bash
pip install mwclient      # MediaWiki
pip install dokuwiki      # DokuWiki (v1.4.1+)
```

---

### Metodo 3: Usando requirements.txt

⚠️ **Nota**: Alcuni utenti hanno riscontrato problemi con questo metodo. Se fallisce, usa il **Metodo 2**.

```bash
pip install -r requirements.txt
```

Se riscontri errori, segui le istruzioni nel Metodo 2.

---

### Metodo 4: Usando Poetry 
Installa poetry [qui](https://python-poetry.org/docs/#installing-with-the-official-installer)

Crea un virtual environment con python 3.12 o 3.13 

```bash
poetry env use python3.12
```

Installa le dipendenze dal file pyproject.toml

```bash
poetry install
```

attiva l'ambiente virtuale

```bash
poetry shell
```




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
streamlit run app.py
```

---

## 📚 Knowledge Base RAG

### Sorgenti Supportate

| Tipo | Descrizione | Pacchetto |
|------|-------------|-----------|
| 📁 **Cartella Locale** | File MD, TXT, HTML, PDF | - |
| 🌐 **MediaWiki** | Wikipedia-like wikis | `mwclient` |
| 📘 **DokuWiki** | Wiki per documentazione | `dokuwiki` |

### Configurazione `wiki_sources.yaml`

```yaml
mode: "selectable"  # fixed | selectable | custom
default_source: "mia_wiki"

sources:
  mia_wiki:
    type: "mediawiki"
    name: "Wiki Interna"
    icon: "🌐"
    url: "https://wiki.example.com"
    api_path: "/w/api.php"
    
  docs_tecniche:
    type: "dokuwiki"
    name: "Documentazione"
    icon: "📘"
    url: "https://docs.example.com"
    
  file_locali:
    type: "local"
    name: "Documenti Locali"
    icon: "📁"
    folder_path: "/home/user/docs"
    extensions: [".md", ".txt", ".pdf"]
```

### Privacy Mode 🔒

Quando la Knowledge Base è attiva:
- ☁️ **Cloud provider BLOCCATO** automaticamente
- 💻 Solo **Ollama locale** o **Remote host** permessi
- 🔒 I tuoi documenti **non escono mai** dal tuo computer

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

## 📋 Dipendenze

```txt
# Core
streamlit>=1.28.0
datapizza-ai
datapizza-ai-clients-openai-like
python-dotenv>=1.0.0
pyyaml>=6.0

# RAG
chromadb>=0.4.0
beautifulsoup4>=4.12.0
PyPDF2>=3.0.0

# Wiki Adapters
mwclient>=0.10.0      # MediaWiki
dokuwiki>=0.1.0       # DokuWiki

# Export
reportlab>=4.0.0
```

---

## 🗺️ Roadmap

Vedi [ROADMAP.md](ROADMAP.md) per il piano completo.

| Versione | Feature | Stato |
|----------|---------|-------|
| v1.4.1 | Multi-Wiki (DokuWiki) | ✅ |
| v1.5.0 | Streaming risposte | 📋 |
| v1.6.0 | Confronto modelli | 📋 |
| v2.0.0 | Multimodal, Docker, API | 🎯 |

---

## 🤝 Contributing

Contribuzioni benvenute! Vedi [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork del repository
2. Crea un branch (`git checkout -b feature/nuova-feature`)
3. Commit (`git commit -m 'feat: aggiungi nuova feature'`)
4. Push (`git push origin feature/nuova-feature`)
5. Apri una Pull Request

---

## 📜 License

MIT License - vedi [LICENSE](LICENSE)

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
