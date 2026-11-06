# Audit prima della v1.16.0 — manuale, SPEC, bug «[object Object]», passi, Graphify

**Data:** 2026-11-06 · **Ramo:** `feat/hybrid-pii-annona` · **Codice di riferimento:** v1.15.3 (`dev` 7acfba2) + i tre commit del giro 1
**Che cosa è:** solo analisi. In questo giro **non si cambia il codice dell'app**; ogni correzione qui è una proposta.

---

## 1. Il manuale contro il codice

Confronto fatto in sola lettura (06/11) fra `MANUALE_DeepAiUG.md` (854 righe), il codice della 1.15.3, `README.md` e `CHANGELOG.md`. Le righe sono quelle del manuale. Sono ordinate per gravità: prima ciò che fa sbagliare l'utente o dice il falso sulla privacy. Controllate a campione sul codice le voci 3, 4, 5 e 6, e la cancellazione in `core/persistence.py:219-236`. **Due punti vanno confermati provando l'app:** il riallegamento dei file dopo l'invio (voce 9) e Anthropic/Google su un'installazione fatta con l'installer (voce 4).

### 1.1 Gravità alta

1. **Cap. 20 «Privacy» §20.1/§20.3 e Cap. 1, righe 765, 779, 57.** Il manuale parla di «Blocco totale» e dice che le chat con dati locali «non possono essere caricate» sul cloud. In realtà il caricamento è bloccato solo se sei *già* su cloud. Se carichi la chat in Local/Remote, spegni la KB e poi passi al cloud, compare solo un avviso: «l'intera cronologia… verrà inviata al provider esterno. Non c'è alcun filtro» (`ui/sidebar/llm_config.py:69-93`). La conferma esplicita del §20.2 scatta solo per i file caricati in questa sessione (`llm_config.py:58`). → **Correzione:** «Se carichi una chat con fonti KB o allegati, ne disattivi la KB e poi passi al cloud, la cronologia (comprese le risposte ricavate da dati locali) viene inviata al provider. Compare solo un avviso: per restare privati apri una nuova conversazione.»
2. **Cap. 18 «Gestione delle conversazioni», riga 721.** «🗑️ Elimina cancella definitivamente la conversazione», ma cancella solo il JSON (`core/persistence.py:219-236`). I pezzi già indicizzati restano nella KB Chat (`knowledge_base/chat_kb_vectorstore/`). «🔄 Aggiorna KB Chat» non elimina le chat orfane (`core/kb_chat_indexer.py:418-476`), e la chat sparisce anche dal pannello «Gestione». → **Correzione:** «Prima di eliminare una chat inclusa nella KB Chat, usa 🗑️ Rimuovi in "📚 Gestione Knowledge Base"; altrimenti il suo contenuto resta recuperabile.» Va anche corretto il codice: passo P13 (§4).
3. **Cap. 13, Cap. 5 e App. A, righe 532, 210, 798.** «Massimo 10 MB per file», «limite applicativo reale… imposto dal codice». In realtà `MAX_FILE_SIZE_MB` compare solo nel testo d'aiuto (`ui/file_upload.py:222`) e non viene mai controllato. Il limite vero è quello di Streamlit, 200 MB. → **Correzione:** dire che 10 MB è un'indicazione, oppure implementare il controllo (passo P13).
4. **Cap. 2 §2.3, Cap. 1, Cap. 12 §12.3, righe 100, 62, 505.** Anthropic e Google sono presentati come pronti all'uso. Ma `create_client` usa `Provider.ANTHROPIC/GOOGLE`, che richiedono `datapizza-ai-clients-anthropic` e `-google`. Questi pacchetti non sono in `requirements.txt` né nel venv: la factory solleva `ImportError` (`datapizza/clients/factory.py:101-107`) e l'utente vede «❌ Errore: …». Il README li indica come installazione a parte (`README.md:447-448`). → **Correzione:** dirlo nel manuale, oppure aggiungerli ai requisiti (passo P13).
5. **App. B «Risoluzione dei problemi», riga 829** (contraddice il riquadro di riga 538). Dice «le immagini non raggiungono ancora il modello… Vision API non integrata», ma dalla 1.15.3 partono come `[TextBlock, MediaBlock…]` (`app.py:831-845`, ADR-0001). → **Riga corretta:** «Immagini ignorate → modello non-Vision (nome non riconosciuto) o connessione cloud → usare un modello vision locale (llava, moondream) su Local/Remote.»
6. **Intestazione, Cap. 1, piè di pagina, righe 8, 14, 71, 854.** Dichiara «v1.15.2», `VERSION = "1.15.2"` e la data 2026-07-13, mentre `config/constants.py:11` ha `VERSION = "1.15.3"` (CHANGELOG [1.15.3] del 2026-08-04). → aggiornare versione e data.
7. **Cap. 17 «Mappa Sessione», riga 692** (contraddice la riga 790). Dice «nessun invio aggiuntivo verso l'esterno», ma la mappa fa una chiamata in più al modello con tutte le domande della sessione: sul cloud va al fornitore (`app.py:455-509`), e in modalità Progressiva dopo *ogni* risposta (`app.py:889-897`). → **Correzione:** «È generata dal modello in uso: su cloud le domande della sessione vengono inviate di nuovo al provider; in Progressiva c'è una chiamata in più per ogni risposta.»

