# Diagramma B — Superficie di rete e sicurezza (DeepAiUG Interface v1.15.2)

> Fallback Mermaid verificabile del file
> `DeepAiUG_Architettura-Sicurezza_Egress-v1_15_2.excalidraw`.
> Importabile direttamente nella canvas Excalidraw se il JSON avesse problemi.
> Mostra la **superficie di egress reale** (inclusi i punti non validati),
> non solo quella coperta dall'audit v1.15.2.

```mermaid
flowchart LR
    subgraph ORIG["ORIGINI EGRESS — applicazione"]
        E1["E1 · get_remote_ollama_models
requests.get base_url/api/tags
core/llm_client.py:75"]
        E2["E2 · OpenAILikeClient — chat
invoke / stream_invoke su base_url
core/llm_client.py:154-173"]
        E3["E3 · ClientFactory cloud fissi
non validato per progettazione
base_url hardcoded
core/llm_client.py:123-147 · config/constants.py:103-128"]
        E4["E4 · MediaWikiAdapter.connect
mwclient.Site — HTTP
rag/adapters/mediawiki.py:131-136"]
        E5["E5 · DokuWikiAdapter.connect
XML-RPC, credenziali nell'URL
rag/adapters/dokuwiki.py:116-129"]
        E6["E6 · SentenceTransformer — download modello
una tantum · non validato ·
nome modello non controllabile dall'utente
rag/embeddings.py:49"]
        K1["K1 · Chiavi API
env → secrets/*.txt — chmod 600
config/settings.py:280-333"]
    end

    subgraph CHOKE["VALIDATOR — choke point SSRF"]
        V1["V1 · classify_url
loopback / private+CGNAT / link_local / public / invalid
core/url_validator.py:33-119"]
        V2["V2 · is_blocked
blocca SOLO link_local → BlockedURLError
core/url_validator.py:122-139 · :28-30"]
        V3["V3 · Pre-check UI
app.py:702 · ui/sidebar/llm_config.py:233 ·
ui/sidebar/knowledge_base.py:671"]
    end

    subgraph DEST["DESTINAZIONI — esterno / non fidato"]
        X1["X1 · Ollama locale / LAN / Tailscale
loopback · private → permesso"]
        X2["X2 · Host pubblico arbitrario
public → permesso con warning"]
        X3["X3 · 169.254.169.254 — metadati cloud
link_local → BLOCCATO"]
        X6["X6 · Wiki MediaWiki / DokuWiki
URL configurato dall'utente"]
        X4["X4 · API cloud fisse
api.openai.com · api.anthropic.com ·
generativelanguage.googleapis.com"]
        X5["X5 · Hugging Face Hub
download modello embedding, poi cache locale"]
    end

    subgraph BANNER["ONESTÀ DELL'INTERFACCIA — banner privacy"]
        P1["P1 · Banner connessione — H3b
destinazione reale dell'URL
app.py:568-583"]
        P2["P2 · Banner privacy sezione KB
ui/sidebar/knowledge_base.py:77-92"]
        P3["P3 · Hard-block Cloud se KB / KB Chat attiva
ui/sidebar/llm_config.py:98-102 · app.py:708-709"]
        P4["P4 · Dialog privacy Local→Cloud con documenti
ui/privacy_warning.py:69-217 · app.py:517-526"]
    end

    E1 -->|"is_blocked ✅ core/llm_client.py:70"| V2
    E2 -->|"is_blocked ✅ core/llm_client.py:151 / :164
check alla creazione del client,
non a ogni invocazione"| V2
    E4 -->|"is_blocked ✅ rag/adapters/mediawiki.py:115"| V2
    E5 -->|"is_blocked ✅ rag/adapters/dokuwiki.py:107
prima dell'invio credenziali"| V2
    E3 -.->|"nessun check —
URL non controllabile dall'utente"| X4
    E6 -.->|"nessun check —
una tantum al primo avvio"| X5
    V3 -.->|"stessi esiti, feedback in UI"| V2
    V2 -->|"usa la classificazione
core/url_validator.py:136"| V1
    V2 -->|"loopback / private → permesso"| X1
    V2 -->|"public → permesso con warning"| X2
    V2 -->|"wiki: E4 / E5"| X6
    V2 -->|"link_local → BLOCCATO"| X3
    V1 -->|"categoria → banner"| P1
    V1 -->|"categoria → banner"| P2
    K1 -.->|api_key| E2
    K1 -.->|api_key| E3

    classDef mod fill:#ffd8a8,stroke:#e8590c,color:#5c2503
    classDef dati fill:#b2f2bb,stroke:#2f9e44,color:#12401e
    classDef sec fill:#ffc9c9,stroke:#c92a2a,color:#5c1010
    classDef ext fill:#dee2e6,stroke:#343a40,color:#1a1d20
    classDef ui fill:#a5d8ff,stroke:#1971c2,color:#0b3a5e
    classDef cred fill:#f1f3f5,stroke:#343a40,color:#1a1d20
    class E1,E2,E3 mod
    class E4,E5,E6 dati
    class X1,X2,X3,X4,X5,X6 ext
    class K1 cred
    class V1,V2,V3 sec
    class P1,P2,P3,P4 ui
```

## Legenda

| Layer | strokeColor | backgroundColor |
|---|---|---|
| Origini layer Modelli (E1-E3) | `#e8590c` | `#ffd8a8` |
| Origini layer Dati/adapter (E4-E6) | `#2f9e44` | `#b2f2bb` |
| Sicurezza / validator (V1-V3) | `#c92a2a` | `#ffc9c9` |
| Esterno / non fidato (X1-X6) | `#343a40` | `#dee2e6` |
| Credenziali locali (K1) — file 0600, non "esterno" | `#343a40` | `#f1f3f5` |
| Interfaccia / banner (P1-P4) | `#1971c2` | `#a5d8ff` |

- **Freccia continua** = egress che passa dal validator (`is_blocked`), con la riga
  del check in etichetta. **Freccia tratteggiata** = egress non validato (con
  motivazione) oppure dipendenza (chiavi API, pre-check UI).
- **V2 → V1**: `is_blocked` delega a `classify_url`
  (`core/url_validator.py:136`) — il choke point è unico perché la
  classificazione è centralizzata.
- **E2**: il check avviene **alla creazione del client**, non a ogni
  invocazione (`create_client`, `core/llm_client.py:151/:164`). Vale anche per
  il client socratico, creato via `get_socratic_client → create_client`
  (`app.py:296`).
- **E3** e **E6** sono egress **reali ma non validati**: E3 per progettazione
  (base_url hardcoded, il check H1c copre solo il provider "Custom"); E6 è il
  download una tantum del modello di embedding da Hugging Face Hub (nome
  modello hardcoded, override solo via env `DEEPAIUG_EMBEDDING_MODEL`).
- **P3 / P4** sono blocchi applicativi (privacy-first), senza archi di rete.
- Limiti noti del validator (rischio accettato, `SECURITY_AUDIT_RESOLUTION.md`):
  validazione al momento del check (no difesa DNS-rebinding/TOCTOU), risoluzione
  solo IPv4.
- `subprocess ollama list` (`core/llm_client.py:27`) è un processo locale, non
  egress di rete: escluso dal diagramma.
