# core/pii_memory.py
# DeepAiUG v1.16.0 (giro 7b) - I valori già tolti si tolgono sempre
# ============================================================================
# Nella prova dei casi di Giacomo, «Limiti» rimandava al cloud il testo del
# modello ripristinato: rizzo-pii, alla seconda passata, non ha riconosciuto
# «Paolo» (in grassetto, e in «Moglie di Paolo») e il nome è uscito in chiaro.
#
# PIISessionMemory tiene, SOLO IN MEMORIA e per la sessione, i valori veri già
# tolti con il loro segnaposto. A ogni chiamata verso fuori casa:
#   1. i valori noti si coprono per confronto di testo (dal più lungo al più
#      corto, confine di parola Unicode, i segnaposto già presenti non si
#      toccano) con un contrassegno temporaneo che rizzo-pii lascia stare;
#   2. il testo passa da rizzo-pii per i dati nuovi;
#   3. i dati nuovi si rinumerano DOPO quelli noti (un [FULLNAME_1] nuovo non
#      coincide mai con uno vecchio) e i contrassegni tornano il segnaposto
#      di prima;
#   4. il ripristino usa la tabella unita.
# Si confrontano solo valori che rizzo-pii ha già tolto così come sono: «Paolo»
# da solo si copre solo se rizzo-pii lo ha tolto una volta da solo. Nessuna
# associazione inventata.
#
# Mai su disco, mai nei log (repr senza valori), mai nella cronologia salvata,
# nella KB Chat o negli export. Si azzera con «Nuova», con il cambio di
# conversazione e alla chiusura della sessione.
# ============================================================================

from __future__ import annotations

import re
from typing import Dict, List, Mapping, Optional, Tuple

from .pii_client import AnonymizedText, _build_pattern

# un segnaposto come quelli di rizzo-pii: [ETICHETTA_N]
_PH_RE = re.compile(r"^\[([A-Z][A-Z0-9_]*?)_(\d+)\]$")
_ANY_PH = r"\[[A-Z][A-Z0-9_]*_\d+\]"
# contrassegno temporaneo per un valore noto, solo durante la chiamata a rizzo-pii
_MARK = "⟦DEEPAIUG·NOTO·{n}⟧"


class PIISessionMemory:
    """Valori già tolti in questa sessione → il loro segnaposto. Solo in memoria."""

    def __init__(self) -> None:
        self._by_value: Dict[str, str] = {}
        self._by_ph: Dict[str, str] = {}

    def __repr__(self) -> str:  # mai i valori in un log o in un traceback
        return f"PIISessionMemory({len(self._by_ph)} valori)"

    __str__ = __repr__

    def __len__(self) -> int:
        return len(self._by_ph)

    def clear(self) -> None:
        self._by_value.clear()
        self._by_ph.clear()

    @property
    def mapping(self) -> Dict[str, str]:
        """Copia della tabella segnaposto → valore (per il ripristino)."""
        return dict(self._by_ph)

    # -- 1. coprire i valori noti ------------------------------------------

    def cover(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Copre i valori noti con contrassegni. Restituisce (testo, contrassegno → segnaposto)."""
        if not text or not self._by_value:
            return text, {}
        values = sorted(self._by_value, key=len, reverse=True)
        alts = [_ANY_PH] + [rf"(?<!\w){re.escape(v)}(?!\w)" for v in values]
        pattern = re.compile("|".join(f"({a})" for a in alts))
        marks: Dict[str, str] = {}
        by_ph_mark: Dict[str, str] = {}

        def sub(m: re.Match) -> str:
            if m.group(1) is not None:  # un segnaposto già presente: resta
                return m.group(0)
            ph = self._by_value[m.group(0)]
            if ph not in by_ph_mark:
                mark = _MARK.format(n=len(by_ph_mark) + 1)
                by_ph_mark[ph] = mark
                marks[mark] = ph
            return by_ph_mark[ph]

        return pattern.sub(sub, text), marks

    # -- 3. unire i dati nuovi -----------------------------------------------

    def _next_placeholder(self, label: str, taken: set) -> str:
        n = 1
        for ph in taken:
            m = _PH_RE.match(ph)
            if m and m.group(1) == label:
                n = max(n, int(m.group(2)) + 1)
        return f"[{label}_{n}]"

    def merge(self, anon: AnonymizedText, marks: Mapping[str, str]) -> AnonymizedText:
        """Rinumera i dati nuovi dopo i noti, rimette i segnaposto noti, unisce le tabelle."""
        rename: Dict[str, str] = {}
        taken = set(self._by_ph)
        for ph, value in anon.mapping.items():
            if value in self._by_value:  # rizzo-pii lo ha trovato lo stesso: stesso segnaposto
                rename[ph] = self._by_value[value]
                continue
            m = _PH_RE.match(ph)
            if m and any((t := _PH_RE.match(x)) and t.group(1) == m.group(1) for x in taken):
                new_ph = self._next_placeholder(m.group(1), taken)  # dopo i noti
            elif ph in taken:
                new_ph = self._next_placeholder("PII", taken)
            else:
                new_ph = ph
            rename[ph] = new_ph
            taken.add(new_ph)
            self._by_ph[new_ph] = value
            self._by_value[value] = new_ph

        text = anon.text
        pattern = _build_pattern(anon.mapping.keys()) if anon.mapping else None
        if pattern is not None:
            by_inner = {(k[1:-1] if k.startswith("[") else k): v for k, v in rename.items()}
            text = pattern.sub(lambda m: by_inner.get(m.group(0).strip("[] \t\r\n"), m.group(0)), text)
        for mark, ph in marks.items():
            text = text.replace(mark, ph)

        by_label: Dict[str, int] = {}
        used = set(rename.values()) | set(marks.values())
        for ph in used:
            m = _PH_RE.match(ph)
            label = m.group(1) if m else "PII"
            by_label[label] = by_label.get(label, 0) + 1
        return AnonymizedText(
            text=text,
            mapping=self.mapping,
            by_label=by_label,
            n_entities=len(used),
        )
