# Ollama, GPU e Embedding — Note pratiche per DeepAiUG

**Versione:** 1.0  
**Data:** 4 Aprile 2026  
**Autore:** Enzo "Gilles" Iodice  
**Contesto:** Osservazioni reali durante indicizzazione vault Obsidian (6921 chunks)
con DeepAiUG Interface v1.14.3 su laptop HP i7-8565U.

---

## Il problema osservato

Durante l'indicizzazione di un vault Obsidian di 847 file (6921 chunks totali),
il monitor di sistema mostrava:

- **CPU:** core al 50-100% di utilizzo (processo `streamlit`)
- **GPU:** 0% di utilizzo
- **`ollama ps`:** spesso vuoto o con modello non visibile

La domanda naturale: *perché la GPU è scarica mentre sta lavorando intensamente?*

---

## Spiegazione: parametri ≠ gigabyte

Prima di tutto, un chiarimento comune su Ollama e i nomi dei modelli.

Il numero dopo il nome del modello (es. `7B`, `3B`, `2B`) indica i **miliardi
di parametri**, non i gigabyte di memoria. La dimensione reale su disco/RAM
dipende dalla **quantizzazione** applicata da Ollama (default: Q4_K_M).

Tabella orientativa:

| Parametri | Quantizzazione | Peso approssimativo |
|-----------|---------------|-------------------|
| 1.5B | Q4 | ~1.0 GB |
| 3B | Q4 | ~2.0 GB |
| 7B | Q4 | ~4.5 GB |
| 14B | Q4 | ~8.5 GB |
| 32B | Q4 | ~18.0 GB |

Esempio pratico: un modello nominato "2B" può pesare ~1.5GB, ma un "7B"
pesa ~4.5GB — tre volte tanto. Verificare sempre con `ollama list` per vedere
il peso reale di ogni modello installato.

---

## Perché Ollama usa la CPU per gli embedding

### Causa 1 — GPU integrata non supportata

Il laptop HP i7-8565U monta una **Intel UHD 620** (GPU integrata).
Ollama su Linux non supporta GPU Intel integrate senza configurazione
specifica OpenCL/oneAPI — che non è il percorso standard e richiede
setup aggiuntivo non banale.

Risultato: Ollama fa **fallback automatico su CPU** per tutti i modelli,
incluso `nomic-embed-text` usato per gli embedding.

### Causa 2 — VRAM insufficiente o già occupata

Se la VRAM disponibile è inferiore al peso del modello, Ollama non lo
carica in GPU. Con 4GB di VRAM condivisa tra sistema grafico e applicazioni,
il margine utile è circa 3.0-3.5GB.

Se un modello LLM è già caricato (es. Qwen 7B a ~4.2GB), non rimane
spazio per caricare anche `nomic-embed-text` (~274MB) in modo efficiente.

### Causa 3 — Ciclo load/unload tra batch

Durante l'indicizzazione batch, Ollama:
1. Carica `nomic-embed-text` in memoria
2. Genera gli embedding per il batch corrente
3. **Scarica il modello** per liberare memoria
4. Ricarica per il batch successivo

Questo spiega perché `ollama ps` appare spesso vuoto durante
l'indicizzazione — lo si vede nei momenti tra un batch e l'altro.

---

## Come verificare cosa sta succedendo

### Controllare i modelli attivi in tempo reale
```bash
ollama ps
```
Output con modello in GPU:
```
NAME                ID              SIZE      PROCESSOR    UNTIL
qwen2.5:7b          abc123def456    4.7 GB    100% GPU     4 minutes from now
```
Output con modello in CPU:
```
NAME                ID              SIZE      PROCESSOR    UNTIL
nomic-embed-text    xyz789          274 MB    100% CPU     4 minutes from now
```

### Verificare modelli installati e peso reale
```bash
ollama list
```

### Monitorare CPU e GPU in tempo reale
```bash
htop                  # CPU e processi
intel_gpu_top         # GPU Intel integrata
nvidia-smi -l 1       # GPU NVIDIA
rocm-smi              # GPU AMD (ROCm)
```

---

## Impatto su DeepAiUG

### Indicizzazione vault (operazione one-shot)
Lenta ma accettabile — l'utente avvia e aspetta. Non è real-time.
Per vault di ~850 file e ~7000 chunks, il tempo atteso su CPU è
nell'ordine dei minuti, non delle ore.

### Risposte LLM (operazione real-time)
I modelli di generazione sono **separati** da `nomic-embed-text`.
Se il modello LLM gira in GPU, le risposte sono veloci indipendentemente
da dove girano gli embedding. Il problema GPU non impatta l'esperienza
conversazionale dell'utente.

---

## Soluzioni e raccomandazioni

### Per laptop con GPU integrata (situazione attuale)
Accettare il fallback su CPU per gli embedding. Scegliere modelli LLM
leggeri che entrano nella VRAM disponibile:

| Modello | Peso | Adatto a 4GB VRAM |
|---------|------|-------------------|
| Qwen 2.5 1.5B | ~1.0 GB | ✅ ottimo |
| Qwen 2.5 3B | ~2.0 GB | ✅ buon compromesso |
| Phi-3 Mini 3.8B | ~2.3 GB | ✅ ottimo per ragionamento |
| Llama 3.2 3B | ~2.0 GB | ✅ ok |
| qualsiasi 7B | ~4.5 GB | ❌ va in CPU o split |

### Per workstation con GPU dedicata (Proxmox + Quadro P6000)
Il P6000 con 24GB VRAM gestisce senza problemi sia embedding che
modelli grandi in parallelo. Per vault di grandi dimensioni, preferire
l'indicizzazione sul server Proxmox via API Ollama remota.

### Architettura consigliata per v2.0

```
Laptop (sviluppo + modelli leggeri)
    ↕ API Ollama remota
Proxmox P6000 (embedding pesanti + modelli grandi)
    ↕
Jetson Nano "Dopey" (edge deployment, modelli tiny)
```

L'indicizzazione di vault grandi viene delegata al Proxmox.
Il laptop riceve i vettori già pronti senza stress hardware.

---

## Note su nomic-embed-text

Modello di embedding usato da DeepAiUG per ChromaDB:

- Dimensione: ~274 MB (molto leggero)
- Dimensione vettori: 768 dimensioni
- Ottimo rapporto qualità/peso per testo in italiano e inglese
- Contesto massimo: 8192 token

Anche se piccolo, se la GPU non è supportata il fallback su CPU
è automatico e silenzioso — nessun errore, solo più lento.

---

## Riferimenti

- [Ollama GPU support](https://github.com/ollama/ollama/blob/main/docs/gpu.md)
- [nomic-embed-text su Ollama](https://ollama.com/library/nomic-embed-text)
- [DeepAiUG Interface](https://github.com/EnzoGitHub27/datapizza-streamlit-interface)

---

*Documento generato dall'esperienza diretta durante lo sviluppo di DeepAiUG Interface v1.14.3.*
*Contributi e correzioni benvenuti — open source, come sempre.*
