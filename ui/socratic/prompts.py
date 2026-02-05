# ui/socratic/prompts.py
# DeepAiUG v1.8.0 - Template Prompt Socratici
# ============================================================================
# Prompt per stimolare il "lavoro semantico" dell'utente.
# Ispirati al concetto di capitale semantico (Floridi/Quartarone).
# ============================================================================

# Template dei prompt socratici
SOCRATIC_PROMPTS = {
    # v1.6.1 - Prima feature
    "alternatives": """Data questa risposta:

\"\"\"{response}\"\"\"

Genera 3 interpretazioni alternative dello stesso problema, ognuna basata su presupposti diversi.

Formato richiesto:
**Alternativa 1 - [Nome prospettiva]**
[Spiegazione concisa]

**Alternativa 2 - [Nome prospettiva]**
[Spiegazione concisa]

**Alternativa 3 - [Nome prospettiva]**
[Spiegazione concisa]

Sii conciso ma significativo. Ogni alternativa deve offrire un punto di vista genuinamente diverso.""",

    # v1.7.0 - Future features (placeholder)
    "assumptions": """Analizza questa risposta:

\"\"\"{response}\"\"\"

Quali assunzioni implicite contiene? Cosa dà per scontato che potrebbe non esserlo?

Elenca le assunzioni in modo chiaro e conciso.""",

    "limits": """Analizza questa risposta:

\"\"\"{response}\"\"\"

In quali situazioni questa risposta NON funzionerebbe o sarebbe fuorviante?
Quali sono i limiti di validità di questa spiegazione?

Sii specifico e concreto.""",

    # v1.8.0 - Confuta (avvocato del diavolo)
    "confute": """Agisci come avvocato del diavolo.

Confuta questa risposta:

\"\"\"{response}\"\"\"

Analizza criticamente:
1. **Punti deboli**: Dove il ragionamento è fragile?
2. **Falle logiche**: Ci sono salti logici o semplificazioni eccessive?
3. **Controesempi**: In quali casi concreti questa risposta sarebbe sbagliata?

Sii rigoroso ma costruttivo. L'obiettivo è rafforzare il pensiero critico, non demolire.""",

    # v1.8.0 - Rifletti (sfida la DOMANDA, non la risposta)
    "reflect": """L'utente ha fatto questa domanda:

\"\"\"{user_question}\"\"\"

E ha ricevuto questa risposta:

\"\"\"{response}\"\"\"

Invece di analizzare la risposta, SFIDA LA DOMANDA dell'utente.
Genera 3 domande provocatorie che aiutino a riflettere su:

1. **Perimetro decisionale**: Su cosa sta davvero decidendo? La domanda nasconde una decisione più grande?

2. **Assunzioni non dette**: Cosa sta dando per scontato senza accorgersene? Quali vincoli impliciti ha nella mente?

3. **Giustificabilità**: Quale parte della risposta non saprebbe giustificare se qualcuno glielo chiedesse?

Non dare risposte. Fai solo domande che mettano in crisi costruttivamente.
Sii diretto ma rispettoso. L'obiettivo è migliorare il DIALOGO, non l'output.""",
}


def get_alternatives_prompt(response: str) -> str:
    """
    Genera il prompt per richiedere alternative a una risposta.
    
    Args:
        response: La risposta originale dell'AI
        
    Returns:
        Il prompt formattato per generare alternative
    """
    return SOCRATIC_PROMPTS["alternatives"].format(response=response)


def get_assumptions_prompt(response: str) -> str:
    """Genera il prompt per analizzare le assunzioni. (v1.7.0)"""
    return SOCRATIC_PROMPTS["assumptions"].format(response=response)


def get_limits_prompt(response: str) -> str:
    """Genera il prompt per identificare i limiti. (v1.7.0)"""
    return SOCRATIC_PROMPTS["limits"].format(response=response)


def get_confute_prompt(response: str) -> str:
    """Genera il prompt per confutare la risposta. (v1.8.0)"""
    return SOCRATIC_PROMPTS["confute"].format(response=response)


def get_reflect_prompt(response: str, user_question: str) -> str:
    """
    Genera il prompt per riflettere sulla DOMANDA dell'utente. (v1.8.0)

    Args:
        response: La risposta dell'AI
        user_question: La domanda originale dell'utente

    Returns:
        Il prompt formattato per stimolare riflessione critica sulla domanda
    """
    return SOCRATIC_PROMPTS["reflect"].format(
        response=response,
        user_question=user_question
    )