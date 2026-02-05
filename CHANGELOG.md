# 📝 CHANGELOG

Tutte le modifiche significative al progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e il progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

---

## [1.8.0] - 2026-02-05

### 🧠 UI Socratica Completa

Release che completa l'approccio socratico con 5 bottoni e toggle modalità.

### ✨ Nuove Funzionalità

- **🎭 Bottone "Confuta"**: Avvocato del diavolo
  - Analizza punti deboli del ragionamento
  - Identifica falle logiche e semplificazioni eccessive
  - Propone controesempi concreti
  - Critica costruttiva per rafforzare il pensiero

- **🪞 Bottone "Rifletti"**: Sfida la DOMANDA (non la risposta!)
  - Analizza il perimetro decisionale dell'utente
  - Svela assunzioni non dette nella domanda stessa
  - Chiede: "Cosa NON stai chiedendo che dovresti?"
  - Stimola meta-riflessione sul dialogo

- **🧠 Toggle Modalità Socratica** (sidebar):
  - 🚀 **Veloce**: Nessun bottone socratico (risposte immediate)
  - ⚖️ **Standard**: Bottoni visibili sotto le risposte (default)
  - 🧠 **Socratico**: Bottoni + invito esplicito a riflettere

- **📊 UI Raggruppata**: Bottoni organizzati in 2 sezioni
  - "Analizza la risposta:" → 4 bottoni (Alternative, Assunzioni, Limiti, Confuta)
  - "Sfida la domanda:" → 1 bottone (Rifletti)

### 🔧 Modifiche Tecniche

- `config/constants.py`: +SOCRATIC_MODES dict, +DEFAULT_SOCRATIC_MODE
- `ui/socratic/prompts.py`: +template "confute" e "reflect", +get_reflect_prompt()
- `ui/socratic/buttons.py`: +generate_confute(), +generate_reflect(), UI raggruppata
- `ui/sidebar/llm_config.py`: +sezione toggle modalità, return con 9° valore
- `ui/chat.py`: Passaggio user_question e socratic_mode a render_socratic_buttons
- `app.py`: Gestione completa socratic_mode

### 🎨 Rebranding Completo

- Tutti i commenti header aggiornati: "Datapizza" → "DeepAiUG"
- User-Agent MediaWiki: "DatapizzaBot" → "DeepAiUGBot"

### 📝 Note

- Il bottone "Rifletti" richiede la domanda utente precedente
- Se non c'è domanda (es. primo messaggio), il bottone non appare
- Retrocompatibilità: se socratic_mode non esiste, default = "standard"

---

## [1.7.1] - 2026-01-29

### 🌐 Remote Servers + Sicurezza + Rebranding

Miglioramenti significativi alla gestione dei server remoti, sicurezza API keys e rebranding UI.

### ✨ Nuove Funzionalità

- **📋 File `remote_servers.yaml`**: Configurazione centralizzata per server Ollama remoti
  - 3 modalità: `fixed`, `selectable`, `custom_allowed`
  - Server predefiniti con nome, icon, host, port, descrizione
  - Settings avanzati (timeout, refresh button)
  - Retrocompatibilità: se il file non esiste, comportamento legacy

- **🔄 Lista modelli dinamica per Remote**: Bottone "Aggiorna modelli"
  - Recupera modelli via API HTTP (`/api/tags`)
  - Dropdown popolato automaticamente come per Local Ollama
  - Metric con numero modelli trovati

### 🐛 Bugfix

- **🔑 API Key Cloud modificabile**: Fix bug che impediva modifica API key salvata
  - Text input sempre visibile e modificabile (se configurato)
  - Session state per gestire modifiche
  - Bottone "💾 Salva modifiche" per aggiornare key esistente

### 🔒 Sicurezza

- **📋 File `security_settings.yaml`**: Configurazione visibilità API Keys
  - Controllo visibilità API key salvate (default: nascoste per sicurezza)
  - Impostazione `show_saved_keys: false` = key nascoste (default)
  - Impostazione `show_saved_keys: true` = key visibili (solo se sistemista lo configura)
  - Bottone "🔄 Usa altra key" per cambiare key senza vederla
  - Messaggi personalizzabili per key visibili/nascoste
  - Previene copia accidentale di credenziali sensibili

### 🎨 Rebranding

- **🧠 DeepAiUG Chat**: Nuovo titolo e identità visiva
  - Titolo app: "🍕 Datapizza Chat" → "🧠 DeepAiUG Chat"
  - Icon browser: 🍕 → 🧠
  - Riflette il focus sull'approccio socratico e sul capitale semantico

