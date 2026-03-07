# 📝 CHANGELOG

Tutte le modifiche significative al progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e il progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

---

## [1.13.0] — 2026-03-07

### Aggiunto
- **F3 Vault Support**: riconoscimento automatico Obsidian, LogSeq, Notion Export
- Banner UI dedicato con icona e conteggio file per tipo vault
- Parser nativo .canvas Obsidian (estrae testo dai nodi)
- Aggiornamento incrementale vault basato su timestamp file
- Filtro file per tipo vault (esclude .obsidian/, logseq/bak/, ecc.)
- Costanti VAULT_TYPES in config/constants.py
- Nuovo modulo `rag/vault.py` con funzioni detect, scan, parse, update

### Modificato
- `ui/sidebar/knowledge_base.py`: flusso selezione con riconoscimento vault automatico
- `rag/adapters/local_folder.py`: supporto file .canvas in `_load_single_file()`
- `config/constants.py`: VERSION → 1.13.0

---

## [1.12.1] - 2026-03-03 — Fix installer Windows

### Fixed

- `installer/INSTALLA_DeepAiUG.bat`: aggiornamento PATH dopo installazione Ollama (fix popup "file non trovato")
- `installer/INSTALLA_DeepAiUG.bat`: sostituito WebClient con Invoke-WebRequest (fix errore DownloadProgressChanged)
- `installer/INSTALLA_DeepAiUG.bat`: stderr Ollama serve reindirizzato a nul (eliminato messaggio "handle is invalid")

---

## [1.12.0] - 2026-03-03 — Architettura Sidebar

### Changed

- Sidebar riorganizzata in 5 sezioni distinte con ordine fisso
- ⚙️ **Configurazione** in `st.expander` chiuso di default (connessione, modello, parametri, Knowledge Base)
- 💬 **Conversazione**, 🗺️ **Mappa Sessione**, 🧠 **Modalità Socratica**, 📤 **Export** — aperte di default
- Banner "Novità" ora dinamico: legge `VERSION` da `config/constants.py` invece di valore hardcoded
- `render_llm_config()` accetta parametro `container` per supporto expander
- `render_knowledge_base_config()` accetta parametro `container` con pattern `_container` a livello di modulo
- `render_socratic_mode_settings()` estratta come funzione indipendente

### 🔧 Modifiche Tecniche

- `ui/sidebar/llm_config.py`: +`container` param, return 8 valori (era 9), +`render_socratic_mode_settings()`
- `ui/sidebar/knowledge_base.py`: +`container` param, `_container` modulo per ~10 helpers privati
- `ui/sidebar/conversations.py`: Header rinominato "💬 Conversazione"
- `ui/sidebar/export_ui.py`: Header rinominato "📤 Export"
- `ui/sidebar/__init__.py`: +export `render_socratic_mode_settings`
- `app.py`: Sidebar ristrutturata con `st.sidebar.expander` + nuovo ordine 5 sezioni
- `config/constants.py`: VERSION → 1.12.0, VERSION_DESCRIPTION → "Architettura Sidebar"
- `config/branding.py`: default `news_banner.version` usa `VERSION` invece di stringa hardcoded
- `branding.yaml`: rimossi `text` e `version` hardcoded (delegati ai default dinamici)

### 📝 Note

- **Solo UI**: nessuna modifica alla logica applicativa, session_state o prompt socratici
- La logica session map (nudge, genera, rigenera) resta identica, solo riposizionata nella sidebar

---

## [1.11.1] - 2026-02-27 — Matrix Theme

### ✨ Nuove Funzionalità

- **🎨 Matrix Theme**: Tema visivo completo ispirato a The Matrix
  - Background scuro `#020c06` con scanlines CRT overlay
  - Palette teal/green: `#00d4aa` (primary), `#00ff41` (accent), `#c8ffd4` (text)
  - Glitch animation su titolo H1 (Cinzel serif)
  - Tipografia: Cinzel (H1), Exo 2 (H2/H3/chat), Share Tech Mono (bottoni/input/metric)
  - Chat bubbles, bottoni, input, selectbox, expander, metric, alert tutti stilizzati
  - Scrollbar personalizzata teal 3px
  - Matrix rain canvas animation (katakana + hex + simboli matematici, opacity 5.5%)
  - `branding.yaml`: `matrix_rain` (on/off) e `matrix_rain_intensity` (opacità) configurabili

