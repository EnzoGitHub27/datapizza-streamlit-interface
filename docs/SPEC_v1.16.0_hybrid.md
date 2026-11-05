# SPEC v1.16.0 «ibrida» — rizzo-pii e Annona come servizi opzionali

**Stato:** bozza da leggere (giro 1) · **Data:** 2026-11-05 · **Base:** v1.15.3 · **Ramo:** `feat/hybrid-pii-annona`
**Cosa c'è già nel ramo:** questa SPEC, `core/pii_client.py`, `core/annona_client.py` e i loro test con i servizi simulati. **Niente è collegato all'interfaccia.**
**Cosa non c'è:** il collegamento in `app.py`, la configurazione nuova, il cambio di versione, README, CHANGELOG e ROADMAP. Si fanno dopo che Gilles ha letto questa SPEC.

---

## 1. L'obiettivo in tre righe

L'Interface diventa da sola un ambiente ibrido semplice da installare:

1. **rizzo-pii** toglie i dati personali prima che il testo esca verso un fornitore cloud;
2. **Annona** decide dove può girare il passo (locale, server remoto, cloud) e tiene il registro;
3. quando la risposta torna, i segnaposto tornano valori **solo sul computer**.

Tutti e due sono **servizi separati, opzionali e spenti per default**. Senza di loro l'Interface fa esattamente quello che fa la 1.15.3.

---

## 2. Come parte oggi il testo verso i modelli (1.15.3)

### 2.1 Un solo costruttore di client

Tutte le chiamate ai modelli passano da un oggetto creato da **`create_client()`** in `core/llm_client.py:95`. Le destinazioni sono tre, decise da `connection_type`:

| `connection_type` | Client | Dove va il testo |
|---|---|---|
| `Local (Ollama)` | `OpenAILikeClient` (`core/llm_client.py:167`) | Ollama sul computer |
| `Remote host` | `OpenAILikeClient` | un server Ollama da `remote_servers.yaml` o un IP scritto a mano |
| `Cloud provider` | `ClientFactory.create` per OpenAI, Anthropic, Google; `OpenAILikeClient` per «Custom» (`core/llm_client.py:125-165`) | il fornitore cloud, con i modelli di `cloud_models.yaml` |

### 2.2 I quattro punti dove si chiama il modello

| Dove | Che cosa parte | Come |
|---|---|---|
| **Chat** — `app.py:787` crea il client, `app.py:856` chiama `client.stream_invoke(llm_input)` | `full_prompt`: la cronologia (`get_conversation_history`) + il messaggio con il testo dei file allegati (`enrich_prompt_with_files`) **oppure**, con il RAG, `system_prompt` + pezzi della KB / KB Chat + messaggio (`app.py:808-829`) | streaming |
| **Bottoni socratici** — `get_socratic_client()` `app.py:292`, usato a `app.py:617` e in `ui/socratic/buttons.py:117-311` | prompt costruiti dalla risposta e dalla domanda | `client.invoke` |
| **Nudge, generazione e rigenerazione socratica** — `app.py:455-504` | idem, su cronologia e messaggi | `client.invoke` |
| **Mappa della sessione** — `app.py:893`, `ui/socratic/session_map.py:294` | **tutti i messaggi** della sessione | `client.invoke` |

In più, il **`system_prompt`** viaggia dentro il client (parametro del costruttore) e quindi parte a ogni chiamata.

### 2.3 Le difese che ci sono già

