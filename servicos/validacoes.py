"""Normalização e validações compartilhadas pelas operações do MVP."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from servicos import ErroServico

_FATORES = {"KG": Decimal("1000"), "L": Decimal("1000"), "UN": Decimal("1")}
_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def texto_obrigatorio(valor: object, campo: str, *, minimo: int = 1) -> str:
    texto = str(valor or "").strip()
    if len(texto) < minimo:
        raise ErroServico(f"Informe {campo} (mínimo de {minimo} caracteres).")
    return texto


def texto_opcional(valor: object | None) -> str | None:
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto or None


def validar_email(valor: object | None) -> str | None:
    email = texto_opcional(valor)
    if email and not _EMAIL.fullmatch(email):
        raise ErroServico("Informe um e-mail válido.")
    return email


def validar_unidade(unidade: object) -> str:
    valor = str(unidade or "").strip().upper()
    if valor not in _FATORES:
        raise ErroServico("A unidade deve ser KG, L ou UN.")
    return valor


def quantidade_para_unidade_base(valor: object, unidade: object) -> int:
    unidade_validada = validar_unidade(unidade)
    if isinstance(valor, bool) or isinstance(valor, float):
        raise ErroServico("Digite a quantidade como texto decimal ou Decimal; não use ponto flutuante.")
    try:
        numero = valor if isinstance(valor, Decimal) else Decimal(str(valor).strip().replace(",", "."))
    except (InvalidOperation, ValueError, AttributeError) as exc:
        raise ErroServico("Informe uma quantidade numérica válida.") from exc
    if not numero.is_finite() or numero <= 0:
        raise ErroServico("A quantidade precisa ser maior que zero.")
    unidades_base = numero * _FATORES[unidade_validada]
    if unidades_base != unidades_base.to_integral_value():
        if unidade_validada == "UN":
            raise ErroServico("Unidades devem ser informadas como números inteiros.")
        raise ErroServico("A quantidade tem mais de três casas decimais; ela não será arredondada.")
    return int(unidades_base)


def quantidade_para_exibicao(valor_base: int, unidade: object) -> str:
    unidade_validada = validar_unidade(unidade)
    numero = Decimal(valor_base) / _FATORES[unidade_validada]
    texto = format(numero.normalize(), "f")
    return texto.replace(".", ",")


def validar_data(valor: date | str, campo: str = "a data") -> date:
    if isinstance(valor, datetime):
        resultado = valor.date()
    elif isinstance(valor, date):
        resultado = valor
    elif isinstance(valor, str):
        try:
            texto = valor.strip()
            resultado = datetime.strptime(texto, "%Y-%m-%d").date()
            if resultado.isoformat() != texto:
                raise ValueError("data fora do formato canônico")
        except ValueError as exc:
            raise ErroServico(f"Informe {campo} no formato AAAA-MM-DD e com uma data existente.") from exc
    else:
        raise ErroServico(f"Informe {campo} no formato AAAA-MM-DD.")
    return resultado


def data_iso(valor: date | str, campo: str = "a data") -> str:
    return validar_data(valor, campo).isoformat()


def validar_tipo_doador(valor: object) -> str:
    tipo = str(valor or "").strip().upper()
    if tipo not in {"PESSOA_FISICA", "EMPRESA", "ORGANIZACAO"}:
        raise ErroServico("Selecione um tipo de doador válido.")
    return tipo


def validar_senha(valor: object) -> str:
    senha = str(valor or "")
    if len(senha) < 12:
        raise ErroServico("A senha deve ter pelo menos 12 caracteres.")
    if len(senha.encode("utf-8")) > 1024:
        raise ErroServico("A senha excede o tamanho máximo permitido.")
    return senha