### 📁 Nuovi File

```
.streamlit/config.toml   # Tema Streamlit nativo (primaryColor, bg, font monospace)
ui/style.py              # inject_matrix_style(), _inject_css(), _inject_matrix_rain()
```

### 🔧 Modifiche Tecniche

- `app.py`: +import `inject_matrix_style`, chiamata subito dopo `st.set_page_config()`
- `ui/__init__.py`: +import e +`__all__` entry per `inject_matrix_style`
- `config/constants.py`: VERSION → 1.11.1, VERSION_DESCRIPTION → "Matrix Theme"
- `config/branding.py`: +`MATRIX_RAIN_ENABLED`, +`MATRIX_RAIN_INTENSITY`, merge scalari in `load_branding()`
- `branding.yaml`: +`matrix_rain`, +`matrix_rain_intensity`

### 📝 Note

- **Solo stile**: nessuna modifica alla logica applicativa esistente
- Il tema Streamlit nativo (`.streamlit/config.toml`) imposta i colori base; il CSS custom in `ui/style.py` aggiunge tipografia, animazioni e dettagli
- La matrix rain usa `streamlit.components.v1.html()` con `height=0` per non occupare spazio nel layout

---

## [1.11.0] - 2026-02-24 — Branding + UX Polish

### ✨ Nuove Funzionalità

- **🎨 branding.yaml**: Titolo, icona e banner novità personalizzabili
  senza modificare il codice. Fallback silenzioso se file assente.
- **🤖 Nome modello + timestamp** negli output socratici (tutti e 5 i bottoni)
- **🤖 Nome modello + timestamp** nella mappa sessione
- **📊 Mappa collassabile**: expander sidebar per recuperare spazio
- **🔄 Bottone "Rigenera mappa"**: rigenera dopo ulteriori domande
- **📊 Bottone "Genera mappa"**: disponibile su conversazioni caricate

### 🐛 Bug Fix

- **Parser frecce vuote**: `_parse_llm_response()` riscritto con regex +
  separatori multipli (→, ->, :) + fallback testo grezzo.
  Nessuna freccia vuota con nessun modello.
- **Posizione nudge**: spostato dentro la sezione "Mappa sessione" in sidebar
- **Reset mappa su caricamento**: la mappa della sessione precedente
  non resta più visibile quando si carica un'altra conversazione

### 🔧 Modifiche Tecniche

- `branding.yaml` (root): Nuovo file configurazione personalizzazione UI
- `config/branding.py`: `load_branding()` + 6 costanti modulo (APP_TITLE, APP_ICON, APP_SUBTITLE, NEWS_BANNER_*)
- `config/__init__.py`: +12 export (6 branding + 4 session map da costanti precedenti)
- `app.py`: Valori hardcoded sostituiti con costanti branding, nudge spostato in sidebar
- `ui/socratic/buttons.py`: +`_render_model_timestamp()` in 5 expander
- `ui/socratic/session_map.py`: Parser riscritto con `re.match`, `import re` al top
- `ui/sidebar/session_map_widget.py`: +`render_generate_map_button()`, expander collassabile, popover tooltip, parametro `model_name`
- `ui/sidebar/conversations.py`: Reset stato F2 su caricamento conversazione

---

## [1.10.0] - 2026-02-23 — Mappa Sessione (F2)

### Filosofia
I bottoni socratici (v1.8.0) restituiscono attrito sulla singola risposta.
La Mappa Sessione restituisce attrito sul **pensiero**: rende visibile la
cornice interpretativa invisibile che si costruisce domanda dopo domanda.

Indirizza il concetto di **sovrascopo** (Cinzia Ligas, AI Semiology):
la direzione simbolica in cui, risposta dopo risposta, viene condotta
la semiosfera dell'utente — spesso senza che se ne accorga.

