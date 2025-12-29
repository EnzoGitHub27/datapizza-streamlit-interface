# 🍕 Datapizza Streamlit LLM Interface

Interfaccia web completa per interagire con Large Language Models (LLM) locali, remoti e cloud tramite il framework [Datapizza AI](https://github.com/datapizza-labs/datapizza-ai).
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

## 🎥 Demo

![Demo Screenshot](screenshot.png)

## 📋 Prerequisiti

- Python 3.8 o superiore
- [Ollama](https://ollama.ai/) (opzionale, per modelli locali)
- API Keys per provider cloud (opzionale)

## 🚀 Installazione

### 1. Clona il repository
```bash
git clone https://github.com/EnzoGitHub27/datapizza-streamlit-interface.git
cd datapizza-streamlit-interface
```

### 2. Crea un ambiente virtuale (consigliato)
```bash
python3 -m venv deepaiug-interface
source deepaiug-interface/bin/activate  # Su Linux/Mac
# oppure
deepaiug-interface\Scripts\activate  # Su Windows
```

### 3. Installa le dipendenze

#### Opzione A: Installazione Completa (consigliata)
```bash
pip install -r requirements.txt

# NOTA BENE: se non funziona con "requirements.txt" installa uno ad uno i pachetti facendo riferimento
# alla documentazione Datapizza AI e Streamlit oppure tutti i comandi specifici indicati di seguito nella Opzione B
```

Questo installerà:
- `datapizza-ai` (core framework)
- `datapizza-ai-clients-openai` (supporto OpenAI)
- `datapizza-ai-clients-anthropic` (supporto Claude)
- `datapizza-ai-clients-google` (supporto Gemini)
- `streamlit` (interfaccia web)
- `python-dotenv` (gestione variabili d'ambiente)

#### Opzione B: Installazione Selettiva
Se vuoi solo provider specifici:
```bash
# How to install Datapizza AI
pip install datapizza-ai

# Solo per Ollama locale (nessun client cloud necessario)
pip install datapizza-ai-clients-openai-like streamlit python-dotenv

# Solo OpenAI
pip install datapizza-ai datapizza-ai-clients-openai streamlit python-dotenv

# Solo Anthropic (Claude)
pip install datapizza-ai datapizza-ai-clients-anthropic streamlit python-dotenv

# Solo Google (Gemini)
pip install datapizza-ai datapizza-ai-clients-google streamlit python-dotenv
```

### 4. Configura le API Keys (opzionale)

#### Opzione A: File .env
```bash
# Crea un file .env nella root del progetto
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
echo "GOOGLE_API_KEY=your-gemini-key-here" >> .env
```

#### Opzione B: File secrets
```bash
# Crea i file nella cartella secrets/
echo "sk-your-openai-key" > secrets/openai_key.txt
echo "sk-ant-your-anthropic-key" > secrets/anthropic_key.txt
echo "your-gemini-key" > secrets/google_key.txt
```

## 🎯 Utilizzo

### Avvia l'applicazione
```bash
streamlit run 00_interfaccia_dinamica_datapizza_Streamlit.py
```

L'applicazione si aprirà automaticamente nel browser su `http://localhost:8501`

### Modalità d'uso

#### 🖥️ Locale (Ollama)
1. Seleziona "Local (Ollama)" dalla sidebar
2. Assicurati che Ollama sia in esecuzione
3. Seleziona un modello dalla lista rilevata automaticamente
4. Inserisci il tuo prompt e clicca "Invia"

#### 🌐 Remote Host
1. Seleziona "Remote host" dalla sidebar
2. Inserisci l'indirizzo del server remoto
3. Configura il modello disponibile
4. Invia il tuo prompt

#### ☁️ Cloud Provider
1. Seleziona "Cloud provider" dalla sidebar
2. Scegli il provider (OpenAI, Anthropic, Google Gemini)
3. Inserisci la tua API key (o sarà caricata automaticamente)
4. Seleziona il modello e invia il prompt

## 📁 Struttura del Progetto
```
datapizza-streamlit-interface/
├── 00_interfaccia_dinamica_datapizza_Streamlit.py  # App principale
├── README.md                                        # Documentazione
├── requirements.txt                                 # Dipendenze Python
├── LICENSE                                          # Licenza MIT
├── .gitignore                                       # File da ignorare
├── secrets/                                         # Cartella per API keys
│   └── .gitkeep
└── examples/                                        # Esempi di codice
    ├── client_factory_tutorial_datapizza-ai.py
    └── secrets_tutorial.py
```

## 🔧 Configurazione Avanzata

### Personalizza System Prompt
Modifica il system prompt dalla sidebar per cambiare il comportamento del modello.

### Regola la Temperature
Usa lo slider temperature (0.0-2.0) per controllare la creatività:
- **0.0-0.3**: Risposte deterministiche e precise
- **0.7-1.0**: Bilanciamento creatività/coerenza
- **1.5-2.0**: Risposte molto creative

### Upload File
In modalità locale/remota puoi caricare documenti che verranno inclusi nel contesto.

## 🤝 Contribuire

I contributi sono benvenuti! Ecco come puoi aiutare:

1. Fai un Fork del progetto
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📝 TODO / Roadmap

- [ ] Supporto per conversazioni multi-turno con memoria
- [ ] Export conversazioni in Markdown/JSON
- [ ] Confronto side-by-side tra più modelli
- [ ] Supporto per streaming delle risposte
- [ ] Temi UI personalizzabili
- [ ] Statistiche d'uso e analytics
- [ ] Supporto per immagini (vision models)

## 🐛 Bug e Problemi

Se incontri problemi, apri una [Issue](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/issues) descrivendo:
- Sistema operativo
- Versione Python
- Messaggio di errore completo
- Passi per riprodurre il problema

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file [LICENSE](LICENSE) per i dettagli.

## 🙏 Ringraziamenti

- [Datapizza AI](https://github.com/datapizza-labs/datapizza-ai) - Framework LLM
- [Streamlit](https://streamlit.io/) - Framework UI
- [Ollama](https://ollama.ai/) - Runtime per modelli locali
- [DeepAiUG](https://deepaiug.vercel.app/) - Progetto DeepAiUG

## 👤 Autore

**Gilles (Enzo) - DeepAiUG**

- GitHub: [@EnzoGitHub27](https://github.com/EnzoGitHub27)
- Repository: [datapizza-streamlit-interface](https://github.com/EnzoGitHub27/datapizza-streamlit-interface)

---

⭐ Se questo progetto ti è stato utile, lascia una stella su GitHub!
```

#### **📄 secrets/.gitkeep**
```
# Questo file mantiene la cartella secrets/ nel repository
# I file *.txt in questa cartella sono ignorati da git per sicurezza