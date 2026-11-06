# tests/conftest.py
# DeepAiUG v1.15.4 — Configurazione comune dei test
# ============================================================================
# I test girano sempre sul processore: sui portatili con GPU non supportate
# dalla build di torch installata (es. MX250) gli embedding falliscono con
# "CUDA error: no kernel image is available", e l'esito dei test non deve
# dipendere dalla scheda video. Va impostato prima di importare torch.
# ============================================================================

import os
import sys
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

# La radice del repo nel path, così "import core..." funziona da qualsiasi cartella
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
