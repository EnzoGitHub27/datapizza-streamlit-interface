# 📝 CHANGELOG

Tutte le modifiche significative al progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e il progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

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

*Datapizza Streamlit Interface - DeepAiUG © 2026*
