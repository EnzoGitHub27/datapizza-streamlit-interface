# SPEC — DeepAiUG Interface v1.14.x
## Feature: Chat Salvate come Knowledge Base Epistemica

---

## 1. Motivazione filosofica

Le chat salvate non sono semplice archivio: sono **memoria epistemica sedimentata**. Alcune conversazioni contengono decisioni architetturali, insight strategici, memoria aziendale implicita. Renderle disponibili come sorgente RAG significa trasformare il sistema da strumento reattivo a strumento dotato di continuità cognitiva — coerente con il framework Floridi/Eco/Quartarone/Ligas su cui è fondato il progetto.

Non tutte le chat hanno lo stesso peso. Occorre un meccanismo di **valutazione esplicita** affidata all'utente, integrata al momento del salvataggio o in un secondo momento, che il sistema rispetti in fase di retrieval.

---

## 2. Schema metadati proposto

Ogni chat salvata acquisisce un campo `kb_metadata` opzionale nel proprio JSON:

```json
{
  "id": "...",
  "titolo": "...",
  "data": "...",
  "vault_used": null,
  "kb_metadata": {
    "includi_in_kb": false,
    "rilevanza": 1,
    "tipo": [],
    "note": ""
  },
  "messaggi": [...]
}
```

### Campi

| Campo | Tipo | Valori | Default |
|---|---|---|---|
| `includi_in_kb` | bool | true / false | false |
| `rilevanza` | int | 1 = bassa, 2 = media, 3 = alta | 1 |
| `tipo` | list[str] | `decisione`, `insight`, `memoria_aziendale`, `riferimento`, `sperimentale` | [] |
| `note` | str | testo libero dell'utente | "" |

La scelta di default `includi_in_kb: false` è deliberata: nessuna chat entra nella KB senza scelta esplicita dell'utente (privacy-first).

---

## 3. Modifiche UI

### 3.1 — Al salvataggio della chat

Nel dialog di salvataggio aggiungere una sezione opzionale "Includi nella Knowledge Base":

```
[ ] Includi questa chat nella Knowledge Base
    Rilevanza: ○ Bassa  ● Media  ○ Alta
    Tipo: [decisione] [insight] [memoria_aziendale] [riferimento] [sperimentale]
    Note: ___________________________________________
```

La sezione è collassata di default per non appesantire il flusso normale.

### 3.2 — Nel selettore delle chat salvate

Aggiungere un'icona indicatore accanto alle chat già flaggate:

- `📚` = inclusa in KB (rilevanza bassa)
- `📚⭐` = inclusa in KB (rilevanza media)
- `📚⭐⭐` = inclusa in KB (rilevanza alta)

Tooltip al hover: mostra tipo/note dell'utente.

### 3.3 — Pannello di gestione KB (nuovo tab o sezione sidebar)

Vista tabellare delle chat incluse nella KB con possibilità di:
- Modificare metadati
- Rimuovere dalla KB (senza eliminare la chat)
- Vedere quante "chunk" ha generato ciascuna chat in ChromaDB

---

## 4. Modifiche al layer RAG

### 4.1 — Indicizzazione

Funzione `index_chat_to_kb(chat_json)`:

1. Legge `kb_metadata`
2. Se `includi_in_kb: False` → skip
3. Chunking del testo (messaggi utente + assistente, con separatore di turno)
4. Per ogni chunk, aggiunge a ChromaDB con metadati:

```python
{
    "source": "chat_salvata",
    "chat_id": chat["id"],
    "chat_titolo": chat["titolo"],
    "rilevanza": kb_metadata["rilevanza"],
    "tipo": ",".join(kb_metadata["tipo"]),
    "data": chat["data"]
}
```

### 4.2 — Retrieval con weighting

Al momento del retrieval dalla KB, applicare un **boost di score** proporzionale alla rilevanza:

```python
def adjust_score(base_score: float, rilevanza: int) -> float:
    boost = {1: 1.0, 2: 1.15, 3: 1.30}
    return base_score * boost.get(rilevanza, 1.0)
```

Opzionalmente, filtrare per `tipo` se l'utente attiva un filtro nel pannello KB.

### 4.3 — Trigger di re-indicizzazione

La re-indicizzazione della chat-KB avviene:
- Manualmente dal pannello di gestione KB ("Aggiorna KB")
- Automaticamente al cambio di `includi_in_kb` o `rilevanza` (se l'utente modifica i metadati)

Non si usa ChromaDB persistent per le chat in real-time: l'indicizzazione è batch/on-demand per mantenere le prestazioni.

---

## 5. Struttura file e compatibilità

### File JSON delle chat

Retrocompatibilità garantita: le chat esistenti senza `kb_metadata` vengono lette normalmente. Il campo viene aggiunto solo al salvataggio o alla prima modifica.

### Separazione delle collection ChromaDB

Usare una collection separata per le chat-KB:

```
collection: "deepaiug_chat_kb"   ← nuova, per le chat salvate
collection: "deepaiug_wiki"       ← esistente, per i wiki RAG
collection: "deepaiug_vault"      ← esistente, per Obsidian/LogSeq/Notion
```

Il retrieval finale può essere:
- Separato (l'utente sceglie quale sorgente attivare)
- Unificato con merge per rilevanza (default consigliato)

---

## 6. Interazione con feature esistenti

| Feature | Impatto |
|---|---|
| Vault icon (v1.13.x) | Nessuno — metadati ortogonali |
| Privacy lock | Le chat con privacy lock NON vengono proposte per la KB (check in UI) |
| F2 Mappa Sessione | Potrebbe in futuro visualizzare "fonti KB usate" — out of scope per ora |
| Export chat | Includere `kb_metadata` nel JSON esportato |

---

## 7. Considerazioni di privacy

- Le chat incluse nella KB **restano locali** come tutto il resto del sistema
- L'utente deve ricevere un avviso chiaro se tenta di includere in KB una chat con privacy lock: "Questa chat è marcata come privata. Sei sicuro di volerla includere nella Knowledge Base?"
- Nessuna sincronizzazione cloud dei metadati KB

---

## 8. Roadmap di implementazione suggerita

### Sprint 1 — Schema e salvataggio
- [ ] Aggiungere `kb_metadata` allo schema JSON delle chat
- [ ] Modificare il dialog di salvataggio con la sezione KB opzionale
- [ ] Retrocompatibilità lettura chat esistenti

### Sprint 2 — Indicizzazione RAG
- [ ] Funzione `index_chat_to_kb()`
- [ ] Collection ChromaDB separata `deepaiug_chat_kb`
- [ ] Boost score per rilevanza nel retrieval
- [ ] Trigger manuale "Aggiorna KB" nel pannello

### Sprint 3 — UI gestione KB
- [ ] Icone indicatore nel selettore chat
- [ ] Pannello/tab di gestione KB (modifica metadati, rimozione)
- [ ] Filtro per tipo nel retrieval (opzionale)

### Sprint 4 — Test e documentazione
- [ ] Test su chat di varie dimensioni
- [ ] Aggiornamento manuale utente
- [ ] Post LinkedIn su "memoria aziendale epistemica"

---

## 9. Versione target

`v1.14.0` — Sprint 1+2 (schema + indicizzazione base)
`v1.14.1` — Sprint 3 (UI gestione completa)
`v1.14.2` — Sprint 4 (rifinitura + documentazione)

---

*Spec prodotta in collaborazione con Claude — DeepAiUG Interface Project*
