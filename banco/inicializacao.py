"""Inicialização transacional e versionada do esquema SQLite."""

from __future__ import annotations

import sqlite3
import os
from pathlib import Path

from banco.conexao import ErroBanco, conectar

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_BANCO_PADRAO = Path(os.environ.get(
    "CONECTA_DB_PATH", str(RAIZ_PROJETO / "dados" / "conecta_alimento.sqlite3")
)).expanduser()
CAMINHO_SCHEMA = Path(__file__).resolve().with_name("schema.sql")
VERSAO_MINIMA_SQLITE = (3, 37, 0)
VERSAO_ESQUEMA = 1

COLUNAS_ESPERADAS = {
    "Doador": {"id_doador", "nome", "tipo", "telefone", "email", "ativo"},
    "Alimento": {"id_alimento", "nome", "categoria", "unidade_medida", "ativo"},
    "Instituicao": {"id_instituicao", "nome", "tipo", "responsavel", "telefone", "email", "endereco", "ativo"},
    "Usuario": {"id_usuario", "nome", "login", "senha_hash", "perfil", "ativo"},
    "Doacao": {"id_doacao", "id_doador", "id_usuario", "data_recebimento", "observacao"},
    "Lote": {"id_lote", "id_doacao", "id_alimento", "codigo_lote", "codigo_origem", "data_validade", "observacao"},
    "Solicitacao": {"id_solicitacao", "id_instituicao", "id_usuario", "data_solicitacao", "status", "observacao"},
    "ItemSolicitacao": {"id_item_solicitacao", "id_solicitacao", "id_alimento", "quantidade_solicitada"},
    "Distribuicao": {"id_distribuicao", "id_solicitacao", "id_usuario", "data_distribuicao", "observacao"},
    "MovimentacaoEstoque": {"id_movimentacao", "id_lote", "id_alimento", "id_usuario", "tipo", "quantidade", "data_movimentacao", "motivo", "id_distribuicao", "id_item_solicitacao", "id_solicitacao", "id_movimentacao_original"},
}
INDICES_ESPERADOS = {
    "idx_doacao_doador", "idx_doacao_usuario", "idx_lote_alimento_validade",
    "idx_lote_doacao", "idx_solicitacao_instituicao_data", "idx_item_solicitacao_alimento",
    "idx_distribuicao_solicitacao_data", "idx_movimentacao_lote", "idx_movimentacao_item_tipo",
    "uq_movimentacao_entrada_lote", "uq_movimentacao_saida_linha", "uq_movimentacao_estorno_origem",
}
TRIGGERS_ESPERADOS = {
    "trg_movimentacao_immutable_update", "trg_movimentacao_immutable_delete",
    "trg_movimentacao_requires_entry", "trg_movimentacao_no_negative_or_expired",
    "trg_movimentacao_request_limit", "trg_alimento_unidade_immutable",
    "trg_movimentacao_refund_integrity", "trg_distribuicao_data_immutable_after_output",
    "trg_lote_validade_immutable_after_output",
}
VIEWS_ESPERADAS = {"vw_saldo_por_lote", "vw_atendimento_itens"}


def validar_compatibilidade() -> None:
    versao = tuple(int(parte) for parte in sqlite3.sqlite_version.split(".")[:3])
    if versao < VERSAO_MINIMA_SQLITE:
        raise ErroBanco(
            f"SQLite {sqlite3.sqlite_version} não suporta tabelas STRICT; mínimo: 3.37.0"
        )


def _objetos(conn: sqlite3.Connection, tipo: str) -> set[str]:
    return {
        linha[0] for linha in conn.execute(
            "SELECT name FROM sqlite_master WHERE type=? AND name NOT LIKE 'sqlite_%'", (tipo,)
        )
    }


def _existe_esquema_usuario(conn: sqlite3.Connection) -> bool:
    return any(_objetos(conn, tipo) for tipo in ("table", "view", "trigger", "index"))


def _assinatura_sql(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    return [tuple(linha) for linha in conn.execute("""
        SELECT type,name,sql FROM sqlite_master
        WHERE type IN ('table','index','trigger','view')
          AND name NOT LIKE 'sqlite_%' AND sql IS NOT NULL
        ORDER BY type,name
    """)]


def _validar_esquema(conn: sqlite3.Connection, schema: str) -> None:
    tabelas = _objetos(conn, "table")
    if tabelas != set(COLUNAS_ESPERADAS):
        raise ErroBanco("Estrutura incompatível: conjunto de tabelas diferente do esquema versão 1")
    for tabela, esperadas in COLUNAS_ESPERADAS.items():
        atuais = {linha[1] for linha in conn.execute(f'PRAGMA table_info("{tabela}")')}
        if atuais != esperadas:
            raise ErroBanco(f"Estrutura incompatível na tabela {tabela}: colunas divergentes")
    tabelas_estritas = {
        linha[1] for linha in conn.execute("PRAGMA table_list") if linha[2] == "table" and linha[5] == 1
    }
    if tabelas_estritas != set(COLUNAS_ESPERADAS):
        raise ErroBanco("Estrutura incompatível: todas as tabelas do esquema devem ser STRICT")
    verificacoes = (
        ("index", INDICES_ESPERADOS), ("trigger", TRIGGERS_ESPERADOS), ("view", VIEWS_ESPERADAS)
    )
    for tipo, esperados in verificacoes:
        presentes = _objetos(conn, tipo)
        if presentes != esperados:
            ausentes = sorted(esperados - presentes)
            adicionais = sorted(presentes - esperados)
            raise ErroBanco(
                f"Estrutura incompatível: objetos {tipo} divergentes; ausentes={ausentes}, adicionais={adicionais}"
            )
    if conn.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise ErroBanco("O banco contém referências estrangeiras inválidas")
    referencia = sqlite3.connect(":memory:")
    try:
        _executar_script_transacional(referencia, schema)
        if _assinatura_sql(conn) != _assinatura_sql(referencia):
            raise ErroBanco("Estrutura incompatível: definições SQL divergentes do esquema versão 1")
    finally:
        referencia.close()


def _executar_script_transacional(conn: sqlite3.Connection, script: str) -> None:
    """Executa statements completos sem o commit implícito de executescript()."""
    buffer = ""
    for linha in script.splitlines(keepends=True):
        buffer += linha
        if sqlite3.complete_statement(buffer):
            if buffer.strip():
                conn.execute(buffer)
            buffer = ""
    if buffer.strip():
        raise ErroBanco("schema.sql termina com uma instrução SQL incompleta")


def inicializar(caminho: str | Path | None = None) -> Path:
    """Inicializa banco novo ou valida/reaplica idempotentemente a versão suportada."""
    validar_compatibilidade()
    destino = Path(caminho) if caminho is not None else CAMINHO_BANCO_PADRAO
    if str(destino) != ":memory:":
        destino = destino.expanduser().resolve()
        destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        schema = CAMINHO_SCHEMA.read_text(encoding="utf-8")
        conn = conectar(destino)
        try:
            versao_atual = conn.execute("PRAGMA user_version").fetchone()[0]
            tem_esquema = _existe_esquema_usuario(conn)
            if versao_atual > VERSAO_ESQUEMA:
                raise ErroBanco(
                    f"Versão de esquema {versao_atual} é futura e não suportada (máxima: {VERSAO_ESQUEMA})"
                )
            if versao_atual < 0 or (versao_atual == 0 and tem_esquema):
                raise ErroBanco("Banco preexistente sem versão; recusada inicialização automática")
            if versao_atual == VERSAO_ESQUEMA:
                _validar_esquema(conn, schema)

            conn.execute("BEGIN IMMEDIATE")
            try:
                _executar_script_transacional(conn, schema)
                conn.execute(f"PRAGMA user_version = {VERSAO_ESQUEMA}")
                _validar_esquema(conn, schema)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        finally:
            conn.close()
    except (sqlite3.Error, OSError) as exc:
        raise ErroBanco(f"Falha ao inicializar banco: {exc}") from exc
    return destino
