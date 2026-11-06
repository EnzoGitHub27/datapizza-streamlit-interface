# tests/test_embeddings_device.py
# DeepAiUG v1.15.4 — Gli embedding usano la GPU solo se torch ha i kernel per
# la sua architettura (MX250 = sm_61 con torch +cu130 = sm_75+ → CPU).
# ============================================================================
# torch.cuda è simulato: nessuna GPU vera, nessun modello caricato.
# ============================================================================

import warnings

import pytest
import torch

from rag import embeddings
from rag.embeddings import DEVICE_ENV_VAR, _arch_supported, select_device

ARCH_CU130 = ["sm_75", "sm_80", "sm_86", "sm_90", "sm_100", "sm_120"]


@pytest.fixture
def fake_cuda(monkeypatch):
    """Configura torch.cuda simulato: fake_cuda(available, capability, arch_list)."""
    monkeypatch.delenv(DEVICE_ENV_VAR, raising=False)

    def setup(available=True, capability=(6, 1), arch_list=ARCH_CU130):
        def get_capability():
            # come torch vero sulle schede vecchie: avvisa, poi risponde
            warnings.warn("Found GPU0 which is of cuda capability 6.1", UserWarning)
            if isinstance(capability, Exception):
                raise capability
            return capability

        monkeypatch.setattr(torch.cuda, "is_available", lambda: available)
        monkeypatch.setattr(torch.cuda, "get_device_capability", get_capability)
        monkeypatch.setattr(torch.cuda, "get_arch_list", lambda: arch_list)

    return setup


def test_supported_gpu_uses_cuda(fake_cuda):
    fake_cuda(capability=(8, 6))
    device, reason = select_device()
    assert device == "cuda"
    assert "sm_86" in reason


def test_unsupported_gpu_uses_cpu(fake_cuda):
    fake_cuda(capability=(6, 1))  # MX250
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)  # il controllo li silenzia
        device, reason = select_device()
    assert device == "cpu"
    assert "sm_61" in reason and "non supportata" in reason


def test_no_cuda_uses_cpu(fake_cuda):
    fake_cuda(available=False)
    assert select_device() == ("cpu", "CUDA non disponibile")


def test_exception_uses_cpu(fake_cuda):
    fake_cuda(capability=RuntimeError("driver rotto"))
    device, reason = select_device()
    assert device == "cpu"
    assert "RuntimeError" in reason


@pytest.mark.parametrize("forced", ["cpu", "cuda", "CUDA "])
def test_env_var_wins(fake_cuda, monkeypatch, forced):
    fake_cuda(capability=(6, 1) if forced.strip().lower() == "cuda" else (8, 6))
    monkeypatch.setenv(DEVICE_ENV_VAR, forced)
    device, reason = select_device()
    assert device == forced.strip().lower()
    assert DEVICE_ENV_VAR in reason


def test_env_var_invalid_is_ignored(fake_cuda, monkeypatch):
    fake_cuda(capability=(6, 1))
    monkeypatch.setenv(DEVICE_ENV_VAR, "tpu")
    assert select_device()[0] == "cpu"


@pytest.mark.parametrize(
    "capability, arch_list, expected",
    [
        ((6, 1), ARCH_CU130, False),          # MX250
        ((7, 5), ARCH_CU130, True),           # esatta
        ((8, 9), ARCH_CU130, True),           # RTX 40: binario sm_86 compatibile
        ((6, 1), ["sm_60"], True),            # stessa generazione, minor più basso
        ((6, 0), ["sm_61"], False),           # minor più alto non va
        ((6, 1), ["sm_75", "compute_60"], True),  # PTX compilato al volo
        ((6, 1), ["compute_75"], False),      # PTX più recente della scheda
        ((6, 1), [], False),
    ],
)
def test_arch_supported(capability, arch_list, expected):
    assert _arch_supported(capability, arch_list) is expected


def test_helper_passes_device(monkeypatch):
    """_EmbeddingsHelper passa il device scelto a SentenceTransformer."""
    import sentence_transformers

    seen = {}

    class FakeST:
        def __init__(self, name, device=None):
            seen["name"], seen["device"] = name, device

    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", FakeST)
    monkeypatch.setattr(embeddings, "select_device", lambda: ("cpu", "prova"))
    helper = embeddings._EmbeddingsHelper("modello-finto")
    assert seen == {"name": "modello-finto", "device": "cpu"}
    assert helper.device == "cpu"
