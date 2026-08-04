# ADR-0001 — Invio immagini al modello via MediaBlock Datapizza (vision local-only)

**Stato:** Accettato · **Data:** 2026-08-04 · **Versione riferimento:** 1.15.2 · **Branch:** feat/vision-local
Collaudato il 2026-08-04 con moondream/llava: vision, non-vision, cloud-block e reload chat verificati.

## Contesto

In `app.py:826-827` c'è il TODO Vision: le immagini allegate vengono già preparate (`enrich_prompt_with_files` ritorna `images_data`, gated da `can_use_images = pending_has_images and is_vision_model(model)`, `app.py:721-726`) ma mai inviate al modello — `client.stream_invoke(full_prompt)` riceve solo una stringa (`app.py:840`). Il client Local/Remote è `OpenAILikeClient` di Datapizza (`core/llm_client.py:167-173`), la cui firma `stream_invoke(input: str | list[Block], ...)` accetta nativamente una lista di Block; l'SDK installato (datapizza-ai 0.0.9, clients-openai-like 0.0.11) fornisce `MediaBlock`/`Media` con `source_type="base64"`.

## Decisione

Quando `can_use_images` è vero e la connessione è Local/Remote (Ollama), passare a `stream_invoke` una lista `[TextBlock(full_prompt), MediaBlock(...), ...]` — un MediaBlock per immagine, costruito dal base64 già presente in `images_data` — invece della sola stringa. Nessuna modifica al client esistente. Le immagini restano **effimere** (mai persistite, mai in KB/vault) e la funzionalità è **local-only**: sui provider cloud l'upload immagini resta bloccato, coerente con la policy egress v1.15.2.

## Conseguenze

- I modelli vision locali (es. llava, moondream) ricevono davvero le immagini; il resto del flusso (RAG, history, streaming) è invariato perché il ramo testuale continua a passare una stringa.
- Nessuna nuova dipendenza: si usano tipi già installati (`datapizza.type.TextBlock/MediaBlock/Media`).
- La superficie egress non cambia: i byte immagine viaggiano solo verso l'endpoint Ollama locale/remoto già consentito dal validatore SSRF.

> **TODO separato (fuori da questo lavoro Vision):** allineare il pin datapizza tra `pyproject.toml` (`^0.0.8`) e `requirements.txt` (`==0.0.11`) in un commit dedicato.

## Alternative scartate

- **Codificare l'immagine nel prompt testuale (base64 inline):** i modelli non la interpretano come immagine; esplode il conteggio token.
- **Chiamare l'API OpenAI-vision a mano (bypass Datapizza):** duplica il client, perde streaming/tracing uniformi e il gating centralizzato.
- **Abilitare vision anche su cloud:** contraria alla policy di blocco upload verso cloud (v1.15.2); scartata per design, non per limite tecnico.

## Punti da collaudare

1. Modello vision locale (llava o moondream via Ollama): immagine singola + prompt → risposta che descrive l'immagine.
2. Più immagini nello stesso messaggio; immagine + RAG attivo (il system prompt arricchito resta nel TextBlock).
3. Modello non-vision: `can_use_images` falso → percorso stringa invariato (regressione zero).
4. Cloud provider con immagine allegata → blocco confermato, nessun byte immagine in uscita.
5. Streaming: i chunk arrivano e il typing indicator si comporta come oggi.
