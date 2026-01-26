# 🍕 Datapizza Streamlit LLM Interface

> Interfaccia Streamlit modulare per interagire con LLM locali (Ollama), remoti e cloud.
> Progetto Open Source della community **DeepAiUG**.

[![Version](https://img.shields.io/badge/version-1.6.1-blue.svg)](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/releases/tag/v1.6.1)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- 🤖 **Multi-provider**: Ollama (locale), Remote host, Cloud (OpenAI, Anthropic, Google)
- 🧠 **Approccio Socratico** - Bottoni per esplorare prospettive alternative! ⭐ NEW
- 🌊 **Streaming Responses** - Risposte token-by-token in tempo reale!
- 💬 **Conversazioni multi-turno** con memoria del contesto
- 💾 **Persistenza** delle conversazioni su file JSON
- 📥 **Export** in Markdown, JSON, TXT, PDF + Batch ZIP
- 📚 **Knowledge Base RAG** - Interroga documenti locali e wiki!
- 🌐 **Multi-Wiki** - MediaWiki + DokuWiki support
- 📎 **File Upload in Chat** - Allega PDF, DOCX, TXT, immagini
- 🔐 **Privacy-First Protection** - Sistema completo protezione dati sensibili
- 🎨 **UI moderna** con temi chiaro/scuro
- ♻️ **Architettura modulare** - Codice organizzato in packages

---

## 🆕 Novità v1.6.1 - Approccio Socratico 🧠

### La Filosofia
DeepAiUG evolve da semplice chat a **strumento socratico**. Ispirato al concetto di "capitale semantico" (Floridi/Quartarone):

> **L'AI produce significato plausibile, ma il SENSO lo costruisce l'umano.**

### 🔄 Bottone "Genera alternative"
Sotto ogni risposta AI appare un nuovo bottone che genera **3 interpretazioni alternative** dello stesso problema.

**Perché è utile?**
- Stimola il pensiero critico
- Mostra che ogni risposta ha assunzioni implicite
- Aiuta a costruire comprensione, non solo ottenere risposte

**Le 4 capacità che DeepAiUG vuole allenare:**
1. **Costruzione di senso** - collegare informazioni
2. **Valutazione semantica** - capire cosa conta
3. **Contestualizzazione** - collocare nel contesto giusto
4. **Resistenza alla plausibilità** - non fidarsi del "suona giusto"

### 🔮 Prossime Feature Socratiche
- **v1.7.0**: Bottoni "🤔 Assunzioni" + "⚠️ Limiti"
- **v1.8.0**: Toggle modalità (Veloce/Standard/Socratico)

---

## Novità v1.6.0

### 🌊 Streaming Responses
Le risposte dell'AI ora appaiono **token-by-token in tempo reale**, come in ChatGPT!

**Provider supportati:**
- ✅ **Ollama locale**: Streaming perfetto
- ✅ **Remote host**: Streaming perfetto
- ⚠️ **Cloud (OpenAI, etc)**: In arrivo

**Footer aggiornato:** 🤖 DeepAiUG by Gilles

---

## Novità v1.5.x

### 📎 File Upload in Chat
Allega file direttamente nella chat, come in ChatGPT/Claude.ai!

| Tipo | Formati | Note |
|------|---------|------|
| 📄 **Documenti** | PDF, TXT, MD, DOCX | Testo estratto e aggiunto al contesto |
| 🖼️ **Immagini** | PNG, JPG, GIF, WEBP | Richiede modello Vision (LLaVA, Granite3.2-Vision) |

### 🔐 Privacy-First Protection
Sistema completo per proteggere i tuoi documenti sensibili:

| Protezione | Descrizione |
|------------|-------------|
| 🔒 **Upload bloccato su Cloud** | I file possono essere caricati solo con Ollama locale o Remote host |
| ⚠️ **Privacy Dialog** | Warning automatico quando passi da Local→Cloud con documenti in memoria |
| 📢 **Banner promemoria** | Ricorda che la sessione contiene dati estratti da documenti |

---

## 🏗️ Architettura v1.6.1

```
datapizza-streamlit-interface/
├── app.py                    # ⭐ Entry point principale
├── wiki_sources.yaml         # Configurazione sorgenti wiki
│
├── config/                   # 📁 Configurazione
│   ├── constants.py          # Costanti, WIKI_TYPES, VISION_MODELS
│   └── settings.py           # Loader settings, API keys
│
├── core/                     # 📁 Logica core
│   ├── llm_client.py         # Factory client LLM
│   ├── conversation.py       # Gestione messaggi
│   ├── persistence.py        # Salvataggio/caricamento
│   └── file_processors.py    # Estrazione testo da file
│
├── rag/                      # 📁 Sistema RAG
│   ├── models.py             # Document, Chunk
│   ├── chunker.py            # TextChunker intelligente
│   ├── vector_store.py       # ChromaDB + fallback
│   ├── manager.py            # KnowledgeBaseManager
│   └── adapters/             # Sorgenti dati
│       ├── local_folder.py   # File locali
│       ├── mediawiki.py      # API MediaWiki
│       └── dokuwiki.py       # DokuWiki
│
├── export/                   # 📁 Sistema export
│   └── exporters.py          # MD, JSON, TXT, PDF, ZIP
│
└── ui/                       # 📁 Interfaccia utente
    ├── styles.py             # CSS
    ├── chat.py               # Rendering chat
    ├── file_upload.py        # Widget upload file
    ├── privacy_warning.py    # Dialog privacy
    ├── socratic/             # 🧠 NEW - Modulo socratico
    │   ├── prompts.py        # Template prompt
    │   └── buttons.py        # Bottoni UI
    └── sidebar/              # Componenti sidebar
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

#### Linux/Mac
```bash
git clone https://github.com/EnzoGitHub27/datapizza-streamlit-interface.git
cd datapizza-streamlit-interface
chmod +x install.sh
./install.sh
```

#### Windows
```bash
git clone https://github.com/EnzoGitHub27/datapizza-streamlit-interface.git
cd datapizza-streamlit-interface
install.bat
```

---

### Metodo 2: Installazione Manuale Passo-Passo

#### 1. Clona il repository
```bash
git clone https://github.com/EnzoGitHub27/datapizza-streamlit-interface.git
cd datapizza-streamlit-interface
```

#### 2. Crea un ambiente virtuale
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows
```

#### 3. Installa le dipendenze nell'ordine corretto

```bash
# 3.1 - Dipendenze base
pip install streamlit python-dotenv reportlab pyyaml

# 3.2 - Datapizza AI core (PRIMA dei client!)
pip install datapizza-ai

# 3.3 - Client provider (DOPO datapizza-ai)
pip install datapizza-ai-clients-openai-like  # Per Ollama
pip install datapizza-ai-clients-openai       # Per OpenAI
pip install datapizza-ai-clients-anthropic    # Per Anthropic
pip install datapizza-ai-clients-google       # Per Google
```

#### 4. Dipendenze aggiuntive
```bash
pip install chromadb beautifulsoup4 PyPDF2    # RAG
pip install mwclient dokuwiki                  # Wiki
pip install python-docx Pillow                 # File Upload
```

---

### Metodo 3: Poetry

```bash
poetry env use python3.12
poetry install
poetry shell
```

---

## ▶️ Avvio

```bash
streamlit run app.py
```

---

## 🔧 Configurazione API Keys

### Opzione A: File .env
```env
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_API_KEY=your-google-gemini-key-here
```

### Opzione B: File secrets
```bash
mkdir -p secrets
echo "sk-your-key" > secrets/openai_key.txt
```

### Opzione C: Interfaccia Web
Puoi inserire le API keys direttamente dall'interfaccia Streamlit!

---

## 📚 Knowledge Base RAG

### Sorgenti Supportate

| Tipo | Descrizione | Pacchetto |
|------|-------------|-----------|
| 📁 **Cartella Locale** | File MD, TXT, HTML, PDF | - |
| 🌐 **MediaWiki** | Wikipedia-like wikis | `mwclient` |
| 📘 **DokuWiki** | Wiki per documentazione | `dokuwiki` |

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

# Modelli multimodali (per immagini)
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
mwclient>=0.10.0
dokuwiki>=0.1.0

# File Upload
python-docx>=0.8.0
Pillow>=10.0.0

# Export
reportlab>=4.0.0
```

---

## 🗺️ Roadmap

Vedi [ROADMAP.md](ROADMAP.md) per il piano completo.

| Versione | Feature | Stato |
|----------|---------|-------|
| v1.6.1 | 🧠 Bottoni Socratici | ✅ |
| v1.7.0 | 🧠 Assunzioni + Limiti | 📋 |
| v1.8.0 | 🧠 Toggle modalità | 📋 |
| v2.0.0 | Semantic Layer | 🎯 |

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
