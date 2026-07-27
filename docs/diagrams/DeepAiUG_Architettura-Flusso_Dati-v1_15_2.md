# Diagramma A — Flusso dati (DeepAiUG Interface v1.15.2)

> Fallback Mermaid verificabile del file
> `DeepAiUG_Architettura-Flusso_Dati-v1_15_2.excalidraw`.
> Importabile direttamente nella canvas Excalidraw se il JSON avesse problemi.
> Ogni nodo è tracciabile a `file:riga` (inventario Fase 1, v1.15.2).

```mermaid
flowchart TD
    subgraph UI["INTERFACCIA — Streamlit"]
        A1["A1 · Input utente + allegati
app.py:662-689 · ui/file_upload.py:178"]
        A2["A2 · Submit + validazioni
modello, API key, Cloud+KB, is_blocked
app.py:695-711"]
        A3["A3 · Rendering risposta streaming
app.py:830-856"]
        A4["A4 · Bottoni socratici + Mappa Sessione
ui/socratic/buttons.py:335 · ui/socratic/session_map.py:258"]
    end

    subgraph ORCH["ORCHESTRAZIONE — datapizza-ai"]
        B1["B1 · Arricchimento prompt con file
ui/file_upload.py:285"]
        B2["B2 · Retrieval wiki KB
get_context_for_prompt
rag/manager.py:141-178"]
        B3["B3 · Retrieval chat KB
boost ×1.0 / ×1.15 / ×1.30
core/kb_chat_indexer.py:348-415 · :34"]
        B4["B4 · Merge contesti + prompt inline
app.py:764-778 · app.py:798-823"]
        B5["B5 · create_client — factory
core/llm_client.py:94-173"]
        B6["B6 · Auto-save conversazione
app.py:235-236 · core/persistence.py:68-126"]
    end

    subgraph DATI["DATI — ChromaDB"]
        C1["C1 · Collection wiki_knowledge_base
persist: knowledge_base/vectorstore
rag/vector_store.py:18,42"]
        C2["C2 · Collection deepaiug_chat_kb
persist: knowledge_base/chat_kb_vectorstore
core/kb_chat_indexer.py:26-27"]
        C3["C3 · Embedding multilingua e5-small
prefix query: / passage:
rag/embeddings.py:22-67"]
        C4["C4 · Indicizzazione wiki/vault
adapter → TextChunker → clear() + add_chunks
re-index SEMPRE completa
rag/manager.py:60-122 · :108"]
        C5["C5 · Indicizzazione chat flaggate
reindex_all_chat_kb → _chunk_text
core/kb_chat_indexer.py:418-476 · :107"]
        C6["C6 · conversations/conv_*.json
core/persistence.py:55-65"]
    end

    S1["S1 · Sorgenti esterne
vault Obsidian / MediaWiki / DokuWiki
rag/vault.py:14-46 · rag/adapters/*"]

    subgraph MOD["MODELLI — Ollama / Cloud"]
        D1["D1 · OpenAILikeClient
Ollama locale / remoto / custom
core/llm_client.py:154-173"]
        D2["D2 · ClientFactory
cloud fissi OpenAI / Anthropic / Google
core/llm_client.py:123-147"]
        D3["D3 · stream_invoke / invoke
app.py:840"]
    end

    A1 -->|submit| A2
    A2 -->|"testo + file"| B1
    B1 --> B4
    A2 -->|"se use_knowledge_base"| B2
    A2 -->|"se use_chat_kb"| B3
    B2 -->|query| C1
    B3 -->|query| C2
    C3 -.->|"embedding function"| C1
    C3 -.->|"embedding function"| C2
    C1 -->|"top-k chunk"| B4
    C2 -->|"chunk boosted"| B4
    B4 -->|"prompt completo"| B5
    B5 --> D1
    B5 --> D2
    D1 --> D3
    D2 --> D3
    D3 -->|"token streaming"| A3
    A3 -->|add_message| B6
    B6 -->|JSON| C6
    C6 -->|"chat flaggate — bottone Aggiorna KB Chat, app.py:393-404"| C5
    C5 -->|"chunk + embedding"| C2
    C4 -->|"chunk + embedding"| C1
    S1 -->|"scan + fetch"| C4
    A4 -->|"client socratico dedicato
get_socratic_client → create_client, app.py:287-306"| B5

    classDef ui fill:#a5d8ff,stroke:#1971c2,color:#0b3a5e
    classDef orch fill:#d0bfff,stroke:#5f3dc4,color:#2a1b66
    classDef dati fill:#b2f2bb,stroke:#2f9e44,color:#12401e
    classDef mod fill:#ffd8a8,stroke:#e8590c,color:#5c2503
    classDef ext fill:#dee2e6,stroke:#343a40,color:#1a1d20
    class A1,A2,A3,A4 ui
    class B1,B2,B3,B4,B5,B6 orch
    class C1,C2,C3,C4,C5,C6 dati
    class D1,D2,D3 mod
    class S1 ext
```

## Legenda

| Layer | strokeColor | backgroundColor |
|---|---|---|
| Interfaccia (Streamlit) | `#1971c2` | `#a5d8ff` |
| Orchestrazione | `#5f3dc4` | `#d0bfff` |
| Dati / ChromaDB | `#2f9e44` | `#b2f2bb` |
| Modelli / Ollama | `#e8590c` | `#ffd8a8` |
| Esterno / non fidato (S1) | `#343a40` | `#dee2e6` |

- **Freccia continua** = flusso della richiesta/dati. **Freccia tratteggiata** = dipendenza/uso.
- **S1** è lo stesso oggetto del nodo X6 del Diagramma B (sorgenti wiki/vault),
  visto dall'angolazione del flusso dati anziché della superficie di rete.
- `build_rag_prompt` (`core/conversation.py:103-143`) esiste ma **non è raggiunta** dal
  percorso di submit: il prompt è costruito inline in `app.py:798-823` (nodo B4).
- L'indicizzazione wiki/vault è **sempre completa**: `vector_store.clear()` in
  `rag/manager.py:108` precede `add_chunks`. `get_files_to_update`
  (`rag/vault.py:67-75`) è definita ma senza call site.
- Il boost per rilevanza (×1.0/×1.15/×1.30, `core/kb_chat_indexer.py:34`) esiste
  **solo** sulla collection chat, non sulla wiki KB.
- Il client socratico (A4) passa da `create_client` (`app.py:296`) e quindi dal
  check `is_blocked` (`core/llm_client.py:151/:164`): stesso choke point della chat.
- C6 → C5 → C2 chiude il ciclo epistemico: le conversazioni salvate e flaggate
  rientrano nel retrieval come knowledge base.