### 🔧 Modifiche Tecniche

- `remote_servers.yaml`: Nuovo file di configurazione (opzionale)
- `security_settings.yaml`: Nuovo file per impostazioni sicurezza (opzionale)
- `config/constants.py`: +2 costanti (remote servers + security settings)
- `config/settings.py`: +8 funzioni (5 remote servers, 3 security)
- `core/llm_client.py`: Nuova funzione `get_remote_ollama_models(base_url)`
- `ui/sidebar/llm_config.py`: Sezione Remote riscritta + Cloud con gestione sicurezza API key
- `app.py`: Titolo "DeepAiUG Chat" + icon 🧠

### 📝 Note

- **Firewall/VPN**: Se il server remoto blocca endpoint `/v1/*`, le chat potrebbero fallire con 404
  - Verifica che il server Ollama abbia OpenAI-compatible API attiva
  - In alternativa usa server senza restrizioni firewall

---

## [1.7.0] - 2026-01-27

### 🧠 Espansione Approccio Socratico

Aggiunti 2 nuovi bottoni socratici per stimolare pensiero critico e consapevolezza dei limiti.

### ✨ Nuove Funzionalità

- **🤔 Bottone "Assunzioni"**: Analizza le assunzioni implicite
  - Mostra cosa la risposta dà per scontato
  - Aiuta a identificare presupposti non esplicitati
  - Stimola domande: "Questo vale anche nel mio caso?"

- **⚠️ Bottone "Limiti"**: Identifica quando la risposta NON funziona
  - Mostra i limiti di validità della soluzione
  - Aiuta a capire i casi limite ed eccezioni
  - Previene applicazioni errate della risposta

### 🔧 Modifiche Tecniche

- `ui/socratic/buttons.py`:
  - Aggiunte funzioni `generate_assumptions()` e `generate_limits()`
  - Esteso `render_socratic_buttons()` per 3 bottoni (era 1)
  - Layout colonne: `[2, 2, 2, 4]` per ospitare i nuovi bottoni
  - Cache indipendente per ogni tipo di analisi
  - Spinner personalizzati per ogni bottone

- `ui/socratic/prompts.py`:
  - Template già presenti da v1.6.1, ora attivati

### 🎯 Impatto UX

I 3 bottoni socratici ora coprono:
1. **🔄 Alternative** - Pensiero laterale (prospettive diverse)
2. **🤔 Assunzioni** - Pensiero critico (cosa si dà per scontato)
3. **⚠️ Limiti** - Pensiero prudente (quando NON usare la risposta)

### 🔮 Prossime Feature Socratiche

- **v1.8.0**: Bottone "🎭 Confuta" (avvocato del diavolo)
- **v1.9.0**: Toggle modalità (Veloce / Standard / Socratico)

---

## [1.6.1] - 2026-01-26

### 🧠 Novità - Approccio Socratico

DeepAiUG evolve da semplice interfaccia chat a **strumento socratico** per costruire comprensione.

Ispirato al concetto di **"capitale semantico"** (Floridi/Quartarone):
> L'AI produce significato plausibile, ma il SENSO lo costruisce l'umano.

### ✨ Nuove Funzionalità

- **🔄 Bottone "Genera alternative"**: Sotto ogni risposta AI
  - Genera 3 interpretazioni alternative dello stesso problema
  - Ogni alternativa basata su presupposti diversi
  - Stimola il pensiero critico e la riflessione
  
- **Nuovo modulo `ui/socratic/`**:
  - `prompts.py`: Template prompt socratici (alternative, assunzioni, limiti, confuta)
  - `buttons.py`: Logica e rendering bottoni
  - Cache risposte per evitare rigenerazioni

### 🎯 Filosofia

Le 4 capacità che DeepAiUG vuole allenare:
1. **Costruzione di senso** - collegare informazioni
2. **Valutazione semantica** - capire cosa conta
3. **Contestualizzazione** - collocare nel contesto giusto
4. **Resistenza alla plausibilità** - non fidarsi del "suona giusto"

### 📁 Nuovi File

```
ui/socratic/
├── __init__.py
├── prompts.py    # Template prompt socratici
└── buttons.py    # Logica bottoni
```

### 🔧 Modifiche Tecniche

- `app.py`: Aggiunto supporto client socratico
- `ui/chat.py`: Integrazione bottoni sotto risposte AI
- `ui/__init__.py`: Export modulo socratic
- `config/constants.py`: VERSION → 1.6.1

### 🔮 Prossime Feature Socratiche (v1.7.0+)

