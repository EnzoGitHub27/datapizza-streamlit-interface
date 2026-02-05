# ui/socratic/__init__.py
# DeepAiUG v1.8.0 - Modulo Socratico
# ============================================================================
# Strumenti per costruire "capitale semantico" (Floridi/Quartarone)
# L'AI non è un oracolo, ma uno strumento per costruire SENSO.
# ============================================================================

from .prompts import (
    SOCRATIC_PROMPTS,
    get_alternatives_prompt,
    get_assumptions_prompt,
    get_limits_prompt,
    get_confute_prompt,    # v1.8.0
    get_reflect_prompt,    # v1.8.0
)

from .buttons import (
    render_socratic_buttons,
    generate_alternatives,
    generate_assumptions,
    generate_limits,
    generate_confute,      # v1.8.0
    generate_reflect,      # v1.8.0
    clear_socratic_cache,
)

__all__ = [
    # Prompts
    "SOCRATIC_PROMPTS",
    "get_alternatives_prompt",
    "get_assumptions_prompt",
    "get_limits_prompt",
    "get_confute_prompt",      # v1.8.0
    "get_reflect_prompt",      # v1.8.0
    # Buttons
    "render_socratic_buttons",
    "generate_alternatives",
    "generate_assumptions",
    "generate_limits",
    "generate_confute",        # v1.8.0
    "generate_reflect",        # v1.8.0
    "clear_socratic_cache",
]
