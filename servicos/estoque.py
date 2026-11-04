"""Consultas de estoque derivadas das movimentações registradas."""

from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path

from banco.conexao import conectar
from banco.inicializacao import CAMINHO_BANCO_PADRAO
from servicos.relogio import obter_referencia_temporal
from servicos.validacoes import validar_data

DIAS_ALERTA_VENCIMENTO = 7


def _referencia(valor: date | str | None) -> date:
    return obter_referencia_temporal().data_referencia if valor is None else validar_data(valor, "a data de referência")


def _listar_saldos_por_lote_conn(
    conn: sqlite3.Connection, *, categoria: str = "todos", data_referencia: date | str | None = None,
    somente_com_saldo: bool = True,
) -> list[dict[str, object]]:
    referencia = _referencia(data_referencia)
    if categoria not in {"todos", "disponivel", "vencido", "proximo"}:
        raise ValueError("Categoria deve ser todos, disponivel, vencido ou proximo.")
    limite = referencia + timedelta(days=DIAS_ALERTA_VENCIMENTO)
    rows = conn.execute("""
        SELECT s.id_lote,s.codigo_lote,s.id_alimento,a.nome AS alimento,
               a.unidade_medida,a.ativo AS alimento_ativo,s.data_validade,s.saldo
        FROM vw_saldo_por_lote s JOIN Alimento a ON a.id_alimento=s.id_alimento
        ORDER BY s.data_validade,s.codigo_lote
    """)
    resultado: list[dict[str, object]] = []
    for row in rows:
        saldo = int(row["saldo"])
        validade = date.fromisoformat(row["data_validade"])
        if somente_com_saldo and saldo <= 0:
            continue
        estado = "vencido" if validade < referencia else "disponível"
        proximo = referencia <= validade <= limite
        if categoria == "disponivel" and estado != "disponível":
            continue
        if categoria == "vencido" and estado != "vencido":
            continue
        if categoria == "proximo" and not proximo:
            continue
        resultado.append({
            "id_lote": row["id_lote"],
            "codigo_lote": row["codigo_lote"],
            "id_alimento": row["id_alimento"],
            "alimento": row["alimento"],
            "unidade_medida": row["unidade_medida"],
            "alimento_ativo": bool(row["alimento_ativo"]),
            "data_validade": row["data_validade"],
            "saldo": saldo,
            "estado": estado,
            "proximo_vencimento": proximo,
        })
    return resultado


def listar_saldos_por_lote(
    *, categoria: str = "todos", data_referencia: date | str | None = None,
    somente_com_saldo: bool = True, caminho: str | Path | None = None,
) -> list[dict[str, object]]:
    conn = conectar(caminho or CAMINHO_BANCO_PADRAO)
    try:
        return _listar_saldos_por_lote_conn(
            conn, categoria=categoria, data_referencia=data_referencia,
            somente_com_saldo=somente_com_saldo,
        )
    finally:
        conn.close()


def _listar_estoque_por_alimento_conn(
    conn: sqlite3.Connection, *, categoria: str = "fisico", data_referencia: date | str | None = None,
) -> list[dict[str, object]]:
    referencia = _referencia(data_referencia)
    if categoria not in {"fisico", "disponivel", "vencido"}:
        raise ValueError("Categoria deve ser fisico, disponivel ou vencido.")
    lotes = conn.execute("""
        SELECT s.id_alimento,a.nome,a.unidade_medida,a.ativo,s.data_validade,s.saldo
        FROM vw_saldo_por_lote s JOIN Alimento a ON a.id_alimento=s.id_alimento
    """)
    totais: dict[int, dict[str, object]] = {}
    for row in lotes:
        saldo = int(row["saldo"])
        if saldo <= 0:
            continue
        vencido = date.fromisoformat(row["data_validade"]) < referencia
        if categoria == "disponivel" and vencido:
            continue
        if categoria == "vencido" and not vencido:
            continue
        alimento_id = int(row["id_alimento"])
        if alimento_id not in totais:
            totais[alimento_id] = {
                "id_alimento": alimento_id,
                "alimento": row["nome"],
                "unidade_medida": row["unidade_medida"],
                "ativo": bool(row["ativo"]),
                "saldo": 0,
            }
        totais[alimento_id]["saldo"] = int(totais[alimento_id]["saldo"]) + saldo
    return sorted(totais.values(), key=lambda item: str(item["alimento"]).casefold())


def listar_estoque_por_alimento(
    *, categoria: str = "fisico", data_referencia: date | str | None = None,
    caminho: str | Path | None = None,
) -> list[dict[str, object]]:
    conn = conectar(caminho or CAMINHO_BANCO_PADRAO)
    try:
        return _listar_estoque_por_alimento_conn(
            conn, categoria=categoria, data_referencia=data_referencia,
        )
    finally:
        conn.close()


def _listar_movimentacoes_recentes_conn(
    conn: sqlite3.Connection, *, limite: int = 20,
) -> list[dict[str, object]]:
    if not 1 <= limite <= 500:
        raise ValueError("O limite deve estar entre 1 e 500.")
    return [dict(row) for row in conn.execute("""
        SELECT m.id_movimentacao,m.tipo,m.quantidade,m.data_movimentacao,m.motivo,
               l.codigo_lote,a.nome AS alimento,a.unidade_medida,u.nome AS responsavel
        FROM MovimentacaoEstoque m
        JOIN Lote l ON l.id_lote=m.id_lote
        JOIN Alimento a ON a.id_alimento=m.id_alimento
        JOIN Usuario u ON u.id_usuario=m.id_usuario
        ORDER BY m.id_movimentacao DESC LIMIT ?
    """, (limite,))]


def listar_movimentacoes_recentes(
    *, limite: int = 20, caminho: str | Path | None = None,
) -> list[dict[str, object]]:
    conn = conectar(caminho or CAMINHO_BANCO_PADRAO)
    try:
        return _listar_movimentacoes_recentes_conn(conn, limite=limite)
    finally:
        conn.close()
