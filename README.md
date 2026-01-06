# 🍕 Datapizza Streamlit LLM Interface

> Interfaccia Streamlit per interagire con LLM locali (Ollama), remoti e cloud.
> Progetto Open Source della community **DeepAiUG**.

[![Version](https://img.shields.io/badge/version-1.3.1-blue.svg)](https://github.com/EnzoGitHub27/datapizza-streamlit-interface)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- 🤖 **Multi-provider**: Ollama (locale), Remote host, Cloud (OpenAI, Anthropic, Google)
- 💬 **Conversazioni multi-turno** con memoria del contesto
- 💾 **Persistenza** delle conversazioni su file JSON
- 📥 **Export** in Markdown, JSON, TXT, PDF
- 📚 **Knowledge Base RAG** - Interroga i tuoi documenti locali! ⭐ NEW
- 🔒 **Privacy-first** - Blocco automatico cloud quando usi documenti sensibili
- 🎨 **UI moderna** con temi chiaro/scuro

---

## 📂 Versioni Disponibili

| File | Versione | Stato | Descrizione |
|------|----------|-------|-------------|
| `03_interfaccia_con_wiki_rag.py` | **v1.3.1** | ⭐ **Latest** | Multi-turno + Persistenza + Export + **Wiki RAG** |
| `02_interfaccia_con_export.py` | v1.2.0 | ✅ Stable | Multi-turno + Persistenza + Export |
| `01_interfaccia_con_memoria.py` | v1.1.1 | ✅ Stable | Multi-turno + Persistenza |
| `00_interfaccia_dinamica_datapizza_Streamlit.py` | v1.0.0 | ✅ Stable | Interfaccia base |

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
pip install streamlit python-dotenv reportlab

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
# CONSIGLIATA: Ultima versione con tutte le funzionalità
streamlit run 03_interfaccia_con_wiki_rag.py

# Versione con export (senza RAG)
streamlit run 02_interfaccia_con_export.py

# Versione con memoria (senza export)
streamlit run 01_interfaccia_con_memoria.py

# Versione base
streamlit run 00_interfaccia_dinamica_datapizza_Streamlit.py
```

---

## 📚 Wiki RAG - Knowledge Base (v1.3.1)

La funzionalità **Wiki RAG** ti permette di interrogare i tuoi documenti locali usando LLM!

### Come Funziona

```
┌─────────────────────────────────────────────────────────────┐
│                    TUOI DOCUMENTI                           │
│  (Markdown, TXT, HTML, PDF in una cartella locale)          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              INDICIZZAZIONE (ChromaDB)                      │
│  - Chunking intelligente (rispetta titoli/paragrafi)        │
│  - Embeddings vettoriali                                    │
│  - Storage locale persistente                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      CHAT RAG                               │
│  1. Ricerca documenti rilevanti                             │
│  2. Contesto iniettato nel prompt                           │
│  3. LLM risponde basandosi sui documenti                    │
│  4. Fonti citate nella risposta                             │
└─────────────────────────────────────────────────────────────┘
```

### Setup Knowledge Base

1. **Attiva** "🔍 Usa Knowledge Base" nella sidebar
2. **Inserisci** il percorso della cartella con i documenti
3. **Seleziona** i formati file da includere (.md, .txt, .html, .pdf)
4. **Configura** i parametri di chunking (opzionale)
5. **Clicca** "🔄 Indicizza Documenti"
6. **Fai domande** sui tuoi documenti!

### Parametri Chunking

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| Chunk Size | 1000 | Dimensione massima di ogni chunk (caratteri) |
| Overlap | 200 | Sovrapposizione tra chunk consecutivi |
| Top K | 5 | Numero di documenti da includere nel contesto |

**Suggerimenti**:
- **Chunk piccoli** (500-800): più precisione, meno contesto
- **Chunk grandi** (1500-2000): più contesto, meno precisione
- **Overlap alto** (30-50%): evita di perdere informazioni ai bordi

### Privacy Mode

Quando la Knowledge Base è attiva:
- ☁️ **Cloud provider BLOCCATO** automaticamente
- 💻 Solo **Ollama locale** o **Remote host** permessi
- 🔒 I tuoi documenti **non escono mai** dal tuo computer

---

## 📋 Dipendenze

```txt
# Core
streamlit>=1.28.0
python-dotenv>=1.0.0
datapizza-ai

# Export (v1.2.0+)
reportlab>=4.0.0

# Wiki RAG (v1.3.0+)
chromadb>=0.4.0
beautifulsoup4>=4.12.0
PyPDF2>=3.0.0
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

## 📁 Struttura Progetto

```
datapizza-streamlit-interface/
├── 00_interfaccia_dinamica_datapizza_Streamlit.py  # v1.0.0
├── 01_interfaccia_con_memoria.py                    # v1.1.1
├── 02_interfaccia_con_export.py                     # v1.2.0
├── 03_interfaccia_con_wiki_rag.py                   # v1.3.1 ⭐
├── requirements.txt
├── install.sh                  # Script installazione Linux/Mac
├── install.bat                 # Script installazione Windows
├── README.md
├── CHANGELOG.md
├── ROADMAP.md
├── LICENSE
├── conversations/              # Conversazioni salvate (auto-generato)
├── knowledge_base/             # Vector store ChromaDB (auto-generato)
└── secrets/                    # API keys (opzionale)
```

---

## 🗺️ Roadmap

Vedi [ROADMAP.md](ROADMAP.md) per il piano di sviluppo completo.

### Prossime Release

| Versione | Feature | Stato |
|----------|---------|-------|
| v1.3.2+ | Adapter MediaWiki, DokuWiki | 📋 Planned |
| v1.4.0 | Streaming risposte | 📋 Planned |
| v1.5.0 | Confronto modelli | 📋 Planned |
| v2.0.0 | Multimodal, Docker, API | 📋 Planned |

---

## 🤝 Contributing

Contribuzioni benvenute! 

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