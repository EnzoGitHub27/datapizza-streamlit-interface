# tests/test_chat_render.py
# DeepAiUG v1.15.4 — Bug «[object Object]»: la bolla della chat usa il
# Markdown nativo di Streamlit, senza HTML grezzo.
# ============================================================================
# Prima: ui/chat.py convertiva il Markdown in HTML (markdown_it) e lo passava a
# st.markdown(unsafe_allow_html=True). Alla prima riga vuota di un blocco di
# codice il blocco HTML si chiudeva, il resto veniva riletto come Markdown e il
# frontend mostrava (e copiava) «[object Object]». Vedi docs/AUDIT_pre_v1.16.0.md §3.
# ============================================================================

from streamlit.testing.v1 import AppTest

from ui.chat import _escape_md, bubble_key

CODICE = '''```python
class Cliente:
    def __init__(self, nome):
        self.nome = nome

    def saluta(self, *args, **kwargs):
        # commento con # e __dunder__
        return f"Ciao {self.nome}"
```'''

RISPOSTA = f"Ecco la classe:\n\n{CODICE}\n\n| Nome | CF |\n|---|---|\n| Mario Rossi | finto |\n"


def _app(messages, socratic_mode="fast"):
    """Script AppTest: disegna i messaggi con render_chat_message."""

    def script(messages, socratic_mode):
        from ui.chat import render_chat_message

        for i, m in enumerate(messages):
            render_chat_message(m, i, None, messages_list=messages, socratic_mode=socratic_mode)

    at = AppTest.from_function(script, args=(messages, socratic_mode), default_timeout=30)
    at.run()
    assert not at.exception, at.exception
    return at


def _all_markdown(at):
    return [m.value for m in at.markdown]


def test_bubble_key():
    assert bubble_key("user", 3) == "user-bubble-3"
    assert bubble_key("assistant", 0) == "assistant-bubble-0"


def test_code_block_passed_verbatim_to_native_markdown():
    msgs = [{"role": "assistant", "content": RISPOSTA, "model": "llama3.2:3b"}]
    at = _app(msgs)
    values = _all_markdown(at)
    # Il contenuto arriva a st.markdown così com'è: il blocco di codice, con la
    # riga vuota, resta un unico blocco fenced
    assert RISPOSTA.strip() in [v.strip() for v in values]
    joined = "\n".join(values)
    assert "[object Object]" not in joined
    assert "<pre>" not in joined and "<div" not in joined


def test_no_raw_html_in_bubbles():
    msgs = [
        {"role": "user", "content": "Ciao <b>grassetto</b>", "attachments": ["preventivo.pdf"]},
        {"role": "assistant", "content": RISPOSTA},
    ]
    at = _app(msgs)
    for m in at.markdown:
        assert not m.proto.allow_html, m.value


def _block_ids(node, out):
    for child in getattr(node, "children", {}).values():
        proto = getattr(child, "proto", None)
        if proto is not None and getattr(proto, "id", ""):
            out.append(proto.id)
        _block_ids(child, out)
    return out


def test_bubbles_have_keyed_containers():
    msgs = [{"role": "user", "content": "domanda"}, {"role": "assistant", "content": "risposta"}]
    at = _app(msgs)
    # i contenitori con key esistono: è lì che si aggancia il CSS (st-key-...)
    ids = " ".join(_block_ids(at.main, []))
    assert "user-bubble-0" in ids, ids
    assert "assistant-bubble-1" in ids, ids


def test_attachments_line_escaped():
    assert _escape_md("file_*finto*.pdf") == r"file\_\*finto\*\.pdf"
    msgs = [{"role": "user", "content": "vedi allegato", "attachments": ["a_b.pdf", "c.txt"]}]
    at = _app(msgs)
    captions = [c.value for c in at.caption]
    assert any("Allegati" in c and r"a\_b\.pdf" in c for c in captions), captions


def test_socratic_buttons_still_render_for_assistant():
    msgs = [
        {"role": "user", "content": "Che cos'è una flangia?"},
        {"role": "assistant", "content": "Un elemento di collegamento."},
    ]
    at = _app(msgs, socratic_mode="standard")
    assert len(at.button) >= 1