- **Cloud bloccato con KB o KB Chat attive** (`app.py:713-714`): oggi i pezzi del RAG **non arrivano mai al cloud**.
- **Upload file disabilitato su cloud** (`ui/file_upload.py:205-211`): niente testo di documenti verso il cloud.
- **Vision local-only** (ADR-0001, `core/llm_client.py:177-208`, `app.py:831-845`): le immagini diventano `MediaBlock` solo con un modello vision locale; sul cloud non c'è l'upload. È il precedente di questa SPEC: **una regola che impedisce a un tipo di dato di andare al cloud**.
- **Dialogo privacy** (`ui/privacy_warning.py`): se nella sessione ci sono stati documenti e si passa al cloud, si sceglie fra «Reset chat» e «Procedi comunque» con conferma. Protegge la **cronologia**, che può contenere quello che il modello locale ha letto nei documenti.
- **SSRF** (`core/url_validator.py`, `is_blocked`) e **banner sulla destinazione reale** (H3b, `classify_url`, `app.py:573-576`): un «Remote host» che risolve su un IP pubblico è di fatto fuori casa.

### 2.4 Che cosa può ancora uscire verso il cloud, in chiaro

Quello che l'utente **scrive** (nomi, codici fiscali, IBAN incollati nel messaggio), la **cronologia** dopo «Procedi comunque», il `system_prompt`, i prompt socratici e la mappa della sessione. È questo che la 1.16.0 deve coprire.

---

## 3. Il punto unico d'intercettazione

**Il punto è `create_client()` in `core/llm_client.py`.** Tutte e quattro le vie della §2.2 ricevono il loro client da lì (la chat direttamente, i socratici attraverso `get_socratic_client`, la mappa usando `client.invoke` del client della chat). Nessun'altra parte del codice parla con un modello.

La proposta: `create_client()` restituisce, **solo quando il servizio ibrido è attivo**, un involucro (`GuardedClient`) attorno al client vero, con gli stessi metodi usati dall'app:

```text
GuardedClient(inner, destination, pii, annona, settings)
  .invoke(input)          → guard(input) → inner.invoke(...)        → restore(risposta)
  .stream_invoke(input)   → guard(input) → inner.stream_invoke(...) → StreamRestorer
```

- **`input`** può essere una stringa o una lista di blocchi (`TextBlock`, `MediaBlock`): il guard anonimizza il testo dei `TextBlock`. Un `MediaBlock` verso il cloud è **sempre** un errore (la regola della Vision resta).
- **Il `system_prompt`** si anonimizza una volta, quando `create_client` costruisce il client vero, con la sua tabella.
- **`destination`** non è solo `connection_type`: per `Remote host` e Cloud «Custom» si usa `classify_url(base_url)` (come H3b). `loopback`/`private` = in casa; `public` = fuori casa, trattato come il cloud.
- **Lo streaming:** l'app calcola i delta su `chunk.text` cumulativo (`app.py:860-866`). Il guard deve restituire chunk con un `.text` cumulativo **già ripristinato** e senza segnaposto a metà: lo fa `StreamRestorer` (in `core/pii_client.py`), che trattiene la coda che potrebbe essere l'inizio di un segnaposto (`[FULLN…`).
- **La cronologia** salvata (`add_message`) contiene i valori veri, perché la risposta è già ripristinata: resta sul computer. A ogni turno si anonimizza di nuovo tutto il `full_prompt`, quindi la numerazione dei segnaposto è coerente **dentro** la chiamata.

Il vantaggio di questo punto: il cambio in `app.py` è quasi nullo (una riga per passare le impostazioni), e nessuna via nuova verso il modello può nascere senza passare dal guard.

---

## 4. rizzo-pii: l'API (fonte primaria)

