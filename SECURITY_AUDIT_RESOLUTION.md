# Security Audit — Resolution Report (v1.15.2)

**Progetto:** DeepAiUG Interface (`datapizza-streamlit-interface`)
**Versione di rilascio dei fix:** v1.15.2
**Data:** 2026-07-13
**Ambito:** audit di sicurezza completo della codebase v1.15.1, condotto su ramo isolato con fix verificati funzionalmente e commit atomici.

> Questo documento è la sintesi **pubblica** dell'audit. Per responsible disclosure non contiene dettagli sfruttabili (file, righe, catene di attacco): descrive *cosa* è stato corretto e con quale approccio, non *come* i problemi fossero riproducibili. Il rapporto tecnico dettagliato è mantenuto privato.

---

## Sommario

L'audit ha analizzato **12 finding** (0 Critical, 4 High, 4 Medium, 4 Low) più 6 verifiche negative documentate. **Nessuna vulnerabilità di esecuzione codice remoto (RCE)**: la deserializzazione è JSON e `yaml.safe_load`, non c'è uso di `pickle`/`eval`/`exec`, e l'unico sottoprocesso è una chiamata fissa senza input utente né shell.

La classe di rischio prevalente riguardava l'**integrità della garanzia privacy-first** e l'**egress di rete** (SSRF), non l'esecuzione di codice. Coerentemente con l'identità del progetto, il lavoro si è concentrato sul rendere la protezione della privacy effettiva in ogni percorso e sull'onestà dell'interfaccia verso l'utente.

---

## Finding risolti in v1.15.2

### High

- **Estensione del blocco cloud alla memoria conversazionale.** Il blocco privacy-first verso i provider cloud copriva la Knowledge Base documentale ma non la memoria conversazionale usata come knowledge base. Il blocco ora copre entrambi i percorsi: le conversazioni locali indicizzate non vengono più inviate a un provider cloud.

- **Hardening SSRF su tutti i punti di egress di rete.** Introdotto un classificatore degli indirizzi (`core/url_validator.py`) che distingue host locali, di rete privata/LAN, VPN mesh (CGNAT/Tailscale) ed esterni. Gli endpoint di metadati cloud (link-local `169.254.0.0/16`) sono bloccati su tutti i punti in cui un URL controllabile dall'utente raggiunge la rete: recupero modelli remoti, creazione del client di chat, adapter MediaWiki e DokuWiki. Per gli adapter wiki il controllo precede l'invio delle credenziali.

- **Banner di privacy onesti.** Gli indicatori di connessione riflettono ora la **destinazione reale** dell'URL configurato (verificata dal classificatore) invece dell'etichetta della modalità selezionata. Un host esterno viene segnalato come tale; un host locale/LAN/Tailscale viene confermato come rete fidata. Corretto inoltre un testo di avviso che descriveva in modo impreciso il comportamento di invio dei dati.

### Medium

- **Renderer chat.** Disabilitato il rendering di HTML grezzo nel renderer dei messaggi (la formattazione Markdown, tabelle incluse, resta invariata) ed applicato escaping ai nomi dei file allegati.
- **Permessi delle chiavi API.** Le chiavi salvate su disco ora hanno permessi ristretti al solo proprietario.
- **Libreria PDF.** Migrazione dalla libreria PDF deprecata a una manutenuta attivamente, che elimina anche vulnerabilità di parsing note.
- **Dipendenze.** Aggiornati i pacchetti con CVE note e "pinnate" tutte le dipendenze a versioni esatte per build riproducibili.

---

## Rischi accettati / documentati

Alcuni finding sono stati valutati come **non applicabili** o **a rischio residuo accettabile** nel contesto d'uso tipico (deployment locale, spesso mono-utente), e documentati:

- **Limiti noti del classificatore URL:** il controllo è effettuato al momento della validazione (non c'è difesa completa contro DNS rebinding/TOCTOU) ed è basato su risoluzione IPv4. Adeguato allo scopo di bloccare gli endpoint di metadati; la difesa completa richiederebbe una validazione a livello di libreria di rete.
- **Accesso al filesystem in scenario locale:** la lettura di percorsi indicati dall'utente è per progettazione in un contesto mono-utente locale; diventa rilevante in scenari multi-utente, dove sono raccomandate misure a livello di deployment.
- **Finding Low:** valutati come falsi positivi o non sfruttabili allo stato attuale, monitorati come debito difensivo.

---

## Rimandato a v2.0

- **Allowlist di host fidati configurabile.** Utile in scenari multi-utente / con figura di *deployer*, dove ha senso architetturale un controllo di accesso esplicito agli host. Rinviata alla v2.0, che introduce un modello di deployment più strutturato.
- Difese avanzatte contro DNS rebinding e supporto IPv6 nel classificatore.

---

## Approccio metodologico

Ogni intervento ha seguito lo stesso ciclo: analisi del codice in sola lettura, decisione umana sul merito (rischio reale vs falso positivo, impatto sul funzionamento), modifica minima, revisione del diff, **test funzionale su host reali**, commit atomico e reversibile. Il lavoro è avvenuto su un ramo isolato; il ramo principale non è mai stato compromesso.

I dettagli tecnici riproducibili (file, righe, catene di sfruttamento) non sono inclusi in questo documento pubblico, in linea con una pratica di divulgazione responsabile.

---

## Segnalazioni di sicurezza

Per segnalare responsabilmente una vulnerabilità, vedere [SECURITY.md](SECURITY.md).
