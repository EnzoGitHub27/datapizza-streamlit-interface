# Changelog

Tutte le modifiche notevoli a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/lang/it/).

---

## [Unreleased] - Branch Dev 🚧

### In Sviluppo Attivo
Nessuna feature attualmente in sviluppo. Controlla [ROADMAP.md](ROADMAP.md) per i piani futuri.

---

## [1.0.0] - 2025-01-02 🎉

### Aggiunto
- ✨ **Interfaccia Streamlit completa** per interazione con LLM
- 🖥️ **Supporto modelli locali** tramite Ollama
  - Rilevamento automatico modelli installati
  - Pulsante refresh per aggiornare lista modelli
  - Configurazione endpoint personalizzato
- 🌐 **Supporto host remoti**
  - Configurazione multipli endpoint
  - Selezione dinamica host dalla sidebar
  - API key opzionale per server protetti
- ☁️ **Supporto provider cloud**
  - OpenAI (GPT-4, GPT-3.5-turbo, ecc.)
  - Anthropic (Claude Sonnet, Opus)
  - Google (Gemini Pro, Ultra)
  - Custom cloud provider con configurazione flessibile
- 🔐 **Gestione sicura API keys**
  - Caricamento da variabili d'ambiente
  - Caricamento da file `.env`
  - Caricamento da file `secrets/{provider}_key.txt`
  - Salvataggio API keys direttamente dall'interfaccia web
  - Indicatore visivo chiave presente/mancante
- 📎 **Upload file con anteprima**
  - Drag & drop multiplo
  - Supporto file di testo con preview
  - Supporto file binari con metadati
  - Opzione incorporamento contenuto nel prompt
  - Disabilitato automaticamente in modalità cloud per privacy
- ⚙️ **Parametri configurabili**
  - Temperature slider (0.0-2.0)
  - System prompt personalizzabile
  - Selezione modello dinamica
- 🎨 **UI/UX**
  - Layout responsive a due colonne
  - Indicatori visivi per tipo connessione
  - Alert contestuali per modalità cloud
  - Metriche modello selezionato
  - Statistiche risposta (caratteri, parole)
  - Preview espandibile file caricati
- 💾 **Funzionalità di export**
  - Download risposta in formato .txt
  - Download file caricati
  - Copia risposta negli appunti
- 🧹 **Gestione sessione**
  - Pulsante pulisci per reset interfaccia
  - Session state per persistenza risposta
  - Memoria ultima richiesta e modello usato

### Sicurezza
- 🔒 File `.gitignore` completo per protezione secrets
  - Esclusione cartella `secrets/`
  - Esclusione file `.env`
  - Esclusione virtual environments
  - Esclusione configurazioni IDE
- 🛡️ **Protezione privacy modalità cloud**
  - Warning visibile su invio dati esterni
  - Upload file disabilitato
  - Styling rosso per evidenziare rischi
  - Messaggi informativi contestuali

### Documentazione
- 📖 README.md completo con:
  - Istruzioni installazione multiple (automatica, manuale, requirements.txt)
  - Guida configurazione API keys (4 metodi)
  - Esempi d'uso per tutte le modalità
  - Sezione troubleshooting
  - Guide contribuzione
- 📜 LICENSE MIT inclusa
- 🔧 Script di installazione automatica:
  - `install.sh` per Linux/Mac
  - `install.bat` per Windows
- 📦 `requirements.txt` con note installazione manuale
- 📚 Cartella `examples/` con tutorial datapizza

### Infrastruttura
- 🌿 Strategia branching: `main` (stabile) + `dev` (sviluppo)
- 🏷️ Sistema di tagging semantico (v1.0.0)
- 🔧 Configurazione git ignore completa
- 📁 Struttura progetto organizzata

### Compatibilità
- 🐍 Python 3.8+
- 🍕 Datapizza AI framework
- 🎈 Streamlit 1.28+
- 🦙 Ollama (opzionale, per locale)

---

## Come Leggere Questo Changelog

### Tipi di Modifiche
- **Aggiunto**: per nuove funzionalità
- **Modificato**: per cambiamenti a funzionalità esistenti
- **Deprecato**: per funzionalità che verranno rimosse
- **Rimosso**: per funzionalità rimosse
- **Corretto**: per bug fix
- **Sicurezza**: per vulnerabilità corrette

### Versioning
Usiamo [Semantic Versioning](https://semver.org/lang/it/):
- **MAJOR** (1.x.x): Cambiamenti incompatibili con API precedenti
- **MINOR** (x.1.x): Nuove funzionalità backward-compatible
- **PATCH** (x.x.1): Bug fix backward-compatible

---

## Link Utili
- [Repository GitHub](https://github.com/EnzoGitHub27/datapizza-streamlit-interface)
- [Issues](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/issues)
- [Roadmap](ROADMAP.md)
- [Contributing](CONTRIBUTING.md)