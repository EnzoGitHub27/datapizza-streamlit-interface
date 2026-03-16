# Knowledge Base dalle Chat Salvate

A partire dalla versione 1.14.0, puoi trasformare le tue conversazioni salvate in una
**fonte di conoscenza riutilizzabile** dal sistema. Le chat che contengono decisioni
importanti, insight strategici o memoria aziendale possono essere incluse nella
Knowledge Base (KB) e verranno consultate automaticamente nelle conversazioni future.

---

## Il flusso in quattro passi

```
1. FLAGGA  →  2. SALVA  →  3. INDICIZZA  →  4. USA
```

Questo ordine è importante: se salti il passo 2 (salvataggio), il passo 3
(indicizzazione) non troverà nulla da elaborare.

---

## Passo 1 — Flagga una chat per la KB

Nella **sidebar**, nella sezione **"Conversazione"**, trovi l'expander
**"📚 Includi nella Knowledge Base"**.

1. Apri l'expander
2. Spunta la checkbox **"Includi questa chat nella Knowledge Base"**
3. Compila i campi opzionali:
   - **Rilevanza**: Bassa, Media o Alta (determina il peso nel retrieval)
   - **Tipo**: una o più categorie tra *decisione*, *insight*,
     *memoria_aziendale*, *riferimento*, *sperimentale*
   - **Note**: appunto libero sul perché questa chat è importante

> ⚠️ **Importante**: se dopo aver flaggato non hai ancora salvato la conversazione,
> il sistema mostra un avviso giallo prima del pulsante "Aggiorna KB Chat".
> In quel caso salva prima di procedere.

Nessuna chat entra automaticamente nella KB: la scelta è sempre tua.

---

## Passo 1b — Flaggare le chat già salvate (bulk)

Se hai chat salvate prima della v1.14.0, puoi includerle nella KB senza
aprirle una per una.

Nella sidebar, apri **"📚 Gestione Knowledge Base"** → sezione
**"Flagga chat esistenti"**:

1. Leggi il messaggio informativo che indica quante chat non sono ancora in KB
2. Seleziona le chat che vuoi includere tramite le checkbox
3. Scegli una **rilevanza di default** applicata a tutte le selezionate
4. Clicca **"➕ Aggiungi alla KB (N)"**
5. Il sistema aggiorna i metadati su disco e ti suggerisce di cliccare
   "Aggiorna KB Chat" per indicizzarle

---

## Passo 2 — Salva la conversazione

Usa il normale pulsante di salvataggio nella sezione **"💬 Conversazione"**.
Solo dopo il salvataggio i metadati KB vengono scritti su disco e
l'indicizzatore può trovarli.

---

## Passo 3 — Indicizza

Clicca il pulsante **"🔄 Aggiorna KB Chat"** nella sidebar.

Il sistema:
- Legge tutte le chat con `includi_in_kb: true`
- Le suddivide in frammenti (chunk)
- Le inserisce nel database vettoriale locale (ChromaDB, collection separata)
- Applica il peso di rilevanza a ciascun frammento

Al termine viene mostrato il conteggio: *"Indicizzate N chat, M chunk totali"*
e la data dell'ultima indicizzazione.

Esegui "Aggiorna KB Chat" ogni volta che:
- Hai flaggato nuove chat
- Hai modificato i metadati di chat già in KB
- Hai aggiunto chat tramite il bulk-flag

---

## Passo 4 — Usa la KB Chat nel retrieval

1. Attiva il toggle **"✅ Usa KB Chat"** nella sidebar
2. (Opzionale) Usa il selettore **"Filtra per tipo"** per cercare solo
   tra le chat di un certo tipo — se vuoto, cerca in tutte
3. Fai la tua domanda normalmente
4. Il sistema cercherà anche tra le chat indicizzate; i risultati
   provenienti dalla KB Chat sono contrassegnati con il prefisso 💬
   nelle fonti della risposta

---

## Il pannello Gestione Knowledge Base

Nella sidebar, l'expander **"📚 Gestione Knowledge Base"** mostra:

- Lista delle chat attualmente in KB con data, rilevanza (⭐), tipo, note, chunk
- Statistiche: chat indicizzate, chunk totali, data ultima indicizzazione
- **Modifica**: cambia rilevanza, tipo o note di una chat — ri-indicizzazione
  automatica dopo il salvataggio
- **Rimuovi**: toglie la chat dalla KB senza eliminarla dalle conversazioni
  salvate
- **Flagga chat esistenti**: sezione bulk per le chat pre-v1.14.0

---

## Cosa significano rilevanza e tipo

### Rilevanza

| Livello | Icona | Significato | Boost retrieval |
|---|---|---|---|
| Bassa | 📚 | Informazione utile ma non critica | ×1.0 |
| Media | 📚⭐ | Insight o decisione di medio peso | ×1.15 |
| Alta | 📚⭐⭐ | Decisione strategica, memoria aziendale importante | ×1.30 |

A parità di pertinenza tematica, le chat con rilevanza alta vengono
preferite nel retrieval.

### Tipo

| Tipo | Quando usarlo |
|---|---|
| `decisione` | Scelta architetturale, strategica o operativa |
| `insight` | Osservazione o scoperta significativa |
| `memoria_aziendale` | Informazioni su processi, persone, contesti aziendali |
| `riferimento` | Risorse esterne, link, fonti bibliografiche |
| `sperimentale` | Esperimenti e prove da documentare |

Puoi assegnare più tipi alla stessa chat.

---

## Icone nel selettore chat

Le chat incluse nella KB mostrano un'icona accanto al titolo:

| Icona | Significato |
|---|---|
| 📚 | In KB — rilevanza bassa |
| 📚⭐ | In KB — rilevanza media |
| 📚⭐⭐ | In KB — rilevanza alta |

---

## Privacy

- Tutte le chat restano **locali** sul tuo computer
- La KB Chat usa un database ChromaDB separato (`knowledge_base/chat_kb_vectorstore/`)
- **Nessuna sincronizzazione cloud** — i dati non escono mai dalla tua macchina
- Le chat con file allegati o vault attivo mostrano un avviso prima
  dell'inclusione in KB

---

*Documentazione DeepAiUG v1.14.1 — aggiornato 2026-03-16*
