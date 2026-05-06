---
versione: 1.14.4
data: 2026-05-06
tipo: spec
ciclo: v1.x maintenance
tags:
  - deepaiug
  - release
  - ux
  - sidebar
  - knowledge-base
  - installer
  - icons
---

# SPEC — v1.14.4: Knowledge Base ritrovata + identità visiva nei launcher

## Contesto

**Repository:** `EnzoGitHub27/datapizza-streamlit-interface`
**Branch di partenza:** `dev`
**Versione precedente:** `v1.14.3` (scroll fix + typing indicator)
**Versione target:** `v1.14.4`
**Natura del rilascio:** patch UX in maintenance mode v1.x

> [!info] Maintenance mode v1.x
> v1.14.3 era stato dichiarato "ultimo rilascio del ciclo v1.x". v1.14.4 entra come patch correttiva *dentro* la maintenance mode — nessuna nuova feature, solo discoverability e identità visiva.

---

## Obiettivo

Due interventi indipendenti, accomunati dalla stessa giornata di lavoro:

1. **Riportare visibilità** alla sezione Knowledge Base (Wiki + Vault) nella sidebar — invisibile dalla v1.12.0 e segnalata dall'utente come "non la vedo più rispetto alle versioni precedenti".
2. **Sostituire l'icona di default del sistema operativo** nei collegamenti creati dagli installer con il logo DeepAiUG.

---

## Intervento 1 — Fix visibilità Knowledge Base in sidebar

### Problema

Dalla v1.12.0 (architettura sidebar rivista), la chiamata `render_knowledge_base_config(...)` era stata spostata **dentro l'expander `⚙️ Configurazione`**, configurato con `expanded=False`. La sezione esisteva ancora, ma:

- l'utente doveva aprire l'expander per scoprirla
- una volta aperto, la sezione si attivava solo spuntando `🔍 Usa Knowledge Base` (off di default)
- nessun indizio visivo segnalava la presenza di MediaWiki, DokuWiki, Obsidian Vault, ecc.

Risultato: una feature centrale del prodotto era diventata **invisibile a colpo d'occhio**.

### Analisi UX — perché *non* è un problema di click

Sembrava un problema di "troppi click". Era invece un problema di **discoverability**: l'utente non sapeva che la feature esistesse. Soluzioni considerate:

| Opzione | Cosa fa | Pro | Contro |
|---|---|---|---|
| **1.** Expander dedicato `📚 Knowledge Base` aperto di default, toggle resta | Ripristina visibilità mantenendo gate privacy | Off-by-default sicuro su Cloud, stato leggibile, zero regressioni | Resta 1 click per attivare |
| **2.** Rimuove il toggle, sempre attiva | Zero click | Riapre questione privacy/Cloud, sempre rendering | Stato implicito, regressioni su `use_knowledge_base` (usato in più punti del codice) |

**Decisione: Opzione 1.** Il toggle non era il problema — la *posizione* lo era. L'Opzione 2 risolveva un non-problema (un click) introducendo rischi reali.

### Implementazione

