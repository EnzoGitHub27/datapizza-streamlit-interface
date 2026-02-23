# F2 — Mappa Sessione
## Specifica Completa — DeepAiUG v1.10.0

**Stato:** 📝 In progettazione  
**Versione target:** v1.10.0  
**Data specifica:** 2026-02-23  
**Moduli HSCI coperti:** M2 (Gestione ambiguità), M8 (Pianificazione controllata)  
**Dipende da:** F1 (Storico esplorazioni — già in produzione con v1.9.0)

---

## 1. Perché esiste F2 — Il problema che risolve

### 1.1 Il problema della singola risposta (già risolto)

I 5 bottoni socratici (v1.8.0 → v1.9.2) affrontano il problema della **singola risposta**:
ogni risposta dell'AI può essere analizzata, confutata, messa alla prova.
Questo indirizza il "vincolo teleologico" descritto da Carmelo Quartarone:
impedire che una risposta localmente corretta perda di vista il fine reale.

### 1.2 Il problema dell'accumulo nel tempo (non ancora risolto)

C'è un secondo problema, più sottile e più pericoloso, descritto da Cinzia Ligas:
il **sovrascopo**.

> "Governare l'AI non significa solo ottimizzare lo scopo, ma vigilare sul sovrascopo:
> la direzione simbolica in cui, risposta dopo risposta, viene condotta la nostra semiosfera."
> — Cinzia Ligas, *AI Semiology*

Il sovrascopo non si manifesta nella singola risposta sbagliata.
Si manifesta nel fatto che **ogni risposta costruisce una cornice interpretativa**
che orienta le domande successive — spesso senza che l'utente se ne accorga.

### 1.3 Un esempio concreto

Una PMI usa DeepAiUG per decidere se adottare un nuovo software gestionale.
Fa queste domande in sequenza:

1. "Quali sono i migliori software gestionali per PMI italiane?"
2. "Quanto costa mediamente l'implementazione?"
3. "Quali sono i rischi principali?"
4. "Conviene fare tutto in cloud o tenere qualcosa on-premise?"

Le 4 risposte sembrano indipendenti. Ma in realtà la risposta alla domanda 1
ha presupposto implicitamente che la PMI voglia una soluzione SaaS.
Da quel momento tutte le domande successive si sono mosse dentro quel frame —
**senza che nessuno lo abbia scelto consapevolmente**.

Il problema non è che le risposte siano sbagliate. È che la cornice è invisibile.

### 1.4 Cosa fa F2

F2 — Mappa Sessione — rende visibile la cornice invisibile.

Non giudica le scelte fatte. Non dice "stai sbagliando".
Restituisce attrito: mostra **da dove l'utente sta guardando il problema**,
così può decidere consapevolmente se continuare a guardare da lì
o esplorare prospettive diverse.

---

## 2. Cosa mostra la Mappa Sessione

La mappa mostra tre elementi:

### 2.1 Frame dominante
Una frase che descrive la cornice interpretativa implicita emersa durante la sessione.

Esempio:
```
Frame dominante: "Sto scegliendo tra soluzioni SaaS esistenti per ottimizzare i costi"
```

### 2.2 Connessione domande → frame
Come ogni domanda ha contribuito a costruire o rinforzare la cornice.

Esempio:
```
1. "Quali software gestionali?" → ha stabilito SaaS come default implicito
2. "Quanto costa?"             → ha rinforzato il criterio costo come principale
3. "Quali rischi?"             → ha circoscritto i rischi al piano tecnico
4. "Cloud o on-premise?"       → già dentro il frame SaaS, lo ha rinforzato
```

### 2.3 Frame non esplorati
Prospettive alternative che la sessione non ha percorso —
non risposte, solo domande che aprono corridoi diversi.

Esempio:
```
⚠️ Frame non esplorati:
→ "Potrei costruire qualcosa di custom invece di adottare?"
→ "Il problema è davvero il software o il processo che lo usa?"
→ "Chi decide in azienda e con quali criteri reali?"
```

---

## 3. Come viene costruita la mappa — La scelta filosofica chiave

### 3.1 NON automatica
La mappa **non si costruisce in background** analizzando silenziosamente
ogni domanda dell'utente senza che lui lo sappia.

