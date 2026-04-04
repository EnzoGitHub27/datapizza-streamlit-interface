# SPEC — v1.14.3: Scroll fix + indicatore animato elaborazione

## Contesto
**Repository:** `EnzoGitHub27/datapizza-streamlit-interface`
**Branch di partenza:** `dev`
**Versione corrente:** `v1.14.2`
**Versione target:** `v1.14.3`
**Natura del rilascio:** UX fix — ultimo rilascio del ciclo v1.x prima di maintenance mode

---

## Obiettivo

Rendere l'esperienza conversazionale più familiare agli utenti già abituati a
Claude, ChatGPT e simili. Due interventi CSS/JS minimali, nessuna modifica
alla logica applicativa.

---

## Intervento 1 — Indicatore animato "sta elaborando"

### Comportamento atteso
Durante la generazione della risposta, al posto del generico spinner di
Streamlit, mostrare tre pallini animati (stile "typing indicator") posizionati
nell'area chat, allineati a sinistra come se fossero la risposta dell'AI in
arrivo.

### Aspetto visivo target
```
┌─────────────────────────────────────┐
│ 👤 Utente: La mia domanda...        │
│                                     │
│ 🤖  ● ● ●                          │  ← pallini animati, lato sinistro
└─────────────────────────────────────┘
```
I pallini devono avere un'animazione "pulse" o "bounce" sequenziale
(il classico indicatore di digitazione dei chatbot moderni).

### Implementazione suggerita

Creare una funzione `show_typing_indicator()` in `ui/chat.py` (o file style
esistente) che inietta HTML/CSS via `st.markdown()` con
`unsafe_allow_html=True`:

```python
def show_typing_indicator():
    st.markdown("""
    <style>
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 12px 16px;
        margin: 4px 0;
    }
    .typing-indicator span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #4A90D9;  /* adattare al colore tema DeepAiUG */
        display: inline-block;
        animation: typing-bounce 1.2s infinite ease-in-out;
    }
    .typing-indicator span:nth-child(1) { animation-delay: 0s; }
    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

    @keyframes typing-bounce {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
        30%            { transform: translateY(-6px); opacity: 1; }
    }
    </style>
    <div class="typing-indicator">
        <span></span><span></span><span></span>
    </div>
    """, unsafe_allow_html=True)
```

### Dove inserirla in app.py
```python
# Prima di avviare lo streaming della risposta LLM
with st.chat_message("assistant"):
    placeholder = st.empty()
    show_typing_indicator()   # ← mostra pallini
    # ... logica streaming esistente ...
    # Una volta completata la risposta, placeholder.markdown(risposta_completa)
    # I pallini spariscono automaticamente quando Streamlit ri-renderizza
```

> ⚠️ Verificare nel codice esistente come è strutturato il blocco
> `st.chat_message("assistant")` e adattare di conseguenza.
> L'obiettivo è che i pallini siano visibili SOLO durante lo streaming,
> non dopo che la risposta è completa.

---

## Intervento 2 — Scroll automatico durante lo streaming

### Comportamento atteso
Durante la generazione della risposta, la finestra della chat scorre
automaticamente verso il basso seguendo il testo che si forma, esattamente
come accade in Claude.ai e ChatGPT. L'utente non deve scrollare manualmente
per vedere la risposta in arrivo.

### Implementazione suggerita

Iniettare un componente JS minimale via `st.components.v1.html()` che
esegue lo scroll. Il punto chiave è che va eseguito *durante* lo streaming,
non solo alla fine.

```python
import streamlit.components.v1 as components

def inject_scroll_to_bottom():
    """
    Inietta JS che scrolla la finestra verso il basso.
    Da chiamare ad ogni chunk dello streaming.
    """
    components.html(
        """
        <script>
            // Cerca il container principale della chat di Streamlit
            const chatContainer = window.parent.document.querySelector(
                '[data-testid="stVerticalBlock"]'
            );
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            // Fallback: scrolla l'intera finestra
            window.parent.scrollTo(0, window.parent.document.body.scrollHeight);
        </script>
        """,
        height=0,  # componente invisibile
    )
```

> ⚠️ Il selettore CSS `[data-testid="stVerticalBlock"]` potrebbe variare
> tra versioni di Streamlit. Verificare con i DevTools del browser sulla
> versione installata nel progetto e adattare se necessario.
> Testare su Chrome e Firefox.

