# Knowledge Base dalle Chat Salvate

A partire dalla versione 1.14.0, puoi trasformare le tue conversazioni salvate in una
**fonte di conoscenza riutilizzabile** dal sistema. Le chat che contengono decisioni
importanti, insight strategici o memoria aziendale possono essere incluse nella
Knowledge Base (KB) e verranno consultate automaticamente nelle conversazioni future.

---

## Come flaggare una chat per la KB

1. Nella **sidebar**, apri la sezione **"Includi nella Knowledge Base"** (icona a libro)
2. Spunta la checkbox **"Includi questa chat nella Knowledge Base"**
3. Compila i campi opzionali:
   - **Rilevanza**: Bassa, Media o Alta (determina quanto peso dare a questa chat
     quando il sistema cerca informazioni)
   - **Tipo**: seleziona una o piu categorie tra *decisione*, *insight*,
     *memoria aziendale*, *riferimento*, *sperimentale*
   - **Note**: un breve appunto libero per ricordarti perche questa chat e importante
4. La chat viene salvata automaticamente con questi metadati

Le chat non flaggate non vengono mai incluse nella KB. Nessuna chat entra
automaticamente: la scelta e sempre tua.

---

## Il pannello Gestione Knowledge Base

Nella sidebar trovi la sezione espandibile **"Gestione Knowledge Base"**.
Qui puoi vedere tutte le chat attualmente incluse nella KB, con:

- Data e modello usato
- Rilevanza (stelle)
- Tipo (etichette)
- Note (troncate)
- Numero di "chunk" indicizzati (i frammenti in cui la chat e stata suddivisa)

### Modificare i metadati

Clicca **"Modifica"** accanto a una chat per cambiare rilevanza, tipo o note.
Dopo il salvataggio, la chat viene ri-indicizzata automaticamente con i nuovi
parametri.

### Rimuovere una chat dalla KB

Clicca **"Rimuovi"** per togliere una chat dalla KB. La chat stessa
**non viene eliminata**: resta tra le conversazioni salvate, semplicemente
non verra piu consultata dal sistema.

---

## Attivare il retrieval dalla KB Chat

1. Nella sidebar, nella sezione conversazioni, attiva il toggle **"Usa KB Chat"**
2. Quando fai una domanda, il sistema cerchera anche tra le chat flaggate
3. I risultati piu rilevanti vengono inclusi nel contesto della risposta,
   con peso maggiore per le chat a rilevanza alta

### Filtrare per tipo

Sotto il toggle "Usa KB Chat" trovi un selettore **"Filtra per tipo"**.
Se selezioni uno o piu tipi (ad esempio solo "decisione"), il sistema
cerchera solo tra le chat di quel tipo. Se lasci vuoto, cerca in tutte.

---

## Cosa significano rilevanza e tipo

### Rilevanza

| Livello | Icona | Significato |
|---|---|---|
| Bassa | ⭐ | Informazione utile ma non critica |
| Media | ⭐⭐ | Insight o decisione di medio peso |
| Alta | ⭐⭐⭐ | Decisione strategica, memoria aziendale importante |

La rilevanza influenza l'ordine dei risultati: a parita di pertinenza,
le chat con rilevanza alta vengono mostrate prima.

### Tipo

| Tipo | Quando usarlo |
|---|---|
| decisione | La chat contiene una scelta architetturale o strategica |
| insight | Un'osservazione o scoperta significativa |
| memoria_aziendale | Informazioni su processi, persone, contesti aziendali |
| riferimento | Link, riferimenti bibliografici, risorse esterne |
| sperimentale | Esperimenti, prove, tentativi da documentare |

Puoi assegnare piu tipi alla stessa chat.

---

## Indicizzazione manuale

Il pulsante **"Aggiorna KB Chat"** nella sidebar riesegue l'indicizzazione
di tutte le chat flaggate. Usalo dopo aver modificato molte chat o
se noti che i risultati non sono aggiornati.

---

## Privacy

- Tutte le chat restano **locali** sul tuo computer
- La KB Chat usa lo stesso database locale (ChromaDB) gia usato per i wiki
- **Nessuna sincronizzazione cloud** dei dati della KB
- Se una chat e marcata come sensibile (contiene file locali, vault, ecc.)
  il sistema ti avvisera prima di includerla nella KB

---

*Documentazione DeepAiUG v1.14.0*
