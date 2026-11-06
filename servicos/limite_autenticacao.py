"""Limitação local de tentativas de login, compartilhada pelo processo."""

from __future__ import annotations

import hashlib
import threading
import time
from collections import defaultdict, deque

MAX_TENTATIVAS = 5
JANELA_SEGUNDOS = 15 * 60
_lock = threading.Lock()
_tentativas: dict[str, deque[float]] = defaultdict(deque)


def _chave(login: object) -> str:
    normalizado = str(login or "").strip().casefold().encode("utf-8")
    return hashlib.sha256(normalizado).hexdigest()


def bloqueado(login: object, *, agora: float | None = None) -> bool:
    instante = time.monotonic() if agora is None else agora
    chave = _chave(login)
    with _lock:
        tentativas = _tentativas[chave]
        if len(tentativas) >= MAX_TENTATIVAS:
            if instante - tentativas[-1] < JANELA_SEGUNDOS:
                return True
            _tentativas.pop(chave, None)
            return False
        while tentativas and instante - tentativas[0] >= JANELA_SEGUNDOS:
            tentativas.popleft()
        if not tentativas:
            _tentativas.pop(chave, None)
            return False
        return len(tentativas) >= MAX_TENTATIVAS


def registrar_falha(login: object, *, agora: float | None = None) -> None:
    instante = time.monotonic() if agora is None else agora
    chave = _chave(login)
    with _lock:
        # Limita crescimento por logins aleatórios e remove buckets expirados.
        for existente, tentativas in list(_tentativas.items()):
            while tentativas and instante - tentativas[0] >= JANELA_SEGUNDOS:
                tentativas.popleft()
            if not tentativas:
                _tentativas.pop(existente, None)
        if chave not in _tentativas and len(_tentativas) >= 10_000:
            return
        tentativas = _tentativas[chave]
        if len(tentativas) < MAX_TENTATIVAS:
            tentativas.append(instante)


def limpar(login: object) -> None:
    with _lock:
        _tentativas.pop(_chave(login), None)


def _limpar_tudo_para_teste() -> None:
    with _lock:
        _tentativas.clear()
