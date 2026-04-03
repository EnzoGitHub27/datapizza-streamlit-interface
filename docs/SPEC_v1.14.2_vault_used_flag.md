# SPEC — v1.14.2: vault_used flag + icona 🧠 nel selettore conversazioni

## Contesto
**Repository:** `EnzoGitHub27/datapizza-streamlit-interface`
**Branch di partenza:** `dev`
**Versione corrente:** `v1.14.1`
**Versione target:** `v1.14.2`
**Feature pendente da:** note v1.13.x — mai implementata

---

## Obiettivo

Quando una conversazione è stata condotta con un vault attivo (Obsidian, LogSeq o
Notion), il selettore conversazioni in sidebar deve mostrare l'icona 🧠 accanto al
titolo, in modo che l'utente riconosca a colpo d'occhio quali chat hanno usato
conoscenza da vault.

---

## Comportamento atteso

### Nel selettore conversazioni (sidebar)
```
🧠 Analisi strategia commerciale 2024     ← vault usato
   Brainstorming naming prodotto          ← nessun vault
🧠 📚⭐ Review contratto Ferrari          ← vault + KB chat rilevanza media
   📚 Note onboarding nuovo fornitore     ← solo KB chat
```

Le icone esistenti (📚 / 📚⭐ / 📚⭐⭐) per la KB Chat rimangono invariate.
🧠 si aggiunge a sinistra, prima di eventuali icone KB Chat.

---

## Implementazione

### 1. Schema JSON conversazione — `core/persistence.py`

Aggiungere `vault_used` al metadata della conversazione.

**Struttura JSON attuale (semplificata):**
```json
{
  "id": "...",
  "title": "...",
  "messages": [...],
  "kb_metadata": { ... }
}
```

**Struttura target:**
```json
{
  "id": "...",
  "title": "...",
  "messages": [...],
  "vault_used": true,
  "kb_metadata": { ... }
}
```

- Default: `false` (retrocompatibilità completa con chat pre-v1.14.2)
- Tipo: `bool`
- Getter da aggiungere: `get_vault_used(conversation: dict) -> bool`
  con fallback sicuro `return conversation.get("vault_used", False)`

### 2. Impostazione del flag — `app.py`

Il flag `vault_used` deve essere impostato a `True` quando:
- Un vault è attivo al momento dell'invio del messaggio (cioè `st.session_state`
  contiene un vault caricato e il RAG vault è abilitato)
- E viene inviato almeno un messaggio in quella sessione

**Logica suggerita in `app.py` (dentro la funzione di invio messaggio):**
```python
# Dopo add_message(), prima o dopo il salvataggio
if vault_is_active():  # funzione/condizione già esistente nel codebase
    current_conversation["vault_used"] = True
```

> ⚠️ Non sovrascrivere `True` con `False` se il vault viene disattivato
> a metà conversazione — una volta impostato a True rimane True.

### 3. Visualizzazione icona — `ui/sidebar/conversations.py`

Nella funzione che costruisce il label del selettore conversazioni, aggiungere
la logica per prepend dell'icona 🧠:

```python
def build_conversation_label(conv: dict) -> str:
    label = conv.get("title", "Conversazione senza titolo")
    
    # Icone KB Chat (logica esistente)
    kb_meta = get_kb_metadata(conv)
    if kb_meta.get("includi_in_kb"):
        rilevanza = kb_meta.get("rilevanza", 1)
        if rilevanza == 3:
            label = "📚⭐⭐ " + label
        elif rilevanza == 2:
            label = "📚⭐ " + label
        else:
            label = "📚 " + label
    
    # Icona vault (NUOVA)
    if get_vault_used(conv):
        label = "🧠 " + label
    
    return label
```

> Verificare l'ordine effettivo delle icone nel codice esistente e adattare
> di conseguenza — l'importante è che 🧠 sia sempre a sinistra.

---

## File da toccare

| File | Modifica |
|------|----------|
| `core/persistence.py` | Aggiungere `get_vault_used()` con fallback |
| `app.py` | Impostare `vault_used = True` quando vault attivo + messaggio inviato |
| `ui/sidebar/conversations.py` | Aggiungere icona 🧠 nel label builder |
| `config/constants.py` | Bump `VERSION = "1.14.2"` |
| `README.md` | Aggiornare badge versione + tabella changelog |
| `CHANGELOG.md` | Nuova sezione v1.14.2 |
| `ROADMAP.md` | Aggiornare riga versione corrente |

---

## Test da aggiungere

Aggiungere casi in `tests/test_kb_chat_indexer.py` o in un nuovo
`tests/test_persistence.py`:

```python
def test_get_vault_used_default_false():
    """Chat pre-v1.14.2 senza campo vault_used → False"""
    conv = {"id": "x", "title": "test", "messages": []}
    assert get_vault_used(conv) == False

def test_get_vault_used_true():
    conv = {"id": "x", "vault_used": True, "messages": []}
    assert get_vault_used(conv) == True

def test_get_vault_used_false_explicit():
    conv = {"id": "x", "vault_used": False, "messages": []}
    assert get_vault_used(conv) == False
```

---

## Workflow Git

```bash
git checkout dev
git checkout -b feature/vault-used-icon
# ... implementazione con Claude Code Max ...
git add .
git commit -m "feat: vault_used flag + icona 🧠 nel selettore conversazioni"
git checkout dev
git merge feature/vault-used-icon --no-ff -m "merge: vault_used flag (#v1.14.2)"
git checkout main
git merge dev --no-ff -m "merge: dev → main (v1.14.2)"
git tag -a v1.14.2 -m "v1.14.2 — vault_used flag + icona 🧠 nel selettore"
git push origin main --tags
git push origin dev
git checkout dev
```

---

## Criteri di accettazione

- [ ] Chat condotte con vault attivo mostrano 🧠 nel selettore
- [ ] Chat senza vault non mostrano 🧠
- [ ] Chat pre-v1.14.2 caricate da disco non crashano (retrocompat)
- [ ] 🧠 e 📚 coesistono correttamente nella stessa chat
- [ ] Il flag `vault_used` persiste correttamente nel JSON su disco
- [ ] Test verdi
- [ ] Versione bumped a 1.14.2 in tutti i file richiesti

---

*Spec preparata il 1 Aprile 2026*
*DeepAiUG Interface — open source · locale · privacy-first*
