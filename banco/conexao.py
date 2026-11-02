"""Criação centralizada e segura de conexões SQLite."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class ErroBanco(RuntimeError):
    """Erro de configuração ou operação de banco de dados."""


def conectar(caminho: str | Path, *, timeout: float = 5.0) -> sqlite3.Connection:
    """Abre uma conexão com FKs ativadas; o chamador é responsável por fechá-la."""
    if timeout < 0:
        raise ValueError("timeout não pode ser negativo")
    destino = str(caminho)
    try:
        conexao = sqlite3.connect(destino, timeout=timeout)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        conexao.execute(f"PRAGMA busy_timeout = {int(timeout * 1000)}")
        if conexao.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
            conexao.close()
            raise ErroBanco("Não foi possível ativar as chaves estrangeiras")
        return conexao
    except (sqlite3.Error, OSError) as exc:
        raise ErroBanco(f"Falha ao abrir banco SQLite: {exc}") from exc


@contextmanager
def conexao_aberta(caminho: str | Path, *, timeout: float = 5.0) -> Iterator[sqlite3.Connection]:
    """Garante commit/rollback e fechamento do recurso."""
    conn = conectar(caminho, timeout=timeout)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
