# ui/socratic/prompts.py
# Datapizza v1.6.1 - Template Prompt Socratici
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

    # v1.8.0 - Future feature (placeholder)
    "confute": """Agisci come avvocato del diavolo.

Confuta questa risposta:

\"\"\"{response}\"\"\"

Trova i punti deboli, le falle logiche, le semplificazioni eccessive.
Non essere gentile, sii rigoroso ma costruttivo.""",
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