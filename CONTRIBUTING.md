# 🤝 Contributing to DeepAiUG Streamlit LLM Interface

Grazie per l'interesse nel contribuire a questo progetto! Questo documento fornisce linee guida per contribuire in modo efficace.

---

## 📋 Indice

- [Codice di Condotta](#codice-di-condotta)
- [Come Posso Contribuire?](#come-posso-contribuire)
- [Setup Ambiente di Sviluppo](#setup-ambiente-di-sviluppo)
- [Workflow Git](#workflow-git)
- [Standard di Codice](#standard-di-codice)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggerire Nuove Feature](#suggerire-nuove-feature)

---

## 📜 Codice di Condotta

### Il Nostro Impegno

Questo progetto adotta un ambiente aperto e accogliente. Ci impegniamo a rendere la partecipazione al progetto un'esperienza libera da molestie per tutti, indipendentemente da età, dimensione corporea, disabilità, etnia, identità di genere, livello di esperienza, nazionalità, aspetto personale, razza, religione o identità e orientamento sessuale.

### Comportamenti Attesi

- Usare linguaggio accogliente e inclusivo
- Rispettare punti di vista ed esperienze diverse
- Accettare critiche costruttive con grazia
- Concentrarsi su ciò che è meglio per la community
- Mostrare empatia verso altri membri della community

### Comportamenti Non Accettabili

- Uso di linguaggio o immagini sessualizzate
- Trolling, commenti offensivi o attacchi personali
- Molestie pubbliche o private
- Pubblicazione di informazioni private altrui
- Altre condotte inappropriate in contesto professionale

---

## 🎯 Come Posso Contribuire?

### Tipi di Contributi

#### 🐛 Segnalare Bug
Hai trovato un bug? Apri una [Issue](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/issues/new) seguendo il template.

#### ✨ Proporre Feature
Hai un'idea? Consulta la [ROADMAP.md](ROADMAP.md) e apri una Feature Request Issue.

#### 💻 Contribuire Codice
Scegli una Issue aperta, commenta per "prenderla in carico", e inizia a sviluppare!

#### 📖 Migliorare Documentazione
README, commenti codice, tutorial: ogni miglioramento è benvenuto.

#### 🧪 Testing
Testa l'applicazione su diversi OS/provider e segnala problemi.

#### 🌍 Traduzioni
Aiuta a tradurre interfaccia e documentazione in altre lingue.

---

## 🛠️ Setup Ambiente di Sviluppo

### Prerequisiti

- Python 3.8+
- Git
- Account GitHub
- (Opzionale) Ollama per test locali
- (Opzionale) API keys provider cloud

### Setup Passo-Passo

```bash
# 1. Fork il repository su GitHub
#    Vai su https://github.com/EnzoGitHub27/datapizza-streamlit-interface
#    Clicca "Fork" in alto a destra

# 2. Clona il TUO fork
git clone https://github.com/TUO-USERNAME/datapizza-streamlit-interface.git
cd datapizza-streamlit-interface

# 3. Aggiungi upstream remote (repository originale)
git remote add upstream https://github.com/EnzoGitHub27/datapizza-streamlit-interface.git

# 4. Verifica remote configurati
git remote -v
# Dovresti vedere:
# origin    https://github.com/TUO-USERNAME/... (tuo fork)
# upstream  https://github.com/EnzoGitHub27/... (originale)

# 5. Crea virtual environment
python -m venv deepaiug-interface
source deepaiug-interface/bin/activate  # Linux/Mac
# deepaiug-interface\Scripts\activate  # Windows

# 6. Installa dipendenze (usa script o manuale)
./install.sh  # Linux/Mac
# install.bat  # Windows

# 7. Configura API keys per testing (opzionale)
cp .env.example .env  # Se esiste template
# Oppure crea secrets/
mkdir secrets
echo "your-key" > secrets/openai_key.txt

# 8. Testa che tutto funzioni
streamlit run 00_interfaccia_dinamica_datapizza_Streamlit.py
```

---

## 🌿 Workflow Git

### Branch Strategy

```
main              # Produzione (solo release stabili)
  └── dev         # Sviluppo (feature integrate)
       ├── feature/nome-feature   # Nuove funzionalità
       ├── bugfix/nome-bug        # Correzioni bug
       └── docs/aggiornamento     # Aggiornamenti documentazione
```

### Workflow Standard

```bash
# 1. Sincronizza con upstream (sempre prima di iniziare!)
git checkout dev
git pull upstream dev

# 2. Crea branch feature dal dev aggiornato
git checkout -b feature/nome-descrittivo

# 3. Fai le modifiche
# ... edit files ...

# 4. Test locali
streamlit run 00_interfaccia_dinamica_datapizza_Streamlit.py
# Testa tutte le funzionalità modificate!

# 5. Commit con messaggi chiari
git add .
git commit -m "✨ Add feature X"

# 6. Push al TUO fork
git push origin feature/nome-descrittivo

# 7. Apri Pull Request su GitHub
# Vai su GitHub → Compare & pull request
# Base: EnzoGitHub27/datapizza-streamlit-interface (dev)
# Compare: TUO-USERNAME/datapizza-streamlit-interface (feature/nome-descrittivo)
```

### Mantenere Branch Aggiornato

```bash
# Se dev upstream è stato aggiornato durante il tuo lavoro:
git checkout feature/tua-feature
git fetch upstream
git rebase upstream/dev

# Risolvi eventuali conflitti, poi:
git push origin feature/tua-feature --force-with-lease
```

---

## 📝 Standard di Codice

### Python Style Guide

Seguiamo [PEP 8](https://peps.python.org/pep-0008/) con alcune eccezioni:

```python
# ✅ BUONO: Nomi funzioni snake_case
def load_api_key(provider_name: str) -> str:
    """
    Carica API key per un provider.
    
    Args:
        provider_name: Nome del provider (es. 'openai')
    
    Returns:
        API key come stringa
    """
    pass

# ✅ BUONO: Type hints sempre dove possibile
def create_client(model: str, temperature: float = 0.7) -> Any:
    pass

# ✅ BUONO: Docstring per funzioni complesse
def complex_function():
    """
    Breve descrizione.
    
    Descrizione dettagliata se necessario,
    con esempi d'uso.
    
    Args:
        param1: Descrizione parametro 1
        param2: Descrizione parametro 2
    
    Returns:
        Descrizione valore di ritorno
    
    Raises:
        ValueError: Quando accade X
    """
    pass

# ❌ CATTIVO: Nomi variabili non descrittivi
x = get_data()  # Cosa è x?
tmp = process(x)  # Cosa fa?

# ✅ BUONO: Nomi descrittivi
api_key = load_api_key("openai")
processed_response = format_response(raw_response)
```

### Commenti

```python
# ✅ BUONO: Commenti per sezioni logiche
# ============================================================================
# GESTIONE API KEYS
# ============================================================================

def load_api_key():
    # Prova prima con variabili d'ambiente
    key = os.getenv("API_KEY")
    
    # Fallback su file secrets
    if not key:
        key = read_from_file()
    
    return key

# ❌ CATTIVO: Commenti ovvi
x = x + 1  # Incrementa x

# ✅ BUONO: Commenti per logica complessa
# Usiamo un timeout di 30s perché alcuni modelli grandi
# (>70B parametri) possono richiedere più tempo su hardware limitato
timeout = 30 if is_large_model else 10
```

### Streamlit Best Practices

```python
# ✅ BUONO: Cache funzioni pesanti
@st.cache_data(ttl=3600)
def load_models_list():
    return expensive_operation()

# ✅ BUONO: Session state per persistenza
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ✅ BUONO: Gestione errori con feedback utente
try:
    response = client.invoke(prompt)
except Exception as e:
    st.error(f"Errore: {e}")
    st.info("Suggerimento: Verifica la connessione al modello")
```

### Naming Conventions

```python
# Costanti: UPPER_SNAKE_CASE
MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.7

# Variabili/funzioni: snake_case
api_key = "..."
def get_user_input():
    pass

# Classi: PascalCase
class ModelClient:
    pass

# Variabili "private": _underscore_prefix
def _internal_helper():
    pass
```

---

## 💬 Commit Messages

### Format Standard

Usiamo [Conventional Commits](https://www.conventionalcommits.org/) con emoji opzionali:

```
<tipo>[scope opzionale]: <descrizione>

[corpo opzionale]

[footer opzionale]
```

### Tipi di Commit

| Tipo | Emoji | Descrizione | Esempio |
|------|-------|-------------|---------|
| `feat` | ✨ | Nuova feature | `✨ feat: add multi-turn conversations` |
| `fix` | 🐛 | Bug fix | `🐛 fix: resolve API key loading issue` |
| `docs` | 📝 | Documentazione | `📝 docs: update installation guide` |
| `style` | 🎨 | Formattazione | `🎨 style: apply PEP 8 formatting` |
| `refactor` | ♻️ | Refactoring | `♻️ refactor: simplify client creation logic` |
| `test` | ✅ | Test | `✅ test: add unit tests for API loading` |
| `chore` | 🔧 | Manutenzione | `🔧 chore: update dependencies` |
| `perf` | ⚡ | Performance | `⚡ perf: optimize model loading speed` |

### Esempi

```bash
# Buoni esempi
git commit -m "✨ feat(ui): add dark mode toggle"
git commit -m "🐛 fix(export): resolve PDF generation crash"
git commit -m "📝 docs: add troubleshooting section to README"
git commit -m "♻️ refactor: extract API key logic to utils"

# Con corpo dettagliato
git commit -m "✨ feat: add streaming response support

- Implement token-by-token streaming
- Add progress indicator
- Support stop generation button
- Fallback to complete response if streaming fails

Closes #42"

# Cattivi esempi (evitare)
git commit -m "update"  # Troppo generico
git commit -m "fix stuff"  # Non descrittivo
git commit -m "WIP"  # Non committare work-in-progress
```

---

## 🔄 Pull Request Process

### Prima di Aprire una PR

- [ ] Codice segue gli standard del progetto
- [ ] Commit messages sono chiari e descrittivi
- [ ] Hai testato localmente tutte le modifiche
- [ ] Documentazione aggiornata se necessario
- [ ] Nessun file di configurazione/secrets committato
- [ ] Branch sincronizzato con upstream/dev

### Template PR

Quando apri la PR su GitHub, usa questo template:

```markdown
## Descrizione
Breve descrizione delle modifiche apportate.

## Tipo di Modifica
- [ ] 🐛 Bug fix (non-breaking change che risolve un problema)
- [ ] ✨ Nuova feature (non-breaking change che aggiunge funzionalità)
- [ ] 💥 Breaking change (modifica che causa malfunzionamenti esistenti)
- [ ] 📝 Documentazione

## Issue Correlata
Closes #(issue_number)

## Come È Stato Testato?
Descrivi i test effettuati:
- [ ] Test su Ollama locale
- [ ] Test con OpenAI
- [ ] Test con Anthropic
- [ ] Test su Linux
- [ ] Test su Windows
- [ ] Test su macOS

## Screenshot (se applicabile)
[Aggiungi screenshot dell'interfaccia modificata]

## Checklist
- [ ] Il codice segue gli standard del progetto
- [ ] Ho commentato il codice dove necessario
- [ ] Ho aggiornato la documentazione
- [ ] Le mie modifiche non generano nuovi warning
- [ ] Ho testato localmente con successo
```

### Processo Review

1. **Automated Checks**: CI/CD esegue test automatici
2. **Code Review**: Maintainer revisionerà il codice
3. **Feedback**: Potrebbero essere richieste modifiche
4. **Approval**: Una volta approvato, verrà mergiato in `dev`
5. **Merge**: Squash merge per mantenere history pulita

### Cosa Succede Dopo

- La tua feature sarà inclusa nel prossimo rilascio
- Sarai menzionato nel CHANGELOG.md
- Riceverai credito come contributor

---

## 🐛 Reporting Bugs

### Prima di Segnalare un Bug

- Cerca nelle [Issues esistenti](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/issues) se già segnalato
- Assicurati di usare l'ultima versione del progetto
- Prova a riprodurre il bug su ambiente pulito

### Template Bug Report

```markdown
## Descrizione Bug
Descrizione chiara e concisa del problema.

## Come Riprodurre
Passi per riprodurre:
1. Vai su '...'
2. Clicca su '....'
3. Inserisci '....'
4. Vedi errore

## Comportamento Atteso
Descrizione di cosa dovrebbe accadere normalmente.

## Screenshot
Se applicabile, aggiungi screenshot per spiegare il problema.

## Ambiente
- OS: [es. Ubuntu 22.04]
- Python Version: [es. 3.10.5]
- Streamlit Version: [es. 1.28.0]
- Datapizza Version: [es. 0.1.0]
- Provider: [es. Ollama locale / OpenAI cloud]
- Browser: [es. Chrome 120]

## Log/Traceback
```
[Incolla qui output errore completo]
```

## Informazioni Aggiuntive
Qualsiasi altra informazione utile sul problema.
```

---

## 💡 Suggerire Nuove Feature

### Feature Request Template

```markdown
## Feature Richiesta
Descrizione chiara della feature che vorresti.

## Problema Risolto
Quale problema risolverebbe questa feature?
Es: "Sono sempre frustrato quando [...]"

## Soluzione Proposta
Descrizione di come vorresti che funzionasse.

## Alternative Considerate
Hai considerato soluzioni alternative? Descrivile.

## Informazioni Aggiuntive
Mockup, esempi, riferimenti, etc.
```

---

## 🎓 Risorse per Contributor

### Documentazione Tecnica
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Datapizza AI GitHub](https://github.com/datapizza)
- [Python PEP 8 Style Guide](https://peps.python.org/pep-0008/)

### Tutorial
- [Git Branching](https://learngitbranching.js.org/)
- [How to Write Good Commit Messages](https://chris.beams.io/posts/git-commit/)
- [Pull Request Best Practices](https://github.blog/2015-01-21-how-to-write-the-perfect-pull-request/)

### Community
- [GitHub Discussions](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/discussions)
- [Issues](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/issues)

---

## 🙏 Riconoscimenti

Ogni contributor sarà riconosciuto:
- Nel file [CHANGELOG.md](CHANGELOG.md)
- Nella sezione Contributors di GitHub
- (Opzionale) Nel README.md

### Hall of Fame 🌟

Contributor con 5+ PR merged riceveranno badge speciale!

---

## ❓ Domande?

Se hai domande su come contribuire:
1. Controlla le [FAQ](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/wiki/FAQ)
2. Cerca nelle [Discussions](https://github.com/EnzoGitHub27/datapizza-streamlit-interface/discussions)
3. Apri una nuova Discussion

---

**Grazie per contribuire a DeepAiUG Streamlit LLM Interface! 🧠**

Il tuo contributo, grande o piccolo, rende questo progetto migliore per tutti! 🚀