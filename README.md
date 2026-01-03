# 🍕 Datapizza Streamlit LLM Interface

Interfaccia web completa per interagire con Large Language Models (LLM) locali, remoti e cloud tramite il framework [Datapizza AI](https://github.com/datapizza).
[DeepAiUG](https://deepaiug.vercel.app/) - Progetto DeepAiUG

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Caratteristiche

- 🖥️ **Modelli Locali**: Supporto completo per Ollama con rilevamento automatico
- 🌐 **Host Remoti**: Connessione a server LLM sulla tua rete
- ☁️ **Provider Cloud**: OpenAI, Anthropic (Claude), Google Gemini
- 🔐 **Gestione Sicura API Keys**: Variabili d'ambiente o file secrets
- 📎 **Upload File**: Carica e processa documenti (solo modalità locale/remota)
- 🎨 **Interfaccia Intuitiva**: UI Streamlit moderna e responsive
- ⚙️ **Parametri Configurabili**: Temperature, system prompt, modelli

## 🎥 Demo 00_interfaccia_dinamica_datapizza_Streamlit.py

![Demo Screenshot](screenshot.png)

## 🎥 Demo 01_interfaccia_con_memoria.py

![Demo Screenshot](screenshot1_1.png)

## 📋 Prerequisiti

- Python 3.8 o superiore
- pip (gestore pacchetti Python)
- [Ollama](https://ollama.ai/) (opzionale, per modelli locali)
- API Keys per provider cloud (opzionale)

## 🚀 Installazione

### Metodo 1: Script Automatico (Consigliato) ⭐

Questo metodo gestisce automaticamente l'ordine di installazione dei pacchetti.

#### Linux/Mac (se non funziona usare il punto 3. Installa le dipendenze nell'ordine corretto ):
```bash
git clone https://github.com/EnzoGitHub27/datapizza-streamlit-interface.git
cd datapizza-streamlit-interface
chmod +x install.sh
./install.sh
```

#### Windows (da testare!!!):
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
python -m venv deepaiug-interface
source deepaiug-interface/bin/activate  # Su Linux/Mac
# oppure
deepaiug-interface\Scripts\activate  # Su Windows
```

#### 3. Installa le dipendenze nell'ordine corretto

**⚠️ IMPORTANTE: L'ordine di installazione è cruciale!**

```bash
# 3.1 - Dipendenze base
pip install streamlit python-dotenv

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

---

### Metodo 3: Usando requirements.txt

⚠️ **Nota**: Alcuni utenti hanno riscontrato problemi con questo metodo. Se fallisce, usa il Metodo 2.

```bash
pip install -r requirements.txt
```

Se riscontri errori, il file `requirements.txt` contiene istruzioni per l'installazione manuale.

---

## 🔧 Configurazione API Keys

### Opzione A: File .env (Consigliata per sviluppo)

Crea un file `.env` nella root del progetto:

```bash
# .env
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

## 🎯 Utilizzo 

### Avvia l'applicazione 00_interfaccia_dinamica_datapizza_Streamlit.py

```bash
streamlit run 00_interfaccia_dinamica_datapizza_Streamlit.py
```

### Oppure Avvia l'applicazione 01_interfaccia_con_memoria.py

```bash
streamlit run 01_interfaccia_con_memoria.py
```

L'applicazione si aprirà automaticamente nel browser su `http://localhost:8501`

---

### Modalità d'uso

#### 🖥️ Locale (Ollama)

**Prerequisiti**: 
- Ollama installato e in esecuzione
- Almeno un modello scaricato (es: `ollama pull llama3.2`)

**Passi**:
1. Seleziona "Local (Ollama)" dalla sidebar
2. Clicca "🔄 Aggiorna Modelli" per rilevare i modelli disponibili
3. Seleziona un modello dalla lista
4. Inserisci il tuo prompt e clicca "🚀 Invia"

**Pro**: 
- ✅ Privacy totale (nessun dato inviato online)
- ✅ Gratuito
- ✅ Nessuna API key necessaria

---

#### 🌐 Remote Host

**Quando usarlo**: Hai un server con Ollama o altro LLM sulla tua rete locale

**Passi**:
1. Seleziona "Remote host" dalla sidebar
2. Inserisci l'indirizzo del server (es: `http://192.168.1.100:11434/v1`)
3. Configura il modello disponibile sul server
4. Invia il tuo prompt

**Pro**:
- ✅ Utilizza hardware più potente in rete
- ✅ Privacy (rete locale)

---

#### ☁️ Cloud Provider

**Quando usarlo**: Vuoi usare modelli cloud come GPT-4, Claude, Gemini

**Passi**:
1. Seleziona "Cloud provider" dalla sidebar
2. Scegli il provider:
   - **OpenAI**: GPT-4, GPT-3.5-turbo, ecc.
   - **Anthropic**: Claude Sonnet, Claude Opus
   - **Google**: Gemini Pro, Gemini Ultra
3. Inserisci la tua API key (o verrà caricata automaticamente se configurata)
4. Seleziona il modello
5. Invia il prompt

**⚠️ Attenzione**:
- I dati vengono inviati a server esterni
- Costi API applicabili
- Upload file disabilitato per privacy

---

## 📚 Documentazione

- [CHANGELOG](CHANGELOG.md) - Storia delle versioni e modifiche
- [ROADMAP](ROADMAP.md) - Piano di sviluppo futuro
- [CONTRIBUTING](CONTRIBUTING.md) - Guida per contribuire al progetto
```

## 🎯 **Struttura Finale Repository**
```
datapizza-streamlit-interface/
├── README.md                               ← Documentazione principale
├── CHANGELOG.md                            ← ✨ NUOVO: Storia versioni
├── ROADMAP.md                              ← ✨ NUOVO: Piano sviluppo
├── CONTRIBUTING.md                         ← ✨ NUOVO: Guida contributor
├── LICENSE                                 
├── .gitignore                              
├── requirements.txt                        
├── install.sh                              
├── install.bat                             
│
├── 00_interfaccia_dinamica_datapizza_Streamlit.py  ← v1.0.0 (STABILE su main)
├── 01_interfaccia_con_memoria.py                   ← v1.1.0 (STABILE su main)
│
├── secrets/
│   └── .gitkeep
│
└── examples/
    ├── client_factory_tutorial_datapizza-ai.py
    └── secrets_tutorial.py

```

---

## 🔧 Risoluzione Problemi

### Problema: "Module not found" durante l'avvio

**Soluzione**:
```bash
# Verifica che tutte le dipendenze siano installate
pip list | grep datapizza
pip list | grep streamlit

# Se mancano, reinstalla nell'ordine corretto (vedi Metodo 2)
```

### Problema: Errori durante `pip install -r requirements.txt`

**Soluzione**: Usa l'installazione manuale (Metodo 2) o lo script automatico (Metodo 1)

### Problema: Ollama non rileva modelli

**Soluzione**:
```bash
# Verifica che Ollama sia in esecuzione
ollama list

# Se non ci sono modelli, scaricane uno
ollama pull llama3.2

# Clicca "🔄 Aggiorna Modelli" nell'interfaccia
```

### Problema: "API key not found" per provider cloud

**Soluzione**:
1. Verifica che la chiave sia corretta
2. Controlla che sia nel formato giusto:
   - OpenAI: `sk-...`
   - Anthropic: `sk-ant-...`
   - Google: stringa alfanumerica
3. Usa l'interfaccia web per salvare la chiave (pulsante "💾 Salva API Key")

### Problema: "Repository not found" durante git push

**Soluzione**: Crea prima il repository su GitHub (vedi sezione Contribuire)

---

## 🎨 Personalizzazione

### Cambiare il System Prompt predefinito

Modifica la riga nel codice:
```python
system_prompt = st.sidebar.text_area(
    "System prompt",
    value="Sei un assistente utile e conciso.",  # ← Cambia qui
    height=100
)
```

### Aggiungere nuovi provider

1. Verifica se Datapizza AI supporta il provider
2. Installa il client: `pip install datapizza-ai-clients-{provider}`
3. Aggiungi l'opzione nel selectbox del codice
4. Configura il client in `create_client()`

---

## 🤝 Contribuire

I contributi sono benvenuti! Ecco come puoi aiutare:

### Setup per lo sviluppo

```bash
# 1. Fai un Fork del progetto su GitHub

# 2. Clona il tuo fork
git clone https://github.com/TUO-USERNAME/datapizza-streamlit-interface.git
cd datapizza-streamlit-interface

# 3. Aggiungi upstream
git remote add upstream https://github.com/EnzoGitHub27/datapizza-streamlit-interface.git

# 4. Crea branch per la tua feature
git checkout -b feature/amazing-feature

# 5. Fai le modifiche e testa

# 6. Commit
git add .
git commit -m '✨ Add amazing feature'

# 7. Push al tuo fork
git push origin feature/amazing-feature

# 8. Apri una Pull Request su GitHub verso il branch `dev`
```

### Branch Strategy

- **`main`**: Branch di produzione (stabile, solo release)
- **`dev`**: Branch di sviluppo (integrazione feature)
- **`feature/*`**: Branch per nuove funzionalità
- **`bugfix/*`**: Branch per correzioni bug

### Linee Guida

- ✅ Scrivi codice pulito e commentato
- ✅ Testa su Python 3.8, 3.9, 3.10, 3.11
- ✅ Aggiorna README se aggiungi nuove funzionalità
- ✅ Usa commit message descrittivi (emoji opzionali: ✨ feature, 🐛 bugfix, 📝 docs)

---

## 📝 TODO / Roadmap

- [ ] Supporto per conversazioni multi-turno con memoria
- [ ] Export conversazioni in Markdown/JSON/PDF
- [ ] Confronto side-by-side tra più modelli
- [ ] Supporto per streaming delle risposte in tempo reale
- [ ] Temi UI personalizzabili (dark/light mode avanzato)
- [ ] Statistiche d'uso e analytics
- [ ] Supporto per immagini (vision models GPT-4V, Claude 3)
- [ ] Supporto per modelli multimodali (audio, video)
- [ ] Docker container per deploy facile
- [ ] API REST per integrazioni
- [ ] Plugin system per estensioni

---

## 🐛 Segnalazione