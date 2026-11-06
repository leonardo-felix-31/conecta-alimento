"""Indicadores operacionais calculados em uma leitura consistente do SQLite."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from banco.conexao import conectar
from banco.inicializacao import CAMINHO_BANCO_PADRAO
from servicos.estoque import (
    DIAS_ALERTA_VENCIMENTO,
    _listar_estoque_por_alimento_conn,
    _listar_movimentacoes_recentes_conn,
    _listar_saldos_por_lote_conn,
)
from servicos.relogio import obter_referencia_temporal
from servicos.validacoes import validar_data


def obter_indicadores(
    *, data_referencia: date | str | None = None, caminho: str | Path | None = None,
) -> dict[str, object]:
    referencia = obter_referencia_temporal().data_referencia if data_referencia is None else validar_data(data_referencia)
    destino = caminho or CAMINHO_BANCO_PADRAO
    conn = conectar(destino)
    try:
        conn.execute("BEGIN")
        try:
            doacoes = int(conn.execute("SELECT COUNT(*) FROM Doacao").fetchone()[0])
            lotes_total = int(conn.execute("SELECT COUNT(*) FROM Lote").fetchone()[0])
            saldos = _listar_saldos_por_lote_conn(conn, data_referencia=referencia)
            por_alimento = _listar_estoque_por_alimento_conn(
                conn, categoria="disponivel", data_referencia=referencia,
            )
            recentes = _listar_movimentacoes_recentes_conn(conn, limite=10)
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
    finally:
        conn.close()

    disponiveis = [lote for lote in saldos if lote["estado"] == "disponível"]
    vencidos = [lote for lote in saldos if lote["estado"] == "vencido"]
    proximos = [lote for lote in saldos if lote["proximo_vencimento"]]
    return {
        "data_referencia": referencia.isoformat(),
        "doacoes_recebidas": doacoes,
        "lotes_registrados": lotes_total,
        "lotes_disponiveis": len(disponiveis),
        "alimentos_disponiveis": len(por_alimento),
        "estoque_por_alimento": por_alimento,
        "saldos_por_lote": [lote for lote in saldos if int(lote["saldo"]) > 0],
        "lotes_proximos_vencimento": proximos,
        "lotes_vencidos": vencidos,
        "movimentacoes_recentes": recentes,
        "banco_vazio": doacoes == 0 and lotes_total == 0,
        "dias_alerta_vencimento": DIAS_ALERTA_VENCIMENTO,
    }