**Fonte:** [Rizzo-AI-Academy/rizzo-pii](https://github.com/Rizzo-AI-Academy/rizzo-pii), `main` al commit `9057eef` (22/10/2026), `APP_VERSION = "2.0.0"` in `src/app/app.py:125`. Il servizio sul portatile **era spento** durante questo giro: niente prove dal vivo, solo codice e documentazione.

Servizio Flask su **`127.0.0.1:5005`** (`src/app/server_config.py:33-34`), senza autenticazione.

| Endpoint | Che cosa fa | Usato dal client |
|---|---|---|
| `GET /health` (`/healthz`) | 200 = modello caricato; **503** = server su, modello no. Corpo: `model_loaded`, `app_version`, `device`, `mapping_enabled`, `excluded_tags` | sì, `health()` / `is_ready()` |
| `POST /analyze` | `{"text", "include_mapping", "exclude_tags"}` → `anonymized_text`, `mapping` (`"[CF_1]": "…"`), `mapping_enabled`, `n_entities`, `by_label`, `segments`, e `source_text` solo con la tabella attiva | sì, `anonymize()` |
| `POST /pdf`, `/pdf/preview`, `/preview` | PDF redatto, anteprime | no (l'upload sul cloud resta bloccato) |
| `GET/POST /settings` (`/tags`) | legenda dei 25 tag, tag esclusi, tabella on/off, salvati in `prefs.json` | no: l'Interface **non cambia** le impostazioni di rizzo-pii |
| `GET/POST /config` | host e porta per il prossimo avvio | no |

**Tre cose da sapere, dal codice:**

1. **Il ripristino non è un endpoint.** Lo fa la UI di rizzo-pii in JavaScript (`reverse()`, `src/app/app.py:1836`). `core/pii_client.py` lo rifà in Python con le stesse regole: una passata sola, parentesi tutto-o-niente, confine di parola Unicode (un `[CF_12]` inventato dal modello non diventa il `CF_1`).
2. **La modalità definitiva** (`mapping_enabled: false`, da `/settings` o `--no-mapping`) non restituisce la tabella. Il client chiede sempre `include_mapping: true`, e se la tabella non torna solleva `PIIMappingDisabled`: senza tabella la risposta del modello resterebbe piena di segnaposto.
3. **`/analyze` fa `strip()` del testo**; con testo vuoto risponde 400 (il client non lo chiama).

---

## 5. Annona: che API espone (fonte primaria)

**Fonte:** [akaion-ai/annona](https://github.com/akaion-ai/annona), tag `v0.1.3` al commit `beb9438` (21/09/2026), Apache-2.0, Python ≥ 3.10. Letto il codice (`runner/kernel_api.py`, `runner/local_api.py`, `runner/placement/`, `runner/audit/ledger.py`, `runner/policy/`), **niente installato, nessuno script lanciato**. Il clone è identico ai `sorgenti/` della prova isolata del 23/10.

### 5.1 Le tre facce di Annona

| Faccia | Che cosa offre | Per l'Interface |
|---|---|---|
| **HTTP** — il demone `annona run`, FastAPI su `127.0.0.1:7070` | letture: `/health`, `/api/kernel/status`, `/policy`, `/substrates`, `/ledger`, `/ledger/verify`; esecuzione: **`POST /api/kernel/ask`** (+ `/ask/{run_id}/cancel`); scrittura della policy: `POST/PUT /api/kernel/policy` | il client `core/annona_client.py` copre letture e `ask` |
| **Libreria Python** — il pacchetto `runner` | `PolicyClassifier(policy).classify_text(text)` → classe; `PlacementDecisionEngine(policy, registry).place(klass, Requirement)` → `Placement`; `Ledger(path).record(kind, outcome=, klass=, substrate=, payload=…)` → voce a catena | è esattamente «decidi e registra», ma va **installata nel venv** |
| **Riga di comando** — `annona` | `policy test <classe>`, `why <step>`, `verify` | utile per Gilles, non per l'app |

### 5.2 Il punto che conta: via HTTP Annona **esegue**, non **consiglia**

`POST /api/kernel/ask` prende un prompt e fa tutto lui: classifica il testo, sceglie il substrato della **sua** policy, chiama rizzo-pii se la regola dice `redact`, **chiama il modello**, rimette i dati e scrive il registro. La risposta contiene `response`, `placement` (`class`, `outcome`, `substrate`, `reason`), `decisions` (le voci nuove del registro) ed `egress` (il testo uscito, parola per parola).

Annona 0.1.3 **non ha** un endpoint per chiedere «dove andrebbe questo testo, se lo mandassi io al cloud?» senza eseguirlo, né un endpoint per scrivere nel registro un passo fatto da un altro programma. Per questo in `core/annona_client.py` i metodi `decide()` e `record()` sono **solo interfaccia** e sollevano `AnnonaUnsupported`.

Altre cose dal codice e dalle prove del 23/10:
- da localhost, **senza `Origin`**, le chiamate passano **senza token** (`runner/pairing.py`); un sito nel browser riceve 401. Il client accetta solo indirizzi di loopback;
- un passo `held` torna con **HTTP 200**: l'esito vero sta in `placement.outcome` (il client lo espone come `AskResult.held`);
- `ask` è sincrono e può durare decine di secondi: **niente streaming**;
- con gli strumenti accesi la redazione di Annona 0.1.3 gira a vuoto: con l'Interface si usa `max_iterations=1` e nessuno strumento.

### 5.3 Tre strade per l'integrazione (da scegliere)

| | Strada | Come | Pro | Contro |
|---|---|---|---|---|
| **A** | **Annona fa da gateway** | per le destinazioni sotto Annona, l'Interface chiama `AnnonaClient.ask()` invece del suo client | funziona con Annona 0.1.3 così com'è; decisione, redazione e registro sono di Annona, con le sue garanzie | l'Interface perde lo streaming, la scelta del fornitore e dei modelli (`cloud_models.yaml`) e le API key: i substrati cloud vanno configurati **nella policy di Annona**, con le chiavi lì; due configurazioni da tenere allineate |
| **B** | **Annona come libreria** | `pip install annona==0.1.3` nel `venv`, e nel guard: `classify_text` → `place` → `Ledger.record` | decide prima, l'Interface tiene il suo client e lo streaming; nessun demone da accendere | ~94 pacchetti in più nel venv dell'Interface (fra cui textual, uvicorn, fastapi, pdfplumber); `datapizza-ai-core` è già `0.1.3` in tutti e due, quindi oggi compatibile, ma i pin dovranno restare allineati; il registro va scritto nel file del demone senza che il demone sia in esecuzione (o con due scrittori, che Annona protegge solo con un lock **nel processo**) |
| **C** | **Un endpoint nuovo in Annona** | chiedere ad Akaion `POST /api/kernel/place` (testo + destinazione → placement + voce nel registro, senza esecuzione) | la forma giusta: servizi separati, l'Interface decide con Annona e chiama il suo client | dipende da Akaion; nel frattempo serve A o B |

**La mia proposta per la 1.16.0:** rizzo-pii dentro il guard dell'Interface (§3), con la regola fissa «verso fuori casa solo testo anonimizzato»; di Annona, **le letture** (stato, registro, verifica della catena) in una sezione della sidebar, e la **strada A come opzione sperimentale** per chi vuole che sia Annona a decidere e chiamare. La strada C si chiede ad Akaion, dichiarando il conflitto d'interessi (§9). La B la sconsiglio per una «installazione semplice».

Il client attuale (`core/annona_client.py`) serve già ad A e alle letture; `decide()`/`record()` restano pronti per C.

---

## 6. Il flusso ibrido

```text
utente scrive ─┐
cronologia ────┤
pezzi RAG ─────┼─▶ full_prompt ─▶ create_client() → GuardedClient
system_prompt ─┘                          │
                                          ├─ destinazione in casa (Ollama locale / remoto privato)
                                          │      → il testo parte così com'è (come oggi)
                                          │
                                          └─ destinazione fuori casa (cloud, remoto pubblico)
                                                 1. rizzo-pii /analyze  → testo con [FULLNAME_1], [CF_1]…
                                                    tabella solo in memoria
                                                 2. Annona (§5.3): decide e registra
                                                    held → blocco + avviso
                                                 3. client cloud ← solo testo pulito
                                                 4. risposta → StreamRestorer → valori veri, in locale
                                                 5. tabella buttata a fine chiamata
```

La tabella dei segnaposto **non** va nei log, nel registro di Annona, nella cronologia salvata, nella KB Chat né nell'export: vive solo per la durata della chiamata (`AnonymizedText.mapping` ha `repr=False`).

---

## 7. Configurazione: spenta per default

Una sezione nuova in **`security_settings.yaml`** (il file esiste già e parla di sicurezza; un file nuovo non serve):

```yaml
# 🆕 v1.16.0 — Ambiente ibrido (tutto spento per default)
hybrid:
  pii:
    enabled: false                  # rizzo-pii prima del cloud
    url: "http://127.0.0.1:5005"    # solo loopback: il client rifiuta altri indirizzi
    timeout_s: 30
    apply_to: ["cloud", "remote_public"]   # dove si anonimizza
    exclude_tags: []                # tag lasciati in chiaro, es. ["AMOUNT"]
  annona:
    enabled: false
    url: "http://127.0.0.1:7070"
    mode: "read"                    # read = stato e registro in sidebar; gateway = strada A
  on_service_down:
    cloud: "block"                  # fisso: non configurabile a "allow"
    local: "proceed"
```

`on_service_down.cloud` si legge ma **non accetta** altri valori: un'impostazione che permette di mandare in chiaro al cloud quando rizzo-pii è spento è la cosa che questa versione esiste per evitare.

---

## 8. Quando un servizio non risponde

| Situazione | Destinazione in casa | Destinazione fuori casa |
|---|---|---|
| ibrido spento (default) | come la 1.15.3 | come la 1.15.3 |
| rizzo-pii spento, in timeout o modello in caricamento (`PIIServiceUnavailable`) | **si procede** (il testo non esce di casa) | **si blocca e si avvisa**: «rizzo-pii non risponde: il messaggio non è stato inviato al cloud». Il messaggio dell'utente resta nella casella |
| rizzo-pii in modalità definitiva (`PIIMappingDisabled`) | si procede | si blocca e si avvisa, con l'indicazione per riattivare la tabella |
| rizzo-pii risponde male (`PIIServiceError`) | si procede | si blocca |
| Annona spento o senza policy (`AnnonaUnavailable`), modo `read` | si procede, la sidebar dice «Annona non risponde» | si procede **solo se** rizzo-pii ha pulito il testo; la sidebar dice che il passo **non è registrato** |
| Annona spento, modo `gateway` | si procede col client dell'Interface | **si blocca**: chi ha scelto il gateway ha scelto che decida Annona |
| Annona risponde `held` | — | si blocca e si mostra `placement.reason` |
| `MediaBlock` (immagine) verso fuori casa | — | errore, sempre (ADR-0001) |

In tutti i blocchi: nessun byte verso il fornitore, un `st.error` chiaro, nessun testo dell'utente nei log.

---

## 9. Licenze, e perché via API

| Strumento | Licenza | Come la usiamo |
|---|---|---|
| rizzo-pii, **codice** (`src/`) | MIT | non lo copiamo: lo chiamiamo via HTTP. La logica di ripristino in `core/pii_client.py` è riscritta in Python, con le stesse regole (da citare nel NOTICE per correttezza) |
| rizzo-pii, **binari** (AppImage, .deb, .exe, .dmg) e **immagine Docker** | **AGPL-3.0**, perché contengono PyMuPDF (`THIRD_PARTY_LICENSES.md`) | l'utente li installa da sé; l'Interface **non li distribuisce** né li impacchetta |
| Annona | Apache-2.0 | strada A e C: chiamata via HTTP; strada B: dipendenza Python (Apache-2.0 è compatibile, serve il NOTICE) |

**Perché come servizi separati:** l'Interface parla con due processi distinti attraverso HTTP su loopback, senza importare il loro codice né distribuire i loro binari. Così la licenza dell'Interface non cambia, l'utente sceglie se installarli, e ciascuno si aggiorna per conto suo.

**Da verificare** (non è un parere legale):
- che la chiamata HTTP a un binario AGPL che gira **sullo stesso computer** non renda l'Interface un'opera combinata: l'interpretazione comune dice di no (comunicazione fra programmi separati), ma va confermata;
- se in futuro l'installer dell'Interface **scaricasse** l'AppImage di rizzo-pii, diventerebbe distribuzione: va evitato o valutato a parte;
- la strada B porta ~94 pacchetti con licenze proprie: va fatto l'elenco prima di sceglierla;
- la licenza dell'Interface stessa: il README dichiara MIT e rimanda a `LICENSE`, ma **nel repo il file `LICENSE` non c'è**. Va aggiunto, insieme al NOTICE.

---

## 10. Conflitto d'interessi

Gilles è **Technical Advisor di Akaion**, l'azienda che sviluppa Annona. Va scritto nel README della 1.16.0, nella sezione dell'ambiente ibrido, con parole semplici. Proposta:

> **Dichiarazione:** sono Technical Advisor di Akaion, che sviluppa Annona. Annona è opzionale e spenta per default; l'ambiente ibrido funziona anche solo con rizzo-pii, che non ha legami con Akaion.

Lo stesso vale per la richiesta della strada C ad Akaion e per le segnalazioni elencate nel dossier delle prove.

---

## 11. Limiti onesti

- **Pseudonimizzato non è anonimo** (GDPR): la tabella esiste, sul computer, per la durata della chiamata.
- **rizzo-pii lavora bene su testo italiano**, non su codice o testo tecnico: lì toglie troppo (in modo prudente). Un prompt con codice incollato può tornare pieno di segnaposto.
- **Il contesto si perde:** il modello cloud vede `[FULLNAME_1]`, non sa se è un cliente o un fornitore. Va detto nella UI.
- **Annona scrive il testo del passo in chiaro nel suo log** (`logs/annona.log`) e il `payload_digest` del registro non ha sale: con la strada A, chi ha accesso al computer vede quei file.
- **La numerazione** dei segnaposto vale dentro una chiamata: `[FULLNAME_1]` di un turno può essere un'altra persona nel turno dopo, se cambia l'ordine nel testo. Il modello cloud non lo sa.
- **Le prestazioni:** rizzo-pii gira sul processore; con la cronologia lunga ogni turno anonimizza di nuovo tutto. Da misurare.

---

## 12. Piano dei test

**Già nel ramo** (56 test, servizi simulati con `tests/fakes_http.py`, nessuna chiamata di rete; `venv/bin/python -m unittest tests.test_pii_client tests.test_annona_client`):
- `tests/test_pii_client.py`: solo loopback; `/health` pronto, in caricamento (503), spento, timeout; `/analyze` ok, payload, tag esclusi, testo vuoto, 503, 400, JSON rotto, modalità definitiva; nessun valore nel testo pulito né nel `repr`; ripristino (forme con e senza parentesi, indici inventati, confini di parola con lettere accentate, una passata sola, `_10` contro `_1`, grassetto markdown); streaming spezzato a caso e un carattere alla volta.
- `tests/test_annona_client.py`: solo loopback; health, status, policy 404, ledger con i parametri, verify, substrati; `ask` con `redacted`, con `held` in HTTP 200, 503 senza executor, 409, prompt vuoto, timeout lungo, `egress` fuori dal `repr`; `decide`/`record` → `AnnonaUnsupported`.

**Da scrivere col collegamento (giro 2):**
1. `GuardedClient`: stringa e lista di blocchi; `system_prompt`; `MediaBlock` verso il cloud → errore; destinazione da `classify_url`.
2. Tutte e quattro le vie della §2.2 passano dal guard (test che fallisce se una chiamata arriva al client vero senza guard).
3. Tabella §8, una riga per test: ogni blocco = zero chiamate al client cloud finto.
4. Il chunk cumulativo dello streaming resta coerente con il calcolo dei delta di `app.py:860-866`.
5. Ibrido spento → comportamento identico alla 1.15.3 (regressione zero).
6. **Prova dal vivo** (a mano, con Gilles): rizzo-pii acceso, un cloud vero con il testo di Mario Rossi inventato, e il controllo che verso il fornitore arrivino solo i segnaposto (stesso metodo `strace` delle prove del 23/10, o un proxy locale).

---

## 13. Domande aperte per Gilles

1. **Annona, quale strada** (§5.3): A sperimentale + letture, come propongo? Oppure aspettare C? La B è da escludere?
2. **Chiedere ad Akaion l'endpoint `place`** (strada C), dichiarando il ruolo di Technical Advisor?
3. **Il RAG sul cloud:** oggi è bloccato (`app.py:713`). Con rizzo-pii attivo lo vuoi **sbloccare** (pezzi di documento anonimizzati verso il cloud) o resta bloccato in ogni caso? Stessa domanda per l'upload dei file.
4. **Il dialogo privacy** (`ui/privacy_warning.py`): con rizzo-pii attivo, «Procedi comunque» diventa «Procedi con anonimizzazione»? Oppure resta com'è?
5. **«Remote host» con IP pubblico:** lo trattiamo come cloud (anonimizza) come propongo?
6. **Annona spento in modo `read`:** il cloud procede con il solo rizzo-pii (passo non registrato) o si blocca anche lui?
7. **Quali tag lasciare in chiaro** per default: nessuno, o `AMOUNT` (importi, spesso utili) e `DATE`?
8. **Configurazione:** va bene la sezione `hybrid:` in `security_settings.yaml`, o preferisci un file nuovo `hybrid_settings.yaml`?
9. **La UI:** un'icona o un badge sul messaggio («🛡️ 3 dati tolti prima dell'invio») e una vista «cosa ha visto il modello», come la sezione `egress` di Annona?
10. **Il NOTICE e la licenza** dell'Interface: chi controlla il punto AGPL della §9? E aggiungiamo il file `LICENSE` (MIT) che il README cita ma che manca?

---

## 14. Il posto nella roadmap

`ROADMAP.md` va oggi dalla 1.15.x (completate) alla 2.0.0 (pianificata: Semantic Layer, Docker, API REST). La 1.16.0 si mette **fra la 1.15.3 e la 2.0.0**, come versione minore (funzione nuova, opzionale, spenta per default, nessuna rottura):

- **v1.16.0 «ibrida»** — rizzo-pii nel guard, letture di Annona, strada A sperimentale;
- **v1.16.x** — strada C quando Akaion la offre; prova dal vivo documentata;
- **v2.0.0** — la sezione «Docker & Deployment» può includere rizzo-pii e Annona come servizi del `docker-compose` (con la nota AGPL per l'immagine di rizzo-pii).

ROADMAP, README e CHANGELOG si aggiornano dopo la lettura di questa SPEC.

---

## 15. Fonti

- rizzo-pii: `https://github.com/Rizzo-AI-Academy/rizzo-pii`, commit `9057eeff88bdf0444e5d3361cf0766b60c5b8a95` (22/10/2026): `README.md` §«The local HTTP API», `src/app/app.py`, `src/app/server_config.py`, `THIRD_PARTY_LICENSES.md`, `LICENSE`.
- Annona: `https://github.com/akaion-ai/annona`, tag `v0.1.3`, commit `beb943804a2c2d544a380cf69feb21d469667290` (21/09/2026): `runner/kernel_api.py`, `runner/local_api.py`, `runner/pairing.py`, `runner/placement/engine.py`, `runner/audit/ledger.py`, `runner/policy/classifier.py`, `runner/cli_perimeter.py`, `pyproject.toml`, `LICENSE`.
- Le prove sul portatile del 23/10/2026 (dossier nel vault: «Annona e rizzo-pii: le prove»).
