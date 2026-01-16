# 🚀 Release v1.5.1 - Workflow Completo

## ✅ Preparazione (COMPLETATA)

- [x] Aggiornato VERSION in `config/constants.py` → `1.5.1`
- [x] Aggiornato `CHANGELOG.md` con entry v1.5.1
- [x] Aggiornato `README.md` con badge versione + wiki test
- [x] Aggiornato `requirements.txt` header versione
- [x] Aggiunte 4 wiki pubbliche in `wiki_sources.yaml`
- [x] Creati script test: `test_wiki.py` e `test_all_wikis.py`
- [x] Commit creato su branch `dev`: `ec16ea6`

---

## 📋 Workflow Release GitHub

### Passo 1: Push branch dev su GitHub

```bash
# Assicurati di essere su dev
git branch

# Push del commit su origin/dev
git push origin dev
```

**Verifica**: Vai su GitHub → branch `dev` → verifica che il commit sia presente

---

### Passo 2: Merge dev → main

```bash
# Passa al branch main
git checkout main

# Pull per sicurezza (se collabori con altri)
git pull origin main

# Merge da dev (fast-forward se possibile)
git merge dev

# Verifica che tutto sia ok
git log --oneline -5
```

---

### Passo 3: Crea Tag Versione

```bash
# Crea tag annotato per v1.5.1
git tag -a v1.5.1 -m "Release v1.5.1 - Wiki Bugfix + Test Sources

## 🐛 Bug Fix
- FIXED: Wiki non funzionavano per dipendenze mancanti
- Root cause: mwclient e dokuwiki non installati
- Soluzione documentata in README

## ✨ Features
- 4 wiki pubbliche pronte per test:
  * Wikipedia IT/EN (AI topics)
  * Wikivoyage IT (travel guides)
  * Wikibooks IT (manuals)

## 🔧 Improvements
- Script di test: test_wiki.py, test_all_wikis.py
- Documentazione migliorata
- Setup venv chiarito

## 📦 Changes
- config/constants.py: VERSION → 1.5.1
- wiki_sources.yaml: 4 public test wikis
- README.md: Test wiki section
- CHANGELOG.md: v1.5.1 entry
"

# Verifica tag creato
git tag -l -n9 v1.5.1
```

---

### Passo 4: Push Main + Tag su GitHub

```bash
# Push branch main
git push origin main

# Push del tag specifico
git push origin v1.5.1

# OPPURE: Push di tutti i tag
# git push origin --tags
```

**Verifica**:
- GitHub → branch `main` → commit presente
- GitHub → Tags → `v1.5.1` presente

---

### Passo 5: Crea Release su GitHub (Web UI)

1. Vai su: `https://github.com/EnzoGitHub27/datapizza-streamlit-interface/releases`
2. Clicca **"Draft a new release"**
3. Compila:

```
Tag version: v1.5.1
Release title: v1.5.1 - Wiki Bugfix + Test Sources

Descrizione:
```

```markdown
## 🐛 Critical Bugfix

**FIXED**: MediaWiki e DokuWiki adapters non funzionavano

### Problema
I pacchetti `mwclient` e `dokuwiki` non erano installati nel virtual environment, causando il mancato funzionamento delle wiki.

### Soluzione
- Documentato correttamente il setup con venv
- Aggiunte 4 wiki pubbliche pronte per test immediato
- Creati script di test per validare connessioni

---

## ✨ Novità

### 🧪 Wiki Pubbliche di Test

Ora puoi provare subito il sistema RAG con wiki pubbliche preconfigurate:

| Wiki | Categoria | Pagine |
|------|-----------|--------|
| 🌍 Wikipedia IT | Intelligenza Artificiale | 30 |
| 🌎 Wikipedia EN | Artificial Intelligence | 20 |
| ✈️ Wikivoyage IT | Guide viaggio Italia | 15 |
| 📚 Wikibooks IT | Manuali Informatica | 20 |

**Come usare:**
1. Attiva Knowledge Base nella sidebar
2. Seleziona una wiki (es: Wikipedia IT)
3. Clicca "Sincronizza"
4. Fai domande sui contenuti!

### 🧪 Script di Test

```bash
# Test veloce Wikipedia
python test_wiki.py

# Test tutte le wiki configurate
python test_all_wikis.py
```

---

## 🔧 Miglioramenti

- Cambiato `default_source` da wiki inesistente a `wikipedia_it`
- Migliorata documentazione setup venv in README
- Aggiunti test automatici per validare connessioni wiki

---

## 📦 File Modificati

- `config/constants.py`: VERSION → 1.5.1
- `wiki_sources.yaml`: 4 wiki pubbliche + default_source
- `README.md`: Badge + sezione wiki test
- `CHANGELOG.md`: Entry v1.5.1
- `test_wiki.py`: Script test Wikipedia (NEW)
- `test_all_wikis.py`: Script test multiple wikis (NEW)

---

## 🔗 Link Utili

- [CHANGELOG Completo](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/blob/main/CHANGELOG.md)
- [Documentazione Wiki](https://github.com/EnzoGitHub27/datapizza-streamlit-interface#-knowledge-base-rag)
- [Guida Setup](https://github.com/EnzoGitHub27/datapizza-streamlit-interface#-installazione)

---

**Full Changelog**: https://github.com/EnzoGitHub27/datapizza-streamlit-interface/compare/v1.5.0...v1.5.1
```

4. **Set as latest release**: ✅ (checked)
5. Clicca **"Publish release"**

---

### Passo 6: Torna su dev per sviluppo futuro

```bash
# Torna al branch dev
git checkout dev

# Opzionale: porta le modifiche di main in dev (già presenti)
# git merge main

# Pronto per il prossimo sviluppo!
git status
```

---

## 🎯 Verifica Finale

- [ ] Commit presente su `origin/dev`
- [ ] Commit presente su `origin/main`
- [ ] Tag `v1.5.1` visibile su GitHub
- [ ] Release v1.5.1 pubblicata su GitHub
- [ ] Badge README mostra versione 1.5.1
- [ ] Tornato su branch `dev` per sviluppo

---

## 📝 Comandi Rapidi (Copy-Paste)

```bash
# Push dev
git push origin dev

# Merge dev → main
git checkout main
git merge dev

# Crea e push tag
git tag -a v1.5.1 -m "Release v1.5.1 - Wiki Bugfix + Test Sources"
git push origin main
git push origin v1.5.1

# Torna a dev
git checkout dev
```

---

## 🆘 Troubleshooting

### Errore: "Updates were rejected"
```bash
# Qualcuno ha pushato prima di te
git pull --rebase origin main
git push origin main
```

### Tag già esistente
```bash
# Rimuovi tag locale e remoto
git tag -d v1.5.1
git push origin :refs/tags/v1.5.1

# Ricrea
git tag -a v1.5.1 -m "Release v1.5.1"
git push origin v1.5.1
```

### Hai committato su main invece che su dev
```bash
# Crea branch da main
git checkout main
git checkout -b fix-branch

# Resetta main
git checkout main
git reset --hard origin/main

# Mergia fix-branch in dev
git checkout dev
git merge fix-branch
```

---

## 📅 Checklist Post-Release

- [ ] Annuncio su Discord/Telegram DeepAiUG
- [ ] Tweet/Post sui social (se applicabile)
- [ ] Aggiorna wiki/docs interne
- [ ] Chiudi eventuali issue risolte con questo fix
- [ ] Pianifica prossimo milestone (v1.5.2 o v1.6.0)

---

**Data Release**: 2025-01-16
**Versione**: v1.5.1
**Type**: Bugfix + Enhancement
**Breaking Changes**: None ✅