La mappa non si costruisce in background. Viene generata **solo su
richiesta esplicita** dell'utente, coerentemente con il principio di
delega consapevole (Quartarone): il momento della delega resta in mano
all'umano.

### ✨ Nuove Funzionalità

- **📊 Mappa Sessione** — Analisi della cornice interpretativa della sessione:
  - **Frame dominante**: la cornice implicita emersa dalle domande
  - **Connessione domande → frame**: come ogni domanda ha costruito/rinforzato il frame
  - **Frame non esplorati**: prospettive alternative non percorse (solo domande, non risposte)

- **🔄 Modalità Progressiva**: la mappa si aggiorna dopo ogni risposta,
  visibile dopo 4 domande

- **🔔 Modalità A soglia** (default): nudge dopo 5 domande —
  l'utente decide se aprire la mappa. Il nudge appare una sola volta per sessione.

- **⏹️ Modalità Disattivata**: nessuna mappa, nessun nudge

- **❓ Tooltip "Cos'è la Mappa Sessione?"**: spiegazione in-app con
  crediti filosofici (Ligas, Quartarone, Floridi)

### 📁 Nuovi File

```
ui/socratic/
└── session_map.py            # SessionMapEntry, SessionMap, SessionMapAnalyzer

ui/sidebar/
└── session_map_widget.py     # Widget sidebar: settings, nudge, display, tooltip
```

### 🔧 Modifiche Tecniche

- `config/constants.py`: +SESSION_MAP_MODES, +DEFAULT_SESSION_MAP_MODE, +SESSION_MAP_NUDGE_THRESHOLD, +SESSION_MAP_PROGRESSIVE_VISIBLE_AFTER, VERSION → 1.10.0
- `ui/socratic/__init__.py`: +6 export (SessionMapEntry, SessionMap, SessionMapAnalyzer, SESSION_MAP_KEY, extract_user_questions, get_nudge_text)
- `app.py`: +4 session_state keys (session_map_mode, session_map_data, n_domande_sessione, nudge_mostrato), logica post-risposta, nudge sidebar, reset su nuova conversazione

### 📝 Note

- **Privacy-first**: la mappa usa lo stesso client LLM già configurato, nessuna chiamata esterna aggiuntiva
- **Su richiesta**: modalità "off" → nessuna analisi; "threshold" → solo se utente clicca; "progressive" → automatica dopo N domande
- **Moduli HSCI coperti**: M2 (Gestione ambiguità), M8 (Pianificazione controllata)

---

## [1.9.2] - 2026-02-20 — Prompt Epistemologici Potenziati

### Filosofia
Questa versione non aggiunge nuovi bottoni né nuove funzionalità visibili.
Interviene in profondità sulla qualità del "lavoro semantico" richiesto all'utente:
i 5 template prompt socratici sono stati riscritti seguendo un framework
epistemologico esplicito, ispirato a Floridi, Umberto Eco (Lector in Fabula)
e al lavoro teorico di Carmelo Quartarone sull'asimmetria AI-umano.

La decisione di NON implementare un validatore automatico AI-su-AI (proposto
come alternativa) è coerente con la filosofia DeepAiUG: il test epistemologico
è l'umano, non un'altra AI. I prompt restituiscono attrito strutturato,
non punteggi o giudizi delegati alla macchina.

### Modifiche — ui/socratic/prompts.py

**🔄 Alternative** (v1.6.1 → v1.9.2)
Prima: generava 3 interpretazioni alternative con formato fisso.
Ora: distingue tre tipi epistemicamente diversi — Alternative di Soluzione
(approcci diversi allo stesso obiettivo), Alternative di Framing
(riformulazioni del problema), Alternative di Assunzione (cosa cambia
se il contesto è diverso). Per ciascuna indica in quale contesto
decisionale avrebbe senso.