Un'AI che analizza il pensiero dell'utente in modo invisibile
e gli dice "stai ragionando così" toglie attrito invece di restituirlo.
È il "reale impoverito" descritto da Cinzia Ligas.
Contraddice la filosofia fondamentale di DeepAiUG.

### 3.2 SU RICHIESTA dell'utente
La mappa viene costruita dall'AI **solo quando l'utente la richiede**
— premendo il bottone o scegliendo la modalità progressiva
sapendo esplicitamente cosa fa.

Anche quando l'AI costruisce la mappa, lo fa su delega consapevole dell'utente.
Come dice Carmelo Quartarone:
> "La delega è possibile solo quando il dominio è stabile e circoscritto."

Analizzare le domande di una sessione per estrarne il frame
è un dominio sufficientemente circoscritto da poter essere delegato.
Ma il **momento** della delega deve restare in mano all'umano.

### 3.3 Il gesto metacognitivo
Il semplice atto di premere "Mostra mappa sessione" è già
un atto metacognitivo: l'utente sta dicendo
*"voglio capire da dove sto guardando questo problema."*
Questo attrito è intenzionale e prezioso.

---

## 4. Modalità di visualizzazione — Configurabile dall'utente

L'utente può scegliere tra tre modalità, coerente con il toggle
modalità socratica già presente in sidebar:

### Modalità C — 🔄 Progressiva (default consigliato)
La mappa si aggiorna nella sidebar dopo ogni risposta,
ma diventa visibile e prominente solo dopo N domande (default: 4).
L'utente vede la cornice formarsi mentre lavora —
in tempo utile per cambiare direzione durante la sessione.

### Modalità B — 🔔 A soglia
La mappa non appare durante la sessione.
Dopo N domande (default: 5) appare in sidebar un nudge:
```
💡 Hai fatto 5 domande in questa sessione.
Sai da dove stai guardando il problema?
[📊 Mostra mappa sessione]
```
L'utente preme il bottone solo se e quando lo ritiene utile.

### Modalità off — ⏹️ Disattivata
Nessuna mappa, nessun nudge. Per chi preferisce lavorare
senza questa funzionalità attiva.

### Impostazione in sidebar
```
📊 Mappa sessione
○ 🔄 Progressiva
● 🔔 A soglia     ← default
○ ⏹️ Disattivata
```

---

## 5. Il Nudge — "Sai da dove stai guardando?"

Il messaggio di invito appare in sidebar dopo N domande (configurabile, default 5).

**Testo del nudge:**
```
💡 Hai fatto 5 domande in questa sessione.
Sai da dove stai guardando il problema?
[📊 Mostra mappa sessione]
```

**Principi del nudge:**
- Breve — non interrompe il flusso di lavoro
- Non giudicante — non dice "stai sbagliando" o "hai un bias"
- Fa una domanda — come i bottoni socratici, non dà risposte
- Lascia libero l'utente — può ignorarlo senza conseguenze
- Appare una sola volta per sessione — non ripetuto

---

## 6. Il Tooltip "?" — Spiegazione in-app

Accanto al titolo "Mappa Sessione" in sidebar appare un'icona "?".
Cliccando si apre un expander con la spiegazione:

```
📊 Cos'è la Mappa Sessione?

Ogni volta che fai una domanda all'AI, non stai solo cercando
una risposta. Stai anche costruendo, senza accorgertene, una
cornice invisibile che orienta le domande successive.

La Mappa Sessione rende visibile questa cornice:
• Qual è il frame implicito che stai usando?
• Come le tue domande lo hanno costruito?
• Quali corridoi non hai ancora esplorato?

Non giudica le tue scelte. Ti restituisce attrito:
ti aiuta a capire da dove stai guardando il problema,
così puoi decidere consapevolmente se continuare
a guardare da lì o cambiare prospettiva.

─────────────────────────────────────
Ispirato a:
• "Sovrascopo" — Cinzia Ligas, AI Semiology (2026)
• "Vincolo teleologico" — Carmelo Quartarone,
  Il Teleology Gate (2026)
• "Capitale semantico" — Luciano Floridi
─────────────────────────────────────
📖 Approfondisci → PHILOSOPHY.md
```