### 1.2 Gravità media

8. **Cap. 13 §13.1, riquadro Vision, riga 538.** «Funziona solo su Local e Remote, mai verso il cloud» è vero, ma con un Remote host su IP pubblico le immagini escono comunque, con il solo banner «⚠️ Host esterno» (`app.py:575-586`). → aggiungere la frase (vedi anche §2.1 e il passo P2).
9. **Cap. 13 §13.2, riga 547.** «🔄 Nuova azzera… allegati», ma il widget allegati non si svuota. È un bug noto (CHANGELOG [1.15.3], `README.md:58`): `chat_file_upload` non viene mai resettato (`ui/file_upload.py:216-234`, `app.py:651-658`, `883`). Da verificare se i file vengono riallegati. → avviso nel manuale, e correzione nel passo P13.
10. **Cap. 18 §18.1, riga 702.** Con Auto-save spento, un bottone socratico salva comunque la chat su disco (`app.py:638-639`, `ui/socratic/buttons.py:90`). → dirlo.
11. **Cap. 7 «Chiavi API», riga 359** (contraddice la riga 428). Dice che i file «possono nascere con permessi larghi (664)», ma `save_api_key_to_file` applica `0o600` (`config/settings.py:330`, M2). → «Dalla v1.15.2 le chiavi salvate dalla UI hanno permessi 0600.»
12. **Cap. 10 «Sicurezza», riga 428.** Dice che la v1.15.2 corregge H1–H4 e M1–M4, ma CHANGELOG [1.15.2] e `SECURITY_AUDIT_RESOLUTION.md` chiudono H1–H3, M1, M2 e M4. H4 è un rischio accettato. M3 (re-indicizzazione automatica del `folder_path` di una chat caricata, `ui/sidebar/conversations.py:281-300`) non risulta corretto. → correggere l'elenco.
13. **Cap. 12 §12.4, riga 517.** Con la KB attiva il prompt contiene solo il contesto KB e la domanda, senza cronologia (`app.py:804-817`): «Max messaggi» vale solo senza KB. → dirlo.
14. **Cap. 14 §14.2, riga 576.** «➕ Configura manualmente…» compare solo con `mode: "custom"` (`ui/sidebar/knowledge_base.py:141-142`), mentre il file fornito ha `selectable`. → precisare.
15. **Cap. 14 §14.3 e Cap. 9 §9.1, righe 585, 392.** C'è un'unica collection, e ogni indicizzazione la svuota (`rag/manager.py:108`): una sorgente sostituisce la precedente. `get_files_to_update` (`rag/vault.py:67`) non è mai chiamata. → «Una sola sorgente attiva alla volta; nessun aggiornamento incrementale.»
16. **Cap. 18 §18.2, riga 719.** Solo cartelle e vault vengono re-indicizzati al caricamento: per le wiki si usa l'indice persistito, che può essere di un'altra sorgente (`conversations.py:281-300`). → precisare.
17. **Cap. 2 §2.1 e Cap. 3–4, righe 85, 127-191.** Windows è citato solo in tabella, ma esistono `installer/INSTALLA_DeepAiUG.bat`, `AGGIORNA_DeepAiUG.bat` e `CHECK_DeepAiUG.bat` (`installer/INIZIA-QUI.txt`). → aggiungere un paragrafo su Windows.
18. **Cap. 2 §2.2, riga 91.** Poetry e `pyproject.toml` non sono un percorso completo: mancano chromadb, sentence-transformers, pypdf e altri, e i pin sono diversi (vedi la nota TODO dell'ADR-0001). → «Usare `requirements.txt`.»
19. **Cap. 6 §6.2 e Cap. 12 §12.3, righe 262, 505.** Per il cloud «Custom» la UI non ha un campo Base URL: vale il `base_url` di `cloud_models.yaml`, che nel file fornito è vuoto (`llm_config.py:413`). → precisare.
20. **Cap. 14 §14.1, riga 560.** Il testo reale è «🔒 Privacy reale - dati e chat restano nella tua rete», e c'è anche il caso dell'host esterno (`knowledge_base.py:77-92`). → aggiornare.

### 1.3 Gravità bassa

21. Riga 455: il titolo reale è «🧠 DeepAiUG Chat → Ollama `1.15.3`» (`app.py:542`).
22. Riga 231: l'esempio di `branding.yaml` mostra `# version: "1.15.2"`, ma il file ha `"1.12.0"` e il default viene da constants. → togliere il numero.
23. Riga 227: `subtitle` è importato ma mai mostrato (`app.py:38`). → «campo riservato».
24. Riga 219: `branding.yaml` si legge solo dalla radice, non da `config/`.
25. Riga 315: `type: local_folder` → nel codice è `local` (`wiki_sources.yaml:119`).
26. Righe 465, 555: l'ordine reale della sidebar è un altro (`app.py:318-516`): ⚙️ Configurazione (chiusa), 📚 Knowledge Base, 💬 Conversazione, KB Chat, 📊 Mappa, 🧠 Socratica, 📤 Export.
27. Riga 471: l'expander ⚙️ Configurazione è chiuso di default: «apri l'expander».
28. Righe 589-591: i testi reali sono «💾 Storage: ChromaDB (persistente)» e «🌍 Embedding: `multilingual-e5-small`»; c'è anche «⚠️ Embedding: legacy». Lo slider compare solo con la KB indicizzata e vale anche per la KB Chat.
29. Righe 582-583: il banner di stima compare dopo il clic; i pulsanti si chiamano «🔄 Sincronizza» o «🔄 Sincronizza DokuWiki».
30. Riga 692: «📊 Genera mappa» compare per qualsiasi chat con messaggi; la mappa non si salva.
31. Righe 660-661: gli expander socratici sono chiusi; l'ora è quella del rendering; ci sono anche le etichette «✅ Confutato» e «✅ Riflettuto».
32. Riga 666: in modalità 🚀 Veloce lo storico socratico è nascosto (`ui/socratic/history_widget.py:33-35`).
33. Righe 706, 721: l'etichetta della chat ha il modello troncato a 12 caratteri; Elimina agisce subito, senza conferma.
34. Righe 734, 744: il bottone si chiama «💾 Salva {Formato}»; l'export multiplo compare solo se la chat corrente ha messaggi.
35. Riga 773: «↩️ Torna a Local/Remote» riporta sempre a «Local (Ollama)» (`ui/privacy_warning.py:213-216`).
36. Riga 788: «Limite ancora valido in v1.15.2» → v1.15.3, aggiungendo le voci 1 e 2.
37. Riga 95: «`streamlit>=1.28.0`» è superato (`requirements.txt` ha `==1.53.1`); anche l'intestazione di `requirements.txt` dice ancora v1.15.1.
38. Riga 89: Python ≥ 3.10 nel manuale, ma il README dice «3.9+» (`README.md:344`). → allineare il README.
39. Riga 463: la stima dei token conta solo il testo digitato e le risposte; l'ID mostra le ultime 8 cifre.
40. README e installer: «Architettura v1.15.2» (`README.md:267`) e `installer/INIZIA-QUI.txt` «v1.15.1» sono superati; il README descrive Poetry (`README.md:460-465`).

---

## 2. La SPEC contro tutto il resto

Legenda: ✅ regge · ✏️ va corretta · ➕ manca qualcosa.

### 2.1 I punti della SPEC, uno per uno

| SPEC | Esito | Che cosa ho trovato | Correzione proposta |
|---|---|---|---|
| §2.1 tre destinazioni da `connection_type` | ✅ | `core/llm_client.py:95-175` | — |
| §2.2 quattro vie verso il modello | ✅ | L'app usa del client **solo** `invoke` e `stream_invoke` (17 chiamate in `app.py` e `ui/socratic/`, nessun altro attributo). Un involucro con questi due metodi copre tutto | aggiungere l'elenco esatto: `ui/socratic/buttons.py:103,151,199,247,297` (alternative, assunzioni, limiti, confuta, rifletti) e `:478-539` |
| §2.3 «i pezzi del RAG non arrivano mai al cloud» | ✏️ | Vero solo per `Cloud provider`. Il blocco KB (`app.py:712-714`), il blocco upload (`ui/file_upload.py:205`) e quindi la Vision guardano **l'etichetta** `connection_type == "Cloud provider"`. Un **Remote host su IP pubblico** riceve KB, KB Chat, file allegati e **immagini**: H3b (`app.py:573-583`) mostra solo un banner «Host esterno» | riscrivere: «mai a un `Cloud provider`; a un Remote host pubblico sì, con il solo banner». È una lacuna della 1.15.3, non della 1.16.0: vedi passo P2 (§4) |
| §2.3 Vision local-only | ✏️ | Stessa cosa: l'ADR-0001 dice «solo verso l'endpoint Ollama locale/remoto già consentito dal validatore SSRF», ma `is_blocked` blocca solo i link-local. Un remoto pubblico con un modello vision riceve le immagini | come sopra; la decisione «remoto pubblico = cloud» (domanda 5 della §13) vale anche per le immagini |
| §2.3 cloud «Custom» | ➕ | È `Cloud provider` anche quando il `base_url` è `localhost` (es. LM Studio): oggi KB e upload sono bloccati anche se il testo non esce. Con il guard basato su `classify_url` diventerebbe «in casa»: comportamento diverso dai blocchi esistenti | decidere una regola sola (la destinazione reale) per guard **e** blocchi; altrimenti scriverlo come eccezione nota |
| §2.4 che cosa esce in chiaro | ➕ | Mancano: la **cronologia di una conversazione caricata** (`ui/sidebar/llm_config.py:69-92` avvisa ma non filtra: «Non c'è alcun filtro che escluda i contenuti locali») e i messaggi dell'utente usati dalla **mappa della sessione** | aggiungerli all'elenco |
| §3 punto unico = `create_client` | ✅ | confermato; `get_socratic_client` (`app.py:292-311`) passa da lì | — |
| §3 `system_prompt` anonimizzato «una volta, con la sua tabella» | ✏️ **difetto** | Due chiamate separate a rizzo-pii danno **due numerazioni**: `[FULLNAME_1]` del system prompt e `[FULLNAME_1]` del messaggio possono essere persone diverse, e il ripristino ne rimetterebbe una sola. In più nel ramo RAG il `system_prompt` è **anche** dentro `full_prompt` (`app.py:810-822`) | anonimizzare `system_prompt` e `full_prompt` **nella stessa chiamata** (testo unico con un separatore, poi diviso) e costruire il client vero per ogni chiamata col system prompt pulito; oppure fondere le tabelle rinumerando. Test dedicato |
| §3 `invoke` | ➕ | `invoke` restituisce un oggetto risposta (i chiamanti leggono `.text`, poi `.content`, poi `str()`: `ui/socratic/session_map.py:140-146`, `ui/socratic/buttons.py:117-125`) | il guard deve restituire un oggetto con `.text` già ripristinato, non una stringa |
| §3 streaming | ✏️ | `StreamRestorer.push()` restituisce **delta**, mentre `app.py:860-866` vuole `chunk.text` **cumulativo** | il guard accumula i delta del restorer e produce chunk con `.text` cumulativo; scriverlo così nella SPEC |
| §3 mappa della sessione | ➕ | Il modello risponde in un formato che `_parse_llm_response` analizza (`session_map.py:149`). Un valore rimesso con caratteri speciali (virgolette, a capo) può rompere il formato | ripristinare **dopo** il parsing, campo per campo, o accettare il rischio; test con un nome inventato che contiene un apostrofo («D'Angelo») |
| §3 cronologia salvata con i valori veri | ✅ | `core/persistence.py:68-120` salva in `conversations/` (ignorata da git); KB Chat indicizza in locale; export (`export/exporters.py`) scrive file locali; embedding con sentence-transformers in locale (`rag/embeddings.py:45-50`) | — |
| §3 conversazioni salvate su cloud | ➕ | Il campo `provider` della conversazione salvata non dice se il guard era attivo | aggiungere ai metadati `"pii_guard": true/false` e il conteggio dei dati tolti (mai i valori) |
| §4 rizzo-pii | ✅ | i client rispettano l'API letta il 05/11 | — |
| §5 Annona | ✅ | — | — |
| §6 «la tabella non va nei log» | ➕ | L'app chiama `logging.warning` e `print` con eccezioni (`app.py:839-843`, `core/llm_client.py:89`); le eccezioni dei client non contengono testo, ma un errore del fornitore cloud può citare il prompt (già anonimizzato: ok). Nessun log oggi scrive il prompt | regola per il guard: mai `logging` di prompt o tabella; test che controlla i messaggi delle eccezioni |
| §7 `security_settings.yaml` | ✅ | il file ha solo `cloud_api_keys` e un segnaposto commentato `remote_servers`: la sezione `hybrid:` non va in conflitto | — |
| §8 tabella dei guasti | ✅ | coerente con i client | aggiungere la riga «immagine verso Remote host pubblico» (dipende dalla domanda 5) |
| §9 licenze | ✏️ | il README dichiara MIT e rimanda a `LICENSE`, che manca (già nella SPEC) | passo P1 |
| §11 limiti | ➕ | rizzo-pii toglie dal testo **anche gli importi, le date e gli URL** per default: in una domanda tecnica al cloud («il bonifico del 12/06 di € 1.200») il modello perde informazioni utili | collegato alla domanda 7 (tag in chiaro) |
| §12 piano dei test | ✏️ | il comando `python -m unittest` funziona; pytest non è nel venv e i test esistenti (`tests/test_persistence.py`) sono in stile pytest | aggiungere `pytest` ai requisiti di sviluppo, o scrivere tutto in `unittest` |

### 2.2 I due client contro la SPEC

| Promessa della SPEC | `core/pii_client.py` | `core/annona_client.py` |
|---|---|---|
| solo loopback | ✅ `PIINotLocal` (testato con IP privato, dominio, `0.0.0.0`) | ✅ `AnnonaNotLocal` |
| nessun valore nei `repr` | ✅ `mapping` `repr=False` | ✅ `egress` `repr=False` |
| guasti → eccezioni esplicite | ✅ `PIIServiceUnavailable`, `PIIMappingDisabled`, `PIIServiceError` | ✅ `AnnonaUnavailable` per 404/409/503 e rete |
| ripristino come `reverse()` di rizzo-pii | ✅ una passata, parentesi tutto-o-niente, confine Unicode. ✏️ Il grassetto `**` non viene «assorbito» come fa rizzo-pii: qui il valore resta dentro gli asterischi (`**Mario Rossi**`), che in Markdown è giusto | — |
| `held` con HTTP 200 | — | ✅ `AskResult.held` |
| `decide`/`record` | — | ✅ solo interfaccia, `AnnonaUnsupported` |
| messaggi d'errore senza testo dell'utente | ✅ solo codici HTTP e tipo d'eccezione | ✅ |
| difetto minore | il messaggio di `PIINotLocal` contiene l'URL configurato (non è un dato personale: ok) | `cancel(run_id)` mette `run_id` nel percorso senza codificarlo: va bene per un uuid, ma il client dovrebbe rifiutare caratteri diversi da `[A-Za-z0-9_-]` |

---

## 3. Il bug «[object Object]»

### 3.1 La causa (riprodotta)

Succede con i **messaggi già nella cronologia**, cioè con **tutte le risposte dopo che lo streaming è finito**. Durante lo streaming la risposta è disegnata con `placeholder.markdown(response_text)` (`app.py:870`), il Markdown nativo di Streamlit, e il codice è giusto. Poi `app.py:903` fa `st.rerun()`, e da lì in poi ogni messaggio passa da `render_chat_message` (`ui/chat.py:84-91`):

1. **`ui/chat.py:85`** converte il Markdown in HTML con `markdown_it` → `<pre><code class="language-python">…</code></pre>`;
2. **`ui/chat.py:88-91`** passa quell'HTML, dentro un `<div class="assistant-bubble">`, a **`st.markdown(..., unsafe_allow_html=True)`**;
3. **`st.markdown` non mostra l'HTML così com'è: lo rilegge come Markdown** (CommonMark con HTML grezzo). Per CommonMark un blocco HTML che comincia con `<div>` **finisce alla prima riga vuota**. Nel codice Python le righe vuote ci sono quasi sempre (fra due metodi, fra due funzioni). Dopo la riga vuota il resto del codice viene letto come **Markdown**: le righe rientrate di 4 spazi diventano un **nuovo blocco di codice annidato** dentro il `<code>` di prima, `__init__` può diventare grassetto, `# commento` un titolo;
4. **nel frontend di Streamlit 1.53.1** il componente dei blocchi di codice (`CustomCodeTag`, in `streamlit/static/static/js/index.DSTThs-t.js`) fa `String(children)`. Se dentro `<code>` c'è solo testo, va bene; se c'è anche un **elemento** (il `<pre>` annidato, un `<strong>`), JavaScript lo scrive come **«[object Object]»**, e unisce i pezzi con le virgole;
5. **quella stringa** è sia il testo mostrato sia quello che il **pulsante di copia** mette negli appunti (`StreamlitSyntaxHighlighter.BOkJThtV.js`: `CopyButton` riceve la stessa stringa). Per questo in VS Code arriva «[object Object]».

Riproduzione fatta il 06/11 senza installare niente, con `markdown_it` già nel venv (lo script minimo è nel §3.3) e leggendo il JavaScript di Streamlit 1.53.1 installato nel venv. Il secondo passaggio mostra il `<pre><code>` annidato che nasce dalla riga vuota:

```text
<pre><code class="language-python">class Cliente:
    def __init__(self, nome):
        self.nome = nome
<pre><code>def saluta(self, *args, **kwargs):       ← nuovo blocco DENTRO il primo
    return f&amp;quot;Ciao {self.nome}&amp;quot;   ← e le virgolette doppiamente escapate
</code></pre>
<p></code></pre></p>
```

### 3.2 In quali casi

| Caso | Succede? |
|---|---|
| codice **con** almeno una riga vuota (quasi tutto il Python) | **sì** |
| codice senza righe vuote | no: il blocco HTML non si interrompe |
| durante lo streaming | no; compare **al termine**, quando la pagina si ridisegna |
| conversazione salvata e ricaricata | sì |
| modelli locali o cloud | tutti e due: il difetto è nella resa, non nel modello |
| pulsante di copia del blocco | sì, copia «[object Object]» |
| selezione col mouse | sì, perché anche il testo a schermo è sbagliato; in più si porta dietro i pezzi spezzati |
| messaggi dell'utente con codice incollato | sì, stessa funzione |
| altri effetti dello stesso difetto | virgolette mostrate come `&quot;`, rientri persi, `#` diventati titoli, `*` e `_` diventati corsivo/grassetto |

### 3.3 Come verificarlo nell'app (senza installare niente)

1. Avviare l'app come sempre, con un modello locale qualsiasi.
2. Chiedere: «Scrivi una classe Python Cliente con due metodi separati da una riga vuota».
3. Durante lo streaming il codice è giusto; quando finisce e la pagina si ridisegna, nel blocco compare «[object Object]» (o il codice spezzato in due riquadri).
4. Passare sul blocco, premere l'icona di copia, incollare in un editor.

Riproduzione minima senza modello: lo script qui sotto, con `venv/bin/python -I script.py`.

```python
from markdown_it import MarkdownIt
risposta = "```python\nclass A:\n    def f(self):\n        pass\n\n    def g(self):\n        pass\n```\n"
inner = MarkdownIt("commonmark", {"html": False}).enable("table").render(risposta)
wrapped = f'<div class="assistant-bubble">{inner}</div>'
print(MarkdownIt("commonmark", {"html": True}).render(wrapped))   # come lo rilegge st.markdown
```

### 3.4 La correzione proposta (non fatta)

In ordine di preferenza:

1. **Non far rileggere l'HTML a `st.markdown`.** La bolla si fa con un contenitore nativo e il contenuto con il Markdown di Streamlit: `with st.container(key=f"bubble-{role}-{index}"):` poi `st.markdown(content)` (senza `markdown_it` e senza `unsafe_allow_html`). Il CSS delle bolle si sposta da `.assistant-bubble` alle classi `st-key-bubble-assistant-*` che Streamlit dà ai contenitori con `key`. Vantaggi: blocchi di codice nativi (evidenziazione e copia giuste), nessun HTML grezzo, stessa resa durante e dopo lo streaming. Da verificare: lo stile delle bolle (`ui/styles.py:20-160`) e il riquadro allegati (`ui/chat.py:78-82`, già escapato).
2. **Correzione minima:** lasciare `markdown_it`, ma dopo il `render` sostituire, **dentro i blocchi `<pre>`**, i caratteri a capo con l'entità `&#10;`. Senza righe vuote il blocco HTML non si spezza e il frontend riceve testo semplice. Più piccola, ma tiene in piedi la doppia lettura HTML→Markdown, fragile.
3. Usare `st.html()` per la bolla: niente rilettura Markdown, ma si perdono i blocchi di codice di Streamlit (niente pulsante di copia).

**Test proposti:** un test Python su una funzione pura `render_bubble_html()` (se si sceglie la 2) che controlla l'assenza di righe vuote dentro `<pre>`; per la 1, un test con `streamlit.testing.v1.AppTest` che verifica che il blocco di codice sia un elemento `code` con il testo intero. Più il controllo a mano del §3.3.

---

## 4. I passi verso la v1.16.0

Ogni passo è piccolo, con un suo ramo da `dev` (o i suoi commit su questo ramo), i test e il criterio di fine. **Subito** = non dipende dalle dieci domande della §13 della SPEC.

| # | Passo | Ramo | Test | Finito quando | Dipende da |
|---|---|---|---|---|---|
| **P0** | **Bug «[object Object]»** (correzione 1 del §3.4) | `fix/chat-code-blocks` | AppTest o funzione pura; prova a mano §3.3; regressione: tabelle, allegati, socratici | un blocco Python con righe vuote si copia identico in VS Code, prima e dopo il ricaricamento della conversazione | **subito**. Può uscire come **1.15.4** prima della 1.16.0 |
| **P1** | `LICENSE` (MIT) e `NOTICE` (rizzo-pii MIT, Annona Apache-2.0, nota AGPL dei binari di rizzo-pii) | `chore/license-notice` | — | i link del README a `LICENSE` funzionano | **subito** (testo del NOTICE: domanda 10) |
| **P2** | Blocchi KB, upload e Vision sulla **destinazione reale**, non sull'etichetta (lacuna §2.1) | `fix/egress-real-destination` | test di `classify_url` + i tre blocchi con un Remote host pubblico finto | KB, upload e immagini verso un IP pubblico si comportano come verso il cloud | **domanda 5**. È una correzione di sicurezza della 1.15.x: si può fare anche prima |
| **P3** | Manuale, prima parte: versione, tabella dei problemi, errori del §1 | `docs/manuale-1.15.3` | — | nessuna voce «alta» del §1 aperta | **subito** |
| **P4** | `pytest` nei requisiti di sviluppo, `tests/` lanciabile con un comando | `chore/test-runner` | tutti i test passano | `venv/bin/python -m pytest` verde | **subito** (serve l'ok per installare pytest nel venv) |
| **P5** | Configurazione `hybrid:` in `security_settings.yaml` + lettore con default spenti | questo ramo | test del lettore: file assente, sezione assente, `cloud: allow` rifiutato | ibrido spento = 1.15.3 identica | **domanda 8** |
| **P6** | `GuardedClient` con rizzo-pii (§3 SPEC, con le correzioni del §2.1: system prompt nella stessa chiamata, `invoke` che restituisce `.text`, streaming cumulativo) | questo ramo | i sei punti del piano dei test della SPEC + il system prompt + la mappa con «D'Angelo» | nessuna chiamata a un client cloud finto contiene i valori inventati; servizio giù = zero chiamate | domande **3, 4, 5, 6, 7** |
| **P7** | Le letture di Annona nella sidebar (stato, ultime decisioni, verifica catena) | questo ramo | test con `FakeSession` | sidebar giusta con Annona acceso, spento, senza policy | domanda **1** (solo se si tiene Annona) |
| **P8** | La strada scelta per Annona (A gateway sperimentale, o C quando c'è) | questo ramo | come P6 | — | domande **1, 2, 6** |
| **P9** | UI: badge «dati tolti», vista «cosa ha visto il modello» | questo ramo | AppTest | — | domanda **9** |
| **P10** | Prova dal vivo con rizzo-pii acceso e un cloud vero, dati inventati, controllo di cosa esce | — | `strace` o proxy locale, come il 23/10 | verbale della prova nel vault | dopo P6 |
| **P11** | Manuale (capitolo ibrido), README (con la dichiarazione su Akaion), CHANGELOG, ROADMAP | questo ramo | — | — | dopo P6-P9 |
| **P12** | Cambio di versione `1.16.0` (`config/constants.py`, `pyproject.toml`, `branding.yaml`, `VERSION_DESCRIPTION`) e merge in `dev` | — | tutti i test | Gilles fa merge e push | ultimo |
| **P13** | Le correzioni di codice che escono dal §1: (a) **Elimina** toglie la chat anche dalla KB Chat; (b) il limite di `MAX_FILE_SIZE_MB` controllato davvero; (c) Anthropic e Google nei requisiti o un messaggio chiaro se mancano; (d) il widget allegati svuotato dopo l'invio e con «Nuova»; (e) M3 | un ramo `fix/...` per ciascuna | un test per ciascuna | la voce corrispondente del §1 si chiude anche nel manuale | **subito**; (a) è la più grave, perché il dato resta dopo che l'utente crede di averlo cancellato |

**Ordine consigliato:** P0 e P13a subito, poi P1, P3, P4 e il resto di P13 (si possono fare tutti mentre Gilles risponde alle domande). P2 appena c'è la risposta alla domanda 5; poi P5-P12. P0, P2 e P13 si possono raccogliere in una **1.15.4** di sole correzioni, prima della 1.16.0.

---

## 5. Graphify

**Servirebbe?** Sì, ma poco, e solo per alcune domande. Il codice è piccolo (una quarantina di file Python) e la parte che conta per la 1.16.0 sta in pochi file già letti: `app.py`, `core/llm_client.py`, `ui/chat.py`, `ui/socratic/`, `ui/file_upload.py`. Un grafo aiuterebbe:
- nei giri P6 e P11, per trovare **chi chiama chi** (ogni via verso `invoke`, ogni lettura di `connection_type`) senza rileggere `app.py`, che ha 900 righe;
- a tenere legati codice, SPEC, ADR e manuale, che oggi si contraddicono (§1).

Per i giri piccoli (P0, P1, P3) costa più di quello che rende.

**Dove metterne la cartella.** Graphify scrive `graphify-out/` nella cartella **da cui lo si lancia**, e nella repo ci sono cartelle che non deve leggere né mandare a un modello:

| Cartella nella repo | Perché va esclusa |
|---|---|
| `conversations/` | chat salvate, possono contenere dati veri |
| `knowledge_base/`, `wiki_cache/` | documenti e pagine wiki dell'utente |
| `secrets/` | credenziali |
| `venv/`, `old/`, `__pycache__/` | rumore |

Proposta:
1. lanciarlo **da fuori la repo**, con la cartella di uscita in `~/Documenti/AI/graphify/datapizza-streamlit-interface/` (vicina al resto di `~/Documenti/AI`, fuori da git e dal vault), dandogli come ingresso **solo** `app.py core ui rag config export installer docs *.md *.yaml`;
2. in ogni caso aggiungere `graphify-out/` al `.gitignore` (una riga, da fare nel passo P4), perché la sua cache potrebbe finire nella cartella d'ingresso: **da verificare** al primo uso;
3. non metterlo nel vault: il grafo del vault è per le note, e mescolarli confonde le domande.