**File 1 — `app.py`** ([linee 312–325](../app.py#L312-L325))

Estratta la chiamata a `render_knowledge_base_config` dall'expander Configurazione, e creato un nuovo expander dedicato `📚 Knowledge Base (Wiki / Vault)` con `expanded=True`:

```python
# 1. ⚙️ Configurazione LLM (chiusa di default)
config_expander = st.sidebar.expander("⚙️ Configurazione", expanded=False)
(
    connection_type, provider, api_key, model, base_url,
    system_prompt, temperature, max_messages,
) = render_llm_config(container=config_expander)

# 1b. 📚 Knowledge Base — Wiki / Vault (aperta di default)
kb_expander = st.sidebar.expander("📚 Knowledge Base (Wiki / Vault)", expanded=True)
render_knowledge_base_config(connection_type, container=kb_expander)
```

**File 2 — `ui/sidebar/knowledge_base.py`** ([linee 62–67](../ui/sidebar/knowledge_base.py#L62-L67))

Quando il toggle è OFF, mostrare una caption che elenchi le sorgenti disponibili (discoverability anche senza attivare la feature):

```python
if not use_kb:
    _container.caption(
        "Disponibili: 📁 Cartella locale · 🌐 MediaWiki · 📖 DokuWiki · "
        "🧠 Obsidian Vault · …  Attiva per configurare."
    )
    return
```

### Cosa NON è stato toccato

- **Logica di routing** wiki/vault: invariata
- **Checkbox `🔍 Usa Knowledge Base`**: invariato — resta come gate esplicito di attivazione e gate privacy su Cloud provider
- **Avviso privacy** "Cloud provider bloccato": invariato

> [!success] Principio applicato
> Don't fix what isn't broken. Il toggle e la logica di gate funzionavano. Solo la posizione era il problema.

---

## Intervento 2 — Icona personalizzata DeepAiUG nei launcher installer

### Problema

Le scorciatoie/launcher creati dagli installer (`INSTALLA_DeepAiUG.bat`, `installa_deepaiug_linux.sh`, `installa_deepaiug_mac.sh`) usavano l'**icona di default del sistema operativo** (icona generica file batch / .desktop / .command). Identità visiva debole e zero brand recognition.

### Vincolo tecnico per OS

| OS | Target shortcut | Formato icona accettato |
|---|---|---|
| 🐧 Linux | `.desktop` in `~/.local/share/applications/` | PNG, SVG ✅ |
| 🪟 Windows | `.lnk` via VBScript `WScript.Shell` | `.ico` (o `.exe`/`.dll`) — **non accetta PNG** |
| 🍎 macOS | `.command` (script bash) | **Nessuna API** per script `.command` — serve un `.app` bundle |

### Decisioni

- **Asset**: `deepaiug-logo.png` + `deepaiug-logo.ico` committati in root del repo. Vengono inclusi automaticamente nello zip scaricato dagli installer e finiscono in `$DEST` dopo l'estrazione.
- **Mac**: poiché non si può dare icona a un `.command`, creato un wrapper `.app` bundle accanto al `.command` esistente. Il `.command` resta come fallback CLI.

### Implementazione

#### Linux — 1 riga nel `.desktop`

[installa_deepaiug_linux.sh:457](../installer/installa_deepaiug_linux.sh#L457):

```diff
 [Desktop Entry]
 Name=DeepAiUG
 Comment=AI locale privacy-first
 Exec=bash $HOME/DeepAiUG/avvia_deepaiug.sh
+Icon=$HOME/DeepAiUG/deepaiug-logo.png
 Terminal=true
 Type=Application
 Categories=Utility;
```

#### Windows — `IconLocation` nel VBScript

[INSTALLA_DeepAiUG.bat:510](../installer/INSTALLA_DeepAiUG.bat#L510):

```diff
     echo Set oLink = WshShell.CreateShortcut^(strDesktop ^& "\DeepAiUG.lnk"^)
     echo oLink.TargetPath = "!DEST!\DeepAiUG.bat"
     echo oLink.WorkingDirectory = "!DEST!"
     echo oLink.Description = "Avvia DeepAiUG - AI locale privacy-first"
+    echo If CreateObject^("Scripting.FileSystemObject"^).FileExists^("!DEST!\deepaiug-logo.ico"^) Then oLink.IconLocation = "!DEST!\deepaiug-logo.ico, 0"
     echo oLink.Save
```

> [!note] Check di esistenza file
> L'`If FileExists` rende la modifica difensiva: se il `.ico` viene rimosso o rinominato, lo shortcut viene comunque creato (senza icona custom) anziché fallire.

#### macOS — `.app` wrapper con `.icns` generato al volo

[installa_deepaiug_mac.sh:496–557](../installer/installa_deepaiug_mac.sh#L496-L557):

Logica:

1. **Generazione `.icns`** dal PNG via `sips` + `iconutil` (entrambi parte del sistema base macOS, no Xcode CLT richiesto):
   ```bash
   for s in 16 32 128 256 512; do
       sips -z $s $s "$LOGO_PNG" --out "$ICONSET_TMP/icon_${s}x${s}.png"
       sips -z $((s*2)) $((s*2)) "$LOGO_PNG" --out "$ICONSET_TMP/icon_${s}x${s}@2x.png"
   done
   iconutil -c icns "$ICONSET_TMP" -o ".../Resources/deepaiug-logo.icns"
   ```

2. **Struttura `.app`**:
   ```
   DeepAiUG.app/
   └── Contents/
       ├── Info.plist          (CFBundleIconFile = deepaiug-logo.icns)
       ├── MacOS/
       │   └── DeepAiUG        (script bash che apre Terminal e lancia il .command)
       └── Resources/
           └── deepaiug-logo.icns
   ```

3. **Eseguibile interno** (`Contents/MacOS/DeepAiUG`): script bash che usa `osascript` per aprire `Terminal.app` e lanciare il `.command` esistente. Mantiene tutta la logica di avvio già esistente, aggiunge solo il livello di "vestizione" visiva.

4. **Best-effort**: se `sips` o `iconutil` falliscono, la creazione del `.app` viene saltata silenziosamente — il `.command` resta sempre disponibile come fallback. Niente errori bloccanti durante l'installazione.

5. **Rimozione attributo quarantine** (`xattr -dr com.apple.quarantine`) per evitare il pop-up Gatekeeper su file generati localmente.

#### Aggiornamento documentazione installer

[INIZIA-QUI.txt:28-29](../installer/INIZIA-QUI.txt#L28-L29) ora cita prima `DeepAiUG.app` (con icona) e poi `DeepAiUG.command` come fallback.

---

## Aggiornamenti versione e documentazione

| File | Modifica |
|---|---|
| `config/constants.py` | `VERSION = "1.14.4"`, descrizione aggiornata |
| `CHANGELOG.md` | Nuova sezione `[1.14.4] — 2026-05-06` con dettaglio fix |
| `README.md` | Badge versione, sezione "🩹 Novità v1.14.4", header architettura, riga in tabella history |
| `ROADMAP.md` | Riga `v1.14.4` nel diagramma + sezione "Completate" in cima |

---

## Workflow Git

Stesso pattern dei rilasci precedenti del ciclo v1.14.x.

### Commit 1 — Fix KB sidebar (su `dev`)

```bash
git checkout dev
# ...modifiche a app.py, ui/sidebar/knowledge_base.py, config/constants.py,
# CHANGELOG.md, README.md, ROADMAP.md...
git add app.py ui/sidebar/knowledge_base.py config/constants.py \
        CHANGELOG.md README.md ROADMAP.md
git commit -m "fix: ripristina visibilità sezione Knowledge Base (Wiki / Vault) in sidebar (v1.14.4)"
git push origin dev
```

### Merge su `main` + tag

```bash
git checkout main
git merge dev --no-ff -m "merge: dev → main (v1.14.4) — fix visibilità Knowledge Base sidebar"
git tag v1.14.4
git push origin main --tags
git checkout dev
```

### Commit 2 — Icone installer (su `dev`, dopo il tag)

```bash
git add installer/*.sh installer/*.bat installer/INIZIA-QUI.txt \
        deepaiug-logo.png deepaiug-logo.ico
git commit -m "feat(installer): icona personalizzata DeepAiUG su Linux, Windows e Mac"
git push origin dev
```

### Merge installer su `main` + force-update tag

Il tag `v1.14.4` è stato spostato in avanti per includere anche le icone installer (era stato pushato pochi minuti prima, repo a singolo contributor — rischio "altri hanno già pullato" praticamente nullo):

```bash
git checkout main
git merge dev --no-ff -m "merge: installer icons (Linux/Windows/Mac launcher con icona personalizzata)"
git push origin main

git tag -f v1.14.4 -m "v1.14.4 — KB sidebar visibility fix + installer icons"
git push origin v1.14.4 --force

git checkout dev
```

> [!warning] Force-update tag
> In contesti multi-contributor evitare. Qui è stato accettato perché: (a) tag pushato pochissimo tempo prima, (b) repo a singolo contributor, (c) la Release GitHub doveva descrivere accuratamente il contenuto del tag.

---

## Release GitHub v1.14.4

Promossa come **Latest** al posto di v1.14.3 tramite la web UI di GitHub (no `gh` CLI installato sul sistema):

1. https://github.com/EnzoGitHub27/datapizza-streamlit-interface/releases
2. Edit / Create release per tag `v1.14.4`
3. Title: `v1.14.4 — Knowledge Base ritrovata + identità visiva nei launcher`
4. Body: descrizione strutturata (vedi sezione Release notes sotto)
5. Spuntare **"Set as the latest release"** ✅
6. Publish

### Estratto release notes

> 🩹 **Fix — Knowledge Base ritrovata nella sidebar**
> Dalla v1.12.0 la sezione di configurazione delle sorgenti Wiki + Vault era finita dentro l'expander "⚙️ Configurazione" chiuso di default, diventando di fatto invisibile. In questa release torna subito visibile e discoverable.
>
> 🎨 **Identità visiva — Nuova icona nei launcher creati dall'installer**
> Le scorciatoie generate dagli installer adesso mostrano il logo DeepAiUG al posto dell'icona di default del sistema operativo (Linux: PNG nel `.desktop`; Windows: `.ico` nel `.lnk`; macOS: nuovo wrapper `.app` con `.icns` generato al volo).

---

## Lezioni / decisioni di design

### Discoverability ≠ click count

Il problema "non vedo più la wiki" sembrava un problema di troppi click. Era un problema di **assenza di indizio visivo**. Aggiungere una caption con l'elenco sorgenti quando il toggle è OFF risolve la discoverability senza alterare il flusso di attivazione (gate privacy + esplicitezza dello stato).

### Spostare un blocco UI > riprogettare

L'intervento più piccolo possibile (creare un secondo expander e passarci il container) era anche il più sicuro. Ogni alternativa più "pulita" (eliminare il toggle, ricomporre la sidebar) introduceva rischi reali su gate privacy e flag `use_knowledge_base` letto in più punti.

### Mac `.app` wrapper come pattern

Per dare icona a uno script `.command` su macOS senza dipendere da Xcode CLT, il pattern `.app` bundle + `Info.plist` + script che apre Terminal via `osascript` è la via più portabile. Tool richiesti (`sips`, `iconutil`) sono parte del sistema base macOS.

### Force-update tag: accettabile a determinate condizioni

Spostare un tag già pushato è generalmente da evitare, ma in repo personali appena pushati e con singolo contributor è accettabile per mantenere coerenza tra contenuto del tag e descrizione della Release.

### Maintenance mode non significa "niente patch"

v1.14.3 era stato annunciato come ultimo rilascio del ciclo. Una patch UX di discoverability + un miglioramento di identità visiva non rompono il principio: nessuna nuova feature, solo correzioni e affinamenti che riducono frizione utente.

---

## Riferimenti incrociati

- [[SPEC_v1.14.3_scroll_fix_animated_indicator]] — patch precedente del ciclo
- [[SPEC_v1.14.2_vault_used_flag]] — feature vault correlata
- [[SPEC_v1.14.x_chat_kb]] — spec ciclo Chat KB
- [[manuale_utente_kb_chat]] — guida utente Knowledge Base

---

*Documento generato durante la sessione di lavoro del 2026-05-06.*
