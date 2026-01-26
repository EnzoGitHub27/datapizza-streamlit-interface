# ui/socratic/__init__.py
# Datapizza v1.6.1 - Modulo Socratico
# ============================================================================
# Strumenti per costruire "capitale semantico" (Floridi/Quartarone)
# L'AI non è un oracolo, ma uno strumento per costruire SENSO.
# ============================================================================

from .prompts import SOCRATIC_PROMPTS, get_alternatives_prompt
from .buttons import render_socratic_buttons, generate_alternatives, clear_socratic_cache

__all__ = [
    "SOCRATIC_PROMPTS",
    "get_alternatives_prompt",
    "render_socratic_buttons",
    "generate_alternatives",
    "clear_socratic_cache",
]