**🤔 Assunzioni** (v1.7.0 → v1.9.2)
Prima: elencava assunzioni implicite in modo generico.
Ora: classifica il contenuto della risposta in tre livelli epistemici —
Fatti (verificabili), Inferenze (probabilistiche), Valutazioni (normative,
dipendenti da chi decide). Per le inferenze chiave aggiunge il Test della
Premessa: "Se questa inferenza fosse errata, quali conclusioni sopravvivono?
Quali cadono?"

**⚠️ Limiti** (v1.7.0 → v1.9.2)
Prima: elencava situazioni in cui la risposta non funzionava.
Ora: distingue Limiti di Dominio (campo instabile o controverso),
Limiti di Contesto (informazioni mancanti, ipotesi errate sul destinatario),
Limiti del Modello (il tipo di lettore implicito presupposto dalla risposta,
concetto da Eco/Ligas). Conclude con quali parti restano valide e quali
richiedono verifica prima di agire.

**🎭 Confuta** (v1.8.0 → v1.9.2)
Prima: avvocato del diavolo generico su punti deboli e controesempi.
Ora: opera su due livelli distinti — Livello 1 (Confutazione delle
Conclusioni: obiezioni di un esperto critico) e Livello 2 (Confutazione
della Struttura: se le premesse fondanti fossero false, quali parti
collassano? Quali reggono?). Il secondo livello è il salto qualitativo
principale: non confuta le risposte ma testa la tenuta logica della
struttura argomentativa.

**🪞 Rifletti** (v1.8.0 → v1.9.2)
Prima: 3 domande provocatorie su perimetro decisionale, assunzioni e
giustificabilità.
Ora: analizza la domanda dell'utente su tre dimensioni — Presupposizioni
(cosa deve essere già vero perché la domanda abbia senso), Destinatario
Implicito (come cambia la risposta se chi decide ha ruolo/valori/vincoli
diversi), Domanda sotto la Domanda (il problema più profondo o più preciso
che sarebbe più utile affrontare). Introduce esplicitamente il concetto
di non-neutralità della risposta AI (Eco: ogni testo presuppone un
Lettore Modello).

### File modificati
- `ui/socratic/prompts.py` — 5 template riscritti, funzioni helper invariate

---

## [1.9.1] - 2026-02-11

### 🎨 UI Polish + Cloud Config + Privacy Granulare

Release di miglioramento UI, configurabilità modelli cloud e rilevamento granulare contenuti sensibili.

### ✨ Nuove Funzionalità

- **🎨 Chat Bubble Rendering Unificato**:
  - Sostituito pattern a 3 chiamate (st.markdown open + st.write + st.markdown close) con singola `st.markdown()`
  - Conversione Markdown→HTML via `markdown-it-py` (tabelle, code blocks, liste)
  - Colori professionali dark/light: dark come default, light via `@media (prefers-color-scheme: light)`
  - Tipografia completa per elementi HTML dentro le bolle (p, strong, a, code, pre, table, ul/ol)

- **☁️ Cloud Models YAML** (`cloud_models.yaml`):
  - Configurazione modelli cloud senza modificare codice (pattern `remote_servers.yaml`)
  - 4 provider preconfigurati: OpenAI, Anthropic, Google Gemini, Custom
  - Ogni provider con lista modelli (id + nome), default_model, base_url
  - Opzione "✏️ Altro..." per modelli custom (configurabile `allow_custom_models`)
  - Fallback automatico a costanti hardcoded se YAML assente

- **🔒 Rilevamento Sensibilità Granulare**:
  - Icone specifiche per tipo: 📚 (KB Wiki), 📁 (Cartella locale), 📎 (File allegati)
  - Combinazioni: 📚📎, 📁📎, etc.
  - Prefisso 🔒 su cloud provider (es. 🔒📁📎)
  - Caption dettagliata sotto selectbox conversazioni
  - Euristica wiki/folder: `kb_folder_path` vuoto = wiki, non vuoto = cartella locale

