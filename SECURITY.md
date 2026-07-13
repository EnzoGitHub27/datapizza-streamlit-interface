# Security Policy

DeepAiUG è uno strumento **privacy-first**: la sicurezza e la protezione dei dati degli utenti sono una priorità del progetto. Se pensi di aver individuato una vulnerabilità, ti chiediamo di segnalarla in modo responsabile.

## Versioni supportate

| Versione | Supporto sicurezza |
|----------|--------------------|
| 1.15.x   | ✅ |
| < 1.15   | ❌ (aggiorna all'ultima release) |

L'ultima release è sempre quella raccomandata: vedi la pagina [Releases](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/releases).

## Come segnalare una vulnerabilità

**Non aprire una issue pubblica** per problemi di sicurezza: una issue pubblica esporrebbe la vulnerabilità prima che sia disponibile una correzione.

Usa invece uno di questi canali privati:

1. **GitHub Security Advisory** (consigliato): dalla scheda *Security* del repository → *Report a vulnerability*. Questo canale è privato tra te e il maintainer.
2. In alternativa, contatta il maintainer del progetto attraverso i riferimenti indicati nel repository.

Nella segnalazione, se possibile, includi:
- una descrizione del problema e del suo impatto;
- i passi per riprodurlo;
- la versione di DeepAiUG interessata;
- eventuali proposte di mitigazione.

## Cosa aspettarti

- **Presa in carico**: cerchiamo di rispondere alle segnalazioni in tempi ragionevoli.
- **Divulgazione coordinata**: i dettagli tecnici di una vulnerabilità vengono resi pubblici **solo dopo** che è disponibile una correzione, per non esporre gli utenti. È la stessa pratica seguita per l'audit interno del progetto (vedi [SECURITY_AUDIT_RESOLUTION.md](SECURITY_AUDIT_RESOLUTION.md)).
- **Riconoscimento**: se lo desideri, il tuo contributo può essere accreditato nelle note di rilascio della correzione.

## Ambito

DeepAiUG è pensato principalmente per **esecuzione locale** (Ollama sulla propria macchina o su un host della rete locale). Molte protezioni presuppongono questo contesto d'uso. Se esponi DeepAiUG in scenari diversi (multi-utente, rete pubblica), alcune garanzie possono richiedere misure aggiuntive a livello di deployment: sei incoraggiato a segnalare anche i casi limite legati a questi scenari.

## Nota sui modelli e sui provider

DeepAiUG può connettersi a modelli locali e a provider cloud di terze parti. La sicurezza e le pratiche sui dati di **provider esterni** (OpenAI, Anthropic, Google, endpoint custom) sono responsabilità dei rispettivi fornitori. DeepAiUG si limita a rendere trasparente **dove** i dati vengono inviati e a impedire invii cloud non voluti quando sono attive protezioni privacy-first.

---

*Grazie per contribuire a mantenere DeepAiUG sicuro per tutta la community.*
