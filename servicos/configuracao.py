"""Leitura de configurações não secretas e de segredos externos ao código."""

from __future__ import annotations

import os


def obter_valor(nome: str, padrao: str = "") -> str:
    """Lê primeiro do ambiente e depois de st.secrets, sem expor o valor."""
    valor = os.environ.get(nome)
    if valor is not None and valor.strip():
        return valor.strip()
    try:
        import streamlit as st

        valor = st.secrets.get(nome, padrao)
    except Exception:
        return padrao
    return str(valor).strip() if valor is not None else padrao


def ambiente_hospedado() -> bool:
    return obter_valor("CONECTA_ENV", "local").casefold() in {"hosted", "cloud"}


def modo_demo() -> bool:
    return obter_valor("CONECTA_DEMO_MODE").casefold() == "true"