### Dove inserirla in app.py
```python
# Dentro il loop di streaming, ad ogni chunk ricevuto
for chunk in stream_response():
    risposta_accumulata += chunk
    placeholder.markdown(risposta_accumulata + "▌")  # cursore animato
    inject_scroll_to_bottom()                         # ← scroll ad ogni chunk
```

---

## Bonus — Cursore di scrittura animato

Aggiungere il classico cursore lampeggiante `▌` durante lo streaming
(già accennato sopra). È un dettaglio piccolo ma molto riconoscibile.

```python
# Durante streaming: testo + cursore
placeholder.markdown(risposta_accumulata + "▌")

# Dopo streaming: testo finale senza cursore
placeholder.markdown(risposta_completa)
```

Verificare se il cursore `▌` è già presente nel codebase — potrebbe
esserci già in qualche forma.

---

## File da toccare

| File | Modifica |
|------|----------|
| `ui/chat.py` (o equivalente) | Aggiungere `show_typing_indicator()` |
| `ui/styles.py` (o equivalente) | CSS animazione pallini (in alternativa inline) |
| `app.py` | Chiamate a `show_typing_indicator()` e `inject_scroll_to_bottom()` nel loop streaming |
| `config/constants.py` | Bump `VERSION = "1.14.3"` |
| `README.md` | Aggiornare badge versione + tabella changelog |
| `CHANGELOG.md` | Nuova sezione v1.14.3 |
| `ROADMAP.md` | Aggiornare riga versione corrente + nota maintenance mode |

---

## Note importanti per Claude Code Max

1. **Leggere prima il codice esistente** — in particolare come è strutturato
   il loop di streaming in `app.py` e dove sono gestiti i messaggi della chat.
   La logica di streaming potrebbe essere in `core/llm_client.py` o simile.

2. **Colori da adattare** — il `#4A90D9` nei pallini è un placeholder.
   Usare il colore accent del tema DeepAiUG già definito in `ui/styles.py`
   o `config/branding.py`.

3. **Non toccare la logica applicativa** — questo è un fix puramente UX.
   Zero modifiche a persistence, RAG, KB, Socratic buttons.

4. **Testare con streaming lento** — simulare una risposta lenta per
   verificare che scroll e pallini si comportino correttamente durante
   tutta la durata della generazione, non solo all'inizio.

5. **ROADMAP.md** — aggiungere una nota esplicita che v1.14.3 è l'ultimo
   rilascio del ciclo v1.x e che il progetto entra in maintenance mode.
   Questo è un momento editoriale importante, non solo tecnico.

---

## Workflow Git

```bash
git checkout dev
git checkout -b feature/ux-scroll-typing-indicator
# ... implementazione con Claude Code Max ...
git add .
git commit -m "feat: scroll automatico + typing indicator animato durante streaming"
git checkout dev
git merge feature/ux-scroll-typing-indicator --no-ff -m "merge: UX scroll fix (#v1.14.3)"
git checkout main
git merge dev --no-ff -m "merge: dev → main (v1.14.3) — ultimo rilascio ciclo v1.x"
git tag -a v1.14.3 -m "v1.14.3 — scroll fix + typing indicator | v1.x → maintenance mode"
git push origin main --tags
git push origin dev
git checkout dev
```

---

## Criteri di accettazione

- [ ] I tre pallini animati appaiono durante lo streaming e spariscono quando la risposta è completa
- [ ] La chat scrolla automaticamente verso il basso durante la generazione
- [ ] Il cursore `▌` è visibile durante lo streaming e scompare alla fine
- [ ] Nessuna regressione sulle feature esistenti (KB Chat, RAG, Socratic buttons, vault)
- [ ] Testato su Chrome e Firefox
- [ ] Versione bumped a 1.14.3 in tutti i file richiesti
- [ ] ROADMAP.md aggiornata con nota maintenance mode v1.x

---

## Nota editoriale — dopo il merge

Dopo il tag v1.14.3, aggiornare il BRAIN.md con:
- Versione corrente → v1.14.3
- Stato v1.x → maintenance mode (ufficiale)
- Aprire la sezione v2.0 come fase attiva

Questa è la fine di un capitolo e l'inizio del prossimo. 🤿

---

*Spec preparata il 4 Aprile 2026*
*DeepAiUG Interface — open source · locale · privacy-first*
*v1.14.3 è l'ultimo rilascio del ciclo v1.x*