---

## 7. Architettura tecnica — File coinvolti

### Nuovi file
```
ui/socratic/
└── session_map.py        # Logica mappa: prompt, estrazione frame,
                          # rilevamento frame non esplorati,
                          # nudge timer

ui/sidebar/
└── session_map_widget.py # Widget sidebar: visualizzazione mappa,
                          # toggle modalità, nudge, tooltip
```

### File modificati
```
config/constants.py       # SESSION_MAP_MODES, SESSION_MAP_DEFAULTS
                          # (soglia nudge, modalità default)
ui/socratic/__init__.py   # Export nuovi moduli
app.py                    # Integrazione session_map nel flusso principale
ui/sidebar/               # Aggiunta widget mappa in sidebar
```

### Prompt interno per costruzione mappa
Il prompt che F2 invia all'AI quando l'utente richiede la mappa:

```
Analizza le seguenti domande fatte dall'utente in questa sessione
e produci una Mappa Sessione strutturata.

DOMANDE DELLA SESSIONE:
{lista_domande}

Produci esattamente:

1. FRAME DOMINANTE (1 frase)
   La cornice interpretativa implicita che emerge dall'insieme
   delle domande. Cosa sta presupponendo l'utente senza saperlo?

2. CONNESSIONE DOMANDE → FRAME
   Per ogni domanda, una riga che spiega come ha contribuito
   a costruire o rinforzare il frame.

3. FRAME NON ESPLORATI (2-3 voci)
   Prospettive alternative che la sessione non ha percorso.
   Non risposte: solo domande che aprirebbero corridoi diversi.

NON giudicare le scelte dell'utente.
NON dare consigli o raccomandazioni.
Restituisci solo la struttura richiesta, in modo chiaro e conciso.
```

---

## 8. Integrazione con l'architettura esistente

F2 si integra naturalmente con quanto già costruito:

| Componente esistente | Come si integra con F2 |
|---|---|
| Storico socratico (v1.9.0) | F2 legge le domande dal medesimo storico |
| Toggle modalità sidebar | F2 aggiunge la propria impostazione nello stesso pattern |
| Privacy icons (v1.9.1) | F2 non invia domande al cloud se conversazione è 🔒 |
| Persistenza (v1.9.0) | La mappa può essere salvata con la conversazione |

---

## 9. Connessione ai moduli HSCI

| Modulo HSCI | Come F2 lo implementa |
|---|---|
| M2 — Gestione ambiguità | Rende visibili i frame impliciti invece di nasconderli |
| M8 — Pianificazione controllata | La mappa della sessione è la "pianificazione" resa visibile |
| M1 — Teoria della mente operativa | L'utente vede come l'AI ha "letto" il suo percorso cognitivo |

---

## 10. Posizionamento comunicativo

> "Non ti diciamo come stai ragionando.
> Ti mostriamo da dove stai guardando —
> così puoi scegliere se continuare a guardare da lì."

> "I bottoni socratici restituiscono attrito sulla risposta.
> La Mappa Sessione restituisce attrito sul pensiero."

> "Non è un'analisi automatica del tuo ragionamento.
> È uno specchio che accendi tu, quando sei pronto a guardare."

---

## 11. Checklist implementazione (per Claude Code Max)

- [ ] Leggere constants.py → aggiungere SESSION_MAP_MODES e defaults
- [ ] Creare ui/socratic/session_map.py (logica e prompt)
- [ ] Creare ui/sidebar/session_map_widget.py (widget UI)
- [ ] Modificare ui/socratic/__init__.py (export)
- [ ] Modificare app.py (integrazione flusso)
- [ ] Test: modalità progressiva
- [ ] Test: modalità a soglia + nudge
- [ ] Test: tooltip "?"
- [ ] Test: privacy (non inviare a cloud se 🔒)
- [ ] Aggiornare CHANGELOG, README, ROADMAP
- [ ] Bump versione → v1.10.0

---

*Specifica creata: 2026-02-23*
*Basata su: sessione di progettazione con Claude (Anthropic)*
*Framework teorico: Carmelo Quartarone, Cinzia Ligas, Luciano Floridi, Umberto Eco*