- **⚠️ Warning Cambio Provider**:
  - Avviso quando si passa a Cloud con conversazione sensibile caricata
  - Copre gap: conversazioni caricate con attachments/sources non rilevate dal check v1.5.0
  - Non blocca il cambio (l'utente può iniziare nuova chat), solo warning informativo

### 🔧 Modifiche Tecniche

- `ui/chat.py`: Import `markdown_it`, creazione converter `_md`, singola `st.markdown()` per bolla
- `ui/styles.py`: CSS dark default + light override, tipografia HTML completa dentro bolle
- `cloud_models.yaml`: Nuovo file configurazione (opzionale)
- `config/settings.py`: +4 funzioni cloud models (`load_cloud_models_config`, `get_cloud_providers`, `get_cloud_provider_models`, `get_cloud_models_settings`)
- `ui/sidebar/llm_config.py`: Sezione Cloud riscritta (YAML-first + fallback), parametri in `st.expander`, warning sensibilità v1.9.1
- `core/persistence.py`: `conversation_has_sensitive_content()` con `has_wiki`, `has_folder`, reason granulari
- `ui/sidebar/conversations.py`: `_get_conversation_icon()` helper, selectbox con icone, blocco cloud con dettaglio

### 📁 Nuovi File

```
cloud_models.yaml    # Configurazione modelli cloud (opzionale)
```

### 📝 Note

- **Parametri collassabili**: System Prompt, Temperature, Max messaggi ora in expander chiuso
- **3 livelli protezione privacy**: Dialog (docs sessione) → Warning (conversazione caricata) → Hard block (KB attiva)
- `markdown-it-py` è già dipendenza transitiva di Streamlit, nessun `pip install` aggiuntivo

---

## [1.9.0] - 2026-02-06

### 📋 Storia Esplorazioni Socratiche + Persistenza

Release che aggiunge il tracciamento completo delle esplorazioni socratiche con persistenza nelle conversazioni salvate.

### ✨ Nuove Funzionalità

- **📋 Storia Esplorazioni Socratiche** (sidebar widget):
  - Contatore totale esplorazioni della sessione
  - Breakdown per tipo di bottone (emoji + conteggio)
  - Lista ultime 10 esplorazioni con expander
  - Ogni esplorazione mostra: domanda originale + risultato socratico
  - Cancellazione storico con checkbox di conferma
  - Visibile solo in modalità Standard e Socratico

- **💾 Persistenza Esplorazioni**:
  - Le esplorazioni socratiche vengono salvate nel JSON della conversazione
  - Al caricamento di una conversazione, esplorazioni ripristinate
  - Auto-save dopo ogni esplorazione (dirty flag pattern)
  - Retrocompatibile: conversazioni senza socratic_history funzionano normalmente

- **🔄 Sync Cache UI**:
  - Al caricamento conversazione: pulizia cache vecchia + ricostruzione cache expander
  - Gli expander socratici si ripristinano correttamente dopo reload

### 📁 Nuovi File

```
ui/socratic/
├── history.py         # SocraticExploration dataclass + SocraticHistory class
└── history_widget.py  # Widget sidebar storico esplorazioni
```

### 🔧 Modifiche Tecniche

- `ui/socratic/history.py`: Dataclass `SocraticExploration` (7 campi), classe `SocraticHistory` (8 metodi statici)
- `ui/socratic/history_widget.py`: `render_socratic_history_sidebar()` con conteggi, breakdown, expander, cancellazione
- `ui/socratic/buttons.py`: +3 helper (`_get_last_user_question`, `_get_session_id`, `_record_exploration`), registrazione in tutti i 5 `generate_*`, dirty flag
- `ui/socratic/__init__.py`: +4 export (SocraticExploration, SocraticHistory, HISTORY_KEY, render_socratic_history_sidebar)
- `core/persistence.py`: +parametro `socratic_history` in `save_conversation()`
- `app.py`: Import SocraticHistory, auto-save socratico, clear su reset, widget sidebar
- `ui/sidebar/conversations.py`: Import + `clear_socratic_cache()` + `load_from_data()` su caricamento

### 📝 Note

- **Privacy-first**: tutti i dati restano in session_state + file locale JSON
- Il widget è nascosto in modalità "Veloce" (fast)
- `msg_index` nell'esplorazione permette ricostruzione esatta della cache UI

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
