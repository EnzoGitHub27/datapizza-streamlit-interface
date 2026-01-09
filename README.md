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
ollama list
```

### Installazione

```bash
# Clone
git clone https://github.com/EnzoGitHub27/datapizza-streamlit-interface.git
cd datapizza-streamlit-interface

# Ambiente virtuale (consigliato)
python3 -m venv deepaiug-interface
source deepaiug-interface/bin/activate  # Linux/Mac

# Dipendenze (ordine importante!)
pip install datapizza-ai
pip install datapizza-ai-clients-openai-like
pip install streamlit pyyaml python-dotenv
pip install chromadb beautifulsoup4 PyPDF2
pip install mwclient reportlab

# DokuWiki support (opzionale)
pip install dokuwiki
```

### Avvio

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

## 🔧 Configurazione API Keys

```bash
# File secrets (consigliato)
mkdir -p secrets
echo "sk-your-key" > secrets/openai_key.txt

# Oppure variabili ambiente
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"
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

1. Fork → Branch → PR
2. Segui le convenzioni
3. Testa le modifiche

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