- Bottoni "🤔 Assunzioni" e "⚠️ Limiti"
- Bottone "🎭 Confuta"
- Toggle modalità: Veloce / Standard / Socratico

---

## [1.6.0] - 2026-01-25

### ✨ Novità

- **Streaming Responses**: Le risposte dell'AI ora appaiono token-by-token in tempo reale!
  - Esperienza utente simile a ChatGPT/Claude.ai
  - Visualizzazione progressiva del testo durante la generazione
  - Sensazione di maggiore reattività e velocità

### ✅ Provider Supportati

- ✅ **Ollama locale**: Streaming perfetto e fluido
- ✅ **Remote host**: Streaming perfetto e fluido
- ⚠️ **Cloud providers** (OpenAI, Anthropic, Google): In arrivo

### 🔧 Implementazione Tecnica

- Sostituito `client.invoke()` con `client.stream_invoke()`
- Creato `response_generator()` per estrarre testo incrementale dai chunk
- Usato `st.write_stream()` per visualizzazione real-time
- Implementata deduplica testo per evitare ripetizioni

### 🎨 UI/UX

- **Footer aggiornato**: Nuovo branding "🤖 DeepAiUG by Gilles"
- Rimosso spinner "sta pensando..." (sostituito da streaming progressivo)
- Migliore percezione di velocità durante le risposte lunghe

### 🐛 Bug Fix

- Risolto problema di ripetizione testo durante streaming
- Implementato tracking `previous_text` per calcolare delta correttamente

---

## [1.5.1] - 2026-01-16

### 🐛 Bug Fix

- **CRITICAL FIX**: Wiki non funzionavano per pacchetti mancanti
  - Problema: `mwclient` e `dokuwiki` non erano installati nel venv
  - Soluzione: Aggiornato README con istruzioni installazione dipendenze

### ✨ Novità

- **Wiki Pubbliche di Test**: Aggiunte 4 wiki pronte all'uso
  - 🌐 Wikipedia IT - Intelligenza Artificiale (30 pagine)
  - 🌎 Wikipedia EN - Artificial Intelligence (20 pagine)
  - ✈️ Wikivoyage IT - Guide viaggio Italia (15 pagine)
  - 📚 Wikibooks IT - Manuali Informatica (20 pagine)

### 🔧 Miglioramenti

- Aggiunti script di test: `test_wiki.py` e `test_all_wikis.py`
- Migliorata documentazione setup venv e dipendenze

---

## [1.5.0] - 2026-01-11

### ✨ Novità

- **File Upload in Chat**: Allegare file direttamente nella chat
  - 📄 Documenti: PDF, TXT, MD, DOCX
  - 🖼️ Immagini: PNG, JPG, JPEG, GIF, WEBP (richiede modello Vision)

- **Privacy-First Upload**: Upload disabilitato con Cloud provider
  - Protegge i documenti sensibili dall'invio a servizi esterni

- **🔐 Privacy Dialog**: Warning automatico passaggio Local→Cloud

### 📦 Dipendenze

- Aggiunto: `python-docx>=0.8.0`
- Aggiunto: `Pillow>=10.0.0`

---

## [1.4.1] - 2026-01-09

### ✨ Nuove Funzionalità

- **Supporto Multi-Wiki**: MediaWiki + DokuWiki
- **Nuovo formato `wiki_sources.yaml`** con campo `type`
- **UI Multi-Tipo** con icone

### 📦 Nuove Dipendenze

- `dokuwiki>=0.1.0`

---

## [1.4.0] - 2026-01-08

### ♻️ Refactoring Completo - Architettura Modulare

Da monolite (2287 righe) a packages Python strutturati.

---

## [1.3.x] - 2026-01-05/07

- Knowledge Base RAG completo
- MediaWiki Adapter
- Export multi-formato (MD, JSON, TXT, PDF, ZIP)

---

## [1.2.0] - 2026-01-04

- Export conversazioni multi-formato

---

## [1.1.x] - 2026-01-02/03

- Conversazioni multi-turno
- Persistenza su file JSON

---

## [1.0.0] - 2026-01-01

### 🎉 Release Iniziale

- Multi-Provider: Ollama, Remote, Cloud
- UI Streamlit moderna

---

## Legenda

- ✨ **Nuove Funzionalità**
- 🐛 **Bug Fix**
- 🔧 **Miglioramenti**
- ♻️ **Refactoring**
- 📦 **Dipendenze**
- 🧠 **Approccio Socratico**

---

*DeepAiUG Streamlit Interface © 2026*
