# 🧠 DeepAiUG Streamlit LLM Interface

> Interfaccia Streamlit modulare per interagire con LLM locali (Ollama), remoti e cloud.
> Progetto Open Source della community **DeepAiUG**.

> *"Non semplifica il pensare, ma lo allena."*
> — Carmelo Quartarone, Innovation Senior Developer @ Cloudia Research

[![Version](https://img.shields.io/badge/version-1.14.2-blue.svg)](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/releases/tag/v1.14.2)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

---

## 🚀 Installazione rapida — Nessuna competenza tecnica richiesta

| Sistema | Script | Cosa fa |
|---|---|---|
| 🪟 Windows 11 | `INSTALLA_DeepAiUG.bat` | Installa tutto automaticamente |
| 🍎 Mac | `installa_deepaiug_mac.sh` | Installa tutto automaticamente |
| 🐧 Linux | `installa_deepaiug_linux.sh` | Installa tutto automaticamente |

📥 **[Scarica installer](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/releases/latest)**
🌐 **[Demo online e guida](https://deepaiug.vercel.app)**

Istruzioni dettagliate in `installer/INIZIA-QUI.txt`

---

## ✨ Features

- 🤖 **Multi-provider**: Ollama (locale), Remote host, Cloud (OpenAI, Anthropic, Google)
- 🧠 **Approccio Socratico** - Bottoni per esplorare prospettive alternative! ⭐ NEW
- 🌊 **Streaming Responses** - Risposte token-by-token in tempo reale!
- 💬 **Conversazioni multi-turno** con memoria del contesto
- 💾 **Persistenza** delle conversazioni su file JSON
- 📥 **Export** in Markdown, JSON, TXT, PDF + Batch ZIP
- 📚 **Knowledge Base RAG** - Interroga documenti locali e wiki!
- 🟣 **Vault Support** - Obsidian, LogSeq, Notion Export con riconoscimento automatico
- 📚 **Chat KB** - Chat salvate come Knowledge Base epistemica con rilevanza e tipo
- 🌐 **Multi-Wiki** - MediaWiki + DokuWiki support
- 📎 **File Upload in Chat** - Allega PDF, DOCX, TXT, immagini
- 🔐 **Privacy-First Protection** - Sistema completo protezione dati sensibili
- 🎨 **UI moderna** con temi chiaro/scuro
- ♻️ **Architettura modulare** - Codice organizzato in packages

---

### 🧠 Novità v1.14.2 — Vault Used Flag + Icona nel Selettore

- **Flag `vault_used`**: le conversazioni condotte con un vault attivo vengono marcate nel JSON
- **Icona 🧠** nel selettore conversazioni: identifica a colpo d'occhio le chat che hanno usato conoscenza da vault
- **Retrocompatibilità completa**: chat pre-v1.14.2 caricate senza crash (default `false`)

### 📚 Novità v1.14.0 — Chat Salvate come Knowledge Base Epistemica

- **Chat KB**: le conversazioni flaggate diventano sorgente RAG consultabile nelle sessioni future
- **Metadati epistemici**: rilevanza (⭐/⭐⭐/⭐⭐⭐), tipo (decisione / insight / memoria_aziendale / riferimento), note libere
- **Boost retrieval** proporzionale alla rilevanza (×1.0 / ×1.15 / ×1.30)
- **Pannello gestione KB** in sidebar: modifica metadati inline, rimozione, statistiche chunk
- **Icone indicatore** nel selettore chat: 📚 / 📚⭐ / 📚⭐⭐
- **Toggle "Usa KB Chat"** con filtro per tipo nel retrieval
- **Collection ChromaDB separata** `deepaiug_chat_kb` — indipendente da wiki e vault
- **23 test** su retrocompatibilità, chunking, indicizzazione, boost e filtro tipo
- **Privacy-first by design**: nessuna chat entra nella KB senza scelta esplicita dell'utente

### 🟣 Novità v1.13.x — Vault Support (F3) + UX Fix

- **Vault Obsidian, LogSeq, Notion Export** selezionabili direttamente dal menu Knowledge Base
- **Riconoscimento automatico** del tipo vault dal percorso inserito
- **Parser nativo .canvas** Obsidian (estrae testo dai nodi del canvas)
- **Aggiornamento incrementale** basato su timestamp file
- **ChromaDB batch fix** — supporto corpus grandi (testato su 808 file / 6693 chunk)
- **Progress bar** in tempo reale durante l'indicizzazione
- **Conferma a 2 step** prima del caricamento conversazioni con vault pesante (≥50 file)
- **Icone vault specifiche** nelle conversazioni salvate: 🧠🟣 Obsidian, 🧠🟤 LogSeq, 🧠⬛ Notion
- **Fix modello nei bottoni socratici** — ogni esplorazione mostra il modello che l'ha generata

### 🏗️ Novità v1.12.0 — Architettura Sidebar

- **Sidebar riorganizzata** in 5 sezioni con ordine fisso
- **⚙️ Configurazione** chiusa di default (`st.expander`) — connessione, modello, parametri, KB
- **💬 Conversazione**, **🗺️ Mappa**, **🧠 Socratica**, **📤 Export** — sempre visibili
- **Banner dinamico**: la versione nel banner segue automaticamente `VERSION`

### 🚀 Novità v1.11.2 — Installer multipiattaforma

- Installazione automatica su **Windows 11**, **Mac** e **Linux**
- Suggerimento modello AI in base alla RAM rilevata
- Progress bar durante i download, log installazione automatico
- Launcher e icona Desktop creati automaticamente
- Nessuna competenza tecnica richiesta

Vedi `installer/INIZIA-QUI.txt` per le istruzioni.

### 🎨 Novità v1.11.1 — Matrix Theme

- **Matrix Theme**: tema visivo completo (sfondo scuro, palette teal/green, glitch H1, scanlines CRT)
- **Matrix rain**: animazione canvas con katakana + hex + simboli matematici
- **Tipografia**: Cinzel (titoli), Exo 2 (contenuti), Share Tech Mono (input/bottoni)
- **Componenti stilizzati**: chat bubbles, bottoni, input, selectbox, metric, scrollbar

### 🎨 Novità v1.11.0 — Branding + UX Polish

- **branding.yaml**: personalizza titolo, icona e banner senza modificare codice
- **Nome modello + timestamp** in output socratici e mappa sessione
- **Mappa collassabile** + bottoni "Rigenera" e "Genera mappa" su conversazioni caricate
- **Fix parser frecce vuote**: nessuna freccia vuota con nessun modello

### 📊 Novità v1.10.0 — Mappa Sessione: attrito sul pensiero (Ligas/Quartarone/Floridi)

### 🧠 Novità v1.9.2 — Prompt Epistemologici Potenziati (Floridi/Eco/Quartarone)

## 🆕 Novità v1.9.1 - UI Polish + Cloud Config + Privacy Granulare 🎨

- **🎨 Chat Bubbles** - Rendering unificato con `markdown-it-py`, colori dark/light professionali
- **☁️ Cloud Models YAML** - File `cloud_models.yaml` per configurare provider e modelli senza toccare il codice
- **🔒 Privacy Granulare** - Icone specifiche (📚 Wiki, 📁 Cartella, 📎 Allegati) + warning cambio provider
- **⚙️ Parametri Collassabili** - System Prompt, Temperature, Max messaggi in expander

### Novità v1.9.0 - Socratic History + Persistence 📋

Tracciamento, visualizzazione e persistenza delle esplorazioni socratiche nelle conversazioni salvate.

### Novità v1.8.0 - UI Socratica Completa 🧠

5 bottoni socratici organizzati in 2 sezioni + toggle modalità (Veloce/Standard/Socratico)

---

## Novità v1.7.x - Remote Servers + Security 🖥️🔐

### Remote Servers YAML
- 3 modalità: fixed, selectable, custom_allowed
- Lista modelli dinamica
- File `remote_servers.yaml` opzionale

### Security Settings
- API Keys nascoste per default
- File `security_settings.yaml`

---

## I 5 Bottoni Socratici 🧠

### La Filosofia
> **L'AI produce significato plausibile, ma il SENSO lo costruisce l'umano.**

Ispirato al "capitale semantico" (Floridi/Quartarone).

**Sezione 1 - Analizza la risposta:**

| Bottone | Funzione |
|---------|----------|
| 🔄 Alternative | 3 interpretazioni diverse |
| 🤔 Assunzioni | Cosa si dà per scontato |
| ⚠️ Limiti | Quando non funziona |
| 🎭 Confuta | Avvocato del diavolo |

**Sezione 2 - Sfida la domanda:**

| Bottone | Funzione |
|---------|----------|
| 🪞 Rifletti | Meta-riflessione sulla domanda stessa |

**⚠️ Limiti** ⭐ NEW
- Identifica quando la risposta NON funziona
- Casi limite ed eccezioni
- Previene applicazioni errate

**Le 4 capacità che DeepAiUG vuole allenare:**
1. **Costruzione di senso** - collegare informazioni
2. **Valutazione semantica** - capire cosa conta
3. **Contestualizzazione** - collocare nel contesto giusto
4. **Resistenza alla plausibilità** - non fidarsi del "suona giusto"

### 🔮 Prossime Feature Socratiche
- **v2.0.0**: Semantic Layer + Knowledge Graph

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

## 🏗️ Architettura v1.14.0

```
datapizza-streamlit-interface/
├── app.py                    # ⭐ Entry point principale
├── .streamlit/config.toml    # Tema Streamlit nativo (Matrix)
├── wiki_sources.yaml         # Configurazione sorgenti wiki
├── remote_servers.yaml       # Config server remoti
├── cloud_models.yaml         # Config modelli cloud
├── security_settings.yaml    # Impostazioni sicurezza
├── branding.yaml             # Personalizzazione titolo/icona/banner
│
├── config/                   # 📁 Configurazione
│   ├── constants.py          # Costanti, WIKI_TYPES, VISION_MODELS
│   ├── settings.py           # Loader settings, API keys
│   └── branding.py           # load_branding() + 6 costanti
│
├── core/                     # 📁 Logica core
│   ├── llm_client.py         # Factory client LLM
│   ├── conversation.py       # Gestione messaggi
│   ├── persistence.py        # Salvataggio/caricamento (+ kb_metadata v1.14.0)
│   ├── kb_chat_indexer.py    # ⭐ NEW v1.14.0: indicizzazione chat-KB ChromaDB
│   └── file_processors.py    # Estrazione testo da file
│
├── rag/                      # 📁 Sistema RAG
│   ├── models.py             # Document, Chunk
│   ├── chunker.py            # TextChunker intelligente
│   ├── vector_store.py       # ChromaDB + fallback
│   ├── manager.py            # KnowledgeBaseManager
│   ├── vault.py              # F3: detect, scan, parse canvas, update incrementale
│   └── adapters/             # Sorgenti dati
│       ├── local_folder.py   # File locali
│       ├── mediawiki.py      # API MediaWiki
│       └── dokuwiki.py       # DokuWiki
│
├── knowledge_base/           # 📁 Dati KB (generato a runtime)
│   ├── vectorstore/          # ChromaDB wiki/vault
│   ├── chat_kb_vectorstore/  # ⭐ NEW v1.14.0: ChromaDB chat-KB
│   └── chat_kb_meta.json     # ⭐ NEW v1.14.0: timestamp ultima indicizzazione
│
├── export/                   # 📁 Sistema export
│   └── exporters.py          # MD, JSON, TXT, PDF, ZIP
│
├── tests/                    # 📁 Test suite
│   └── test_kb_chat_indexer.py  # ⭐ NEW v1.14.0: 23 test indicizzazione KB
│
├── docs/                     # 📁 Documentazione
│   └── manuale_utente_kb_chat.md  # ⭐ NEW v1.14.0: guida utente KB Chat
│
└── ui/                       # 📁 Interfaccia utente
    ├── styles.py             # CSS
    ├── style.py              # Matrix Theme (CSS + rain animation)
    ├── chat.py               # Rendering chat
    ├── file_upload.py        # Widget upload file
    ├── privacy_warning.py    # Dialog privacy
    ├── socratic/             # 🧠 Modulo socratico
    │   ├── prompts.py        # Template prompt
    │   ├── buttons.py        # Bottoni UI + registrazione esplorazioni
    │   ├── history.py        # SocraticExploration + SocraticHistory
    │   ├── history_widget.py # Widget sidebar storico
    │   └── session_map.py    # SessionMap + SessionMapAnalyzer (F2)
    └── sidebar/
        ├── llm_config.py
        ├── knowledge_base.py
        ├── conversations.py
        ├── export_ui.py
        ├── session_map_widget.py  # Widget mappa sessione (F2)
        └── kb_panel.py            # ⭐ NEW v1.14.0: pannello gestione KB Chat
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

## 🔍 Come scegliere il modello giusto per il tuo hardware

Uno degli ostacoli più comuni nell'adottare un'AI locale è capire **quale modello scaricare** senza sprecare tempo e spazio su modelli incompatibili con il proprio hardware.

Ti consigliamo di usare **[llmfit](https://github.com/AlexsJones/llmfit)** — uno strumento open source che analizza CPU, RAM e VRAM della tua macchina e ti mostra quali modelli LLM sono compatibili, con score, token/s stimati e quantizzazione ottimale.

### Installazione rapida (Linux/macOS)

```bash
curl -fsSL https://llmfit.axjns.dev/install.sh | sh
```

> ⚠️ È un singolo binario Rust — nessun ambiente virtuale, nessun conflitto con i tuoi venv Python esistenti.

### Utilizzo base

```bash
# Interfaccia TUI interattiva
llmfit

# Output tabellare (consigliato su VM o server)
llmfit --cli

# Solo i modelli perfettamente compatibili
llmfit fit --perfect -n 10

# Se hai una GPU ma llmfit non la rileva (VM, Jetson, ecc.)
llmfit --memory=8G --cli
```

### Guida rapida alla scelta del modello per DeepAiUG

| VRAM disponibile | Modelli consigliati per iniziare | Note |
|---|---|---|
| **< 4 GB** | `llama3.2:3b`, `qwen3:0.6b`, `qwen3.5:0.8b` | Inferenza CPU o ibrida |
| **4 GB** | `llama3.2:3b`, `qwen3.5:2b`, `ministral-3b` | GPU pura, ottima velocità |
| **8 GB** | `llama3.1:8b`, `qwen3.5:4b`, `gemma3:4b` | Sweet spot qualità/velocità |
| **16 GB+** | `qwen2.5-coder:7b`, `llama3.1:latest`, `deepseek-v2-lite` | Modelli capaci per uso professionale |
| **24 GB+** | `qwen3.5:4b`+ modelli 14-30B | Qualità paragonabile ai cloud |

> 💡 I pulsanti Socratici di DeepAiUG sono stati calibrati e testati su `llama3.2:3b` — è il punto di partenza consigliato per chi ha hardware limitato.

---

## 🔧 Installazione avanzata (sviluppatori)

### Metodo 1: Script Automatico (da repo clonata)

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
| 🟣 **Vault Obsidian** | Note .md + Canvas, riconoscimento automatico | - |
| 🟤 **Vault LogSeq** | Note .md e .org, esclusi file di backup | - |
| ⬛ **Notion Export** | Cartelle export Notion in formato MD | - |
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
| v1.14.0 | 📚 Chat salvate come Knowledge Base epistemica | ✅ |
| v1.13.9 | 🔧 Fix modello per esplorazione socratica specifica | ✅ |
| v1.13.8 | 🔧 Fix nome modello nei bottoni socratici | ✅ |
| v1.13.7 | 🧠 Conferma caricamento vault + icone vault in conversazioni | ✅ |
| v1.13.6 | 🔧 Fix progress callback + stima tempo caricamento | ✅ |
| v1.13.5 | 🟣 Warning + progress bar caricamento conversazioni vault | ✅ |
| v1.13.4 | 🔧 ChromaDB batch fix + progress bar indicizzazione | ✅ |
| v1.13.3 | 🟣 Banner vault rilevato coerente | ✅ |
| v1.13.2 | 🟣 Vault nel dropdown YAML | ✅ |
| v1.13.1 | 🟣 Vault nel dropdown custom | ✅ |
| v1.13.0 | 🟣 F3 Vault Support — Obsidian, LogSeq, Notion | ✅ |
| v1.12.0 | 🏗️ Architettura Sidebar — configurazione separata | ✅ |
| v1.11.2 | 🚀 Installer multipiattaforma Windows/Mac/Linux | ✅ |
| v1.11.1 | 🎨 Matrix Theme | ✅ |
| v1.11.0 | 🎨 Branding + UX Polish + Bug Fix parser | ✅ |
| v1.10.0 | 📊 Mappa Sessione — Attrito sul pensiero | ✅ |
| v1.9.1 | 🎨 UI Polish + ☁️ Cloud Config + 🔒 Privacy Granulare | ✅ |
| v1.9.0 | 📋 Socratic History + Persistence | ✅ |
| v1.8.0 | 🧠 UI Socratica Completa (5 bottoni + Toggle) | ✅ |
| v1.7.1 | 🖥️ Remote YAML + 🔐 Security | ✅ |
| v2.0.0 | Semantic Layer + Knowledge Graph | 🎯 |

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

*Made with ❤️ by Gilles - DeepAiUG*
