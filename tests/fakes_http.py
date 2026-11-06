# tests/fakes_http.py
# Sessione HTTP finta per i test dei client rizzo-pii e Annona.
# Nessuna chiamata di rete: ogni risposta è scritta nel test.
# ============================================================================

from urllib.parse import urlparse

import requests


class FakeResponse:
    def __init__(self, status_code=200, body=None, raw=None):
        self.status_code = status_code
        self._body = body
        self._raw = raw

    def json(self):
        if self._raw is not None:
            raise ValueError("not json")
        return self._body


class FakeSession:
    """Risponde secondo una tabella {(metodo, percorso): FakeResponse | Exception}."""

    def __init__(self, routes=None):
        self.routes = dict(routes or {})
        self.calls = []

    def _handle(self, method, url, **kwargs):
        path = urlparse(url).path or "/"
        self.calls.append({"method": method, "path": path, **kwargs})
        target = self.routes.get((method, path))
        if target is None:
            return FakeResponse(404, {"detail": "not found"})
        if isinstance(target, Exception):
            raise target
        return target

    def get(self, url, **kwargs):
        return self._handle("get", url, **kwargs)

    def post(self, url, **kwargs):
        return self._handle("post", url, **kwargs)


def connection_refused():
    return requests.ConnectionError("[Errno 111] Connection refused")
