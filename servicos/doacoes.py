"""Recebimento transacional de doações, lotes e entradas de estoque."""

from __future__ import annotations

import secrets
import logging
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Mapping

from banco.conexao import conectar, conexao_aberta
from banco.inicializacao import CAMINHO_BANCO_PADRAO
from servicos import ErroServico
from servicos.relogio import obter_referencia_temporal
from servicos.validacoes import data_iso, quantidade_para_unidade_base, texto_opcional

logger = logging.getLogger(__name__)


def _novo_codigo_lote(conn: sqlite3.Connection, ano: int) -> str:
    for _ in range(20):
        codigo = f"CA-{ano}-{secrets.token_hex(4).upper()}"
        if conn.execute("SELECT 1 FROM Lote WHERE codigo_lote=?", (codigo,)).fetchone() is None:
            return codigo
    raise ErroServico("Não foi possível gerar um código interno de lote único.")


def receber_doacao(
    id_doador: int,
    id_usuario: int,
    itens: Iterable[Mapping[str, object]],
    *,
    data_recebimento: date | str | None = None,
    observacao: object | None = None,
    caminho: str | Path | None = None,
    instante: datetime | None = None,
) -> dict[str, object]:
    referencia = obter_referencia_temporal(instante)
    recebida_em = data_iso(data_recebimento or referencia.data_referencia, "a data de recebimento")
    observacao_ok = texto_opcional(observacao)
    try:
        lista_itens = list(itens)
    except TypeError as exc:
        raise ErroServico("Informe os itens recebidos na doação.") from exc
    if not lista_itens:
        raise ErroServico("Adicione pelo menos um alimento à doação.")
    if len(lista_itens) > 100:
        raise ErroServico("Uma doação pode conter no máximo 100 lotes por operação.")

    itens_validados: list[dict[str, object]] = []
    for posicao, item in enumerate(lista_itens, start=1):
        try:
            id_alimento_original = item["id_alimento"]
            id_alimento = int(id_alimento_original)
            if isinstance(id_alimento_original, bool) or str(id_alimento_original).strip() != str(id_alimento):
                raise ErroServico(f"Selecione um alimento válido para o item {posicao}.")
            quantidade_digitada = item["quantidade"]
            validade = data_iso(item["data_validade"], f"a validade do item {posicao}")
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, ErroServico):
                raise
            raise ErroServico(f"Confira os dados do item {posicao}.") from exc
        if id_alimento <= 0:
            raise ErroServico(f"Selecione um alimento válido para o item {posicao}.")
        itens_validados.append({
            "id_alimento": id_alimento,
            "quantidade_digitada": quantidade_digitada,
            "data_validade": validade,
            "codigo_origem": texto_opcional(item.get("codigo_origem")),
        })

    destino = caminho or CAMINHO_BANCO_PADRAO
    codigos: list[str] = []
    try:
        with conexao_aberta(destino) as conn:
            conn.execute("BEGIN IMMEDIATE")
            doador = conn.execute("SELECT ativo FROM Doador WHERE id_doador=?", (id_doador,)).fetchone()
            usuario = conn.execute("SELECT ativo FROM Usuario WHERE id_usuario=?", (id_usuario,)).fetchone()
            if doador is None or doador["ativo"] != 1:
                raise ErroServico("Selecione um doador ativo.")
            if usuario is None or usuario["ativo"] != 1:
                raise ErroServico("O usuário responsável não existe ou está inativo.")

            ids_alimento = {int(item["id_alimento"]) for item in itens_validados}
            placeholders = ",".join("?" for _ in ids_alimento)
            alimentos = {
                row["id_alimento"]: row
                for row in conn.execute(
                    f"SELECT id_alimento,unidade_medida,ativo FROM Alimento WHERE id_alimento IN ({placeholders})",
                    tuple(ids_alimento),
                )
            }
            for item in itens_validados:
                alimento = alimentos.get(item["id_alimento"])
                if alimento is None or alimento["ativo"] != 1:
                    raise ErroServico("A doação contém alimento inexistente ou inativo.")
                item["quantidade_base"] = quantidade_para_unidade_base(
                    item["quantidade_digitada"], alimento["unidade_medida"]
                )

            cursor_doacao = conn.execute(
                "INSERT INTO Doacao (id_doador,id_usuario,data_recebimento,observacao) VALUES (?,?,?,?)",
                (id_doador, id_usuario, recebida_em, observacao_ok),
            )
            id_doacao = int(cursor_doacao.lastrowid)
            ano_codigo = date.fromisoformat(recebida_em).year
            for item in itens_validados:
                codigo = _novo_codigo_lote(conn, ano_codigo)
                cursor_lote = conn.execute(
                    "INSERT INTO Lote (id_doacao,id_alimento,codigo_lote,codigo_origem,data_validade) VALUES (?,?,?,?,?)",
                    (id_doacao, item["id_alimento"], codigo, item["codigo_origem"], item["data_validade"]),
                )
                id_lote = int(cursor_lote.lastrowid)
                conn.execute(
                    """INSERT INTO MovimentacaoEstoque
                       (id_lote,id_alimento,id_usuario,tipo,quantidade,data_movimentacao)
                       VALUES (?,?,?,'ENTRADA_DOACAO',?,?)""",
                    (id_lote, item["id_alimento"], id_usuario, item["quantidade_base"], referencia.timestamp),
                )
                codigos.append(codigo)
            return {"id_doacao": id_doacao, "codigos_lote": codigos, "data_recebimento": recebida_em}
    except sqlite3.IntegrityError as exc:
        logger.exception("Falha de integridade ao receber doação; transação revertida")
        raise ErroServico("O recebimento não foi concluído; nenhuma alteração foi gravada. Confira os dados e tente novamente.") from exc
