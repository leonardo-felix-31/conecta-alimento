"""Referência temporal local centralizada e substituível nos testes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class ReferenciaTemporal:
    instante: datetime
    data_referencia: date
    timestamp: str


def obter_instante_local() -> datetime:
    return datetime.now().astimezone()


def obter_referencia_temporal(instante: datetime | None = None) -> ReferenciaTemporal:
    valor = instante if instante is not None else obter_instante_local()
    if valor.tzinfo is None or valor.utcoffset() is None:
        raise ValueError("O instante precisa incluir um fuso horário")
    # datetime.now().astimezone() já é local; instantes injetados preservam o fuso fixo do teste.
    local = valor if instante is not None else valor.astimezone()
    return ReferenciaTemporal(
        instante=local,
        data_referencia=local.date(),
        timestamp=local.isoformat(timespec="seconds"),
    )
