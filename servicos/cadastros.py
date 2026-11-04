"""Cadastros de doadores, alimentos e usuários responsáveis."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from banco.conexao import conectar, conexao_aberta
from banco.inicializacao import CAMINHO_BANCO_PADRAO
from servicos import ErroServico
from servicos.autenticacao import gerar_hash_senha
from servicos.validacoes import (
    texto_obrigatorio,
    texto_opcional,
    validar_email,
    validar_tipo_doador,
    validar_unidade,
)

logger = logging.getLogger(__name__)


def cadastrar_doador(
    nome: object,
    tipo: object,
    *,
    telefone: object | None = None,
    email: object | None = None,
    caminho: str | Path | None = None,
) -> int:
    nome_ok = texto_obrigatorio(nome, "o nome do doador")
    tipo_ok = validar_tipo_doador(tipo)
    telefone_ok = texto_opcional(telefone)
    if telefone_ok and len(telefone_ok) > 30:
        raise ErroServico("O telefone deve ter no máximo 30 caracteres.")
    email_ok = validar_email(email)
    try:
        with conexao_aberta(caminho or CAMINHO_BANCO_PADRAO) as conn:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute("SELECT 1 FROM Doador WHERE nome=? COLLATE NOCASE", (nome_ok,)).fetchone():
                raise ErroServico("Já existe um doador com esse nome.")
            result = conn.execute(
                "INSERT INTO Doador (nome,tipo,telefone,email,ativo) VALUES (?,?,?,?,1)",
                (nome_ok, tipo_ok, telefone_ok, email_ok),
            )
            return int(result.lastrowid)
    except sqlite3.IntegrityError as exc:
        logger.exception("Falha de integridade ao cadastrar doador")
        raise ErroServico("Não foi possível cadastrar o doador; confira os dados informados.") from exc


def listar_doadores(*, incluir_inativos: bool = False, caminho: str | Path | None = None) -> list[dict[str, object]]:
    conn = conectar(caminho or CAMINHO_BANCO_PADRAO)
    try:
        filtro = "" if incluir_inativos else "WHERE ativo=1"
        return [dict(row) for row in conn.execute(
            f"SELECT id_doador,nome,tipo,telefone,email,ativo FROM Doador {filtro} ORDER BY nome COLLATE NOCASE"
        )]
    finally:
        conn.close()


def desativar_doador(id_doador: int, *, caminho: str | Path | None = None) -> None:
    with conexao_aberta(caminho or CAMINHO_BANCO_PADRAO) as conn:
        conn.execute("BEGIN IMMEDIATE")
        result = conn.execute("UPDATE Doador SET ativo=0 WHERE id_doador=? AND ativo=1", (id_doador,))
        if result.rowcount == 0:
            raise ErroServico("Doador inexistente ou já desativado.")


def cadastrar_alimento(
    nome: object,
    categoria: object,
    unidade_medida: object,
    *,
    caminho: str | Path | None = None,
) -> int:
    nome_ok = texto_obrigatorio(nome, "o nome do alimento")
    categoria_ok = texto_obrigatorio(categoria, "a categoria")
    unidade_ok = validar_unidade(unidade_medida)
    try:
        with conexao_aberta(caminho or CAMINHO_BANCO_PADRAO) as conn:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute("SELECT 1 FROM Alimento WHERE nome=? COLLATE NOCASE", (nome_ok,)).fetchone():
                raise ErroServico("Já existe um alimento com esse nome.")
            result = conn.execute(
                "INSERT INTO Alimento (nome,categoria,unidade_medida,ativo) VALUES (?,?,?,1)",
                (nome_ok, categoria_ok, unidade_ok),
            )
            return int(result.lastrowid)
    except sqlite3.IntegrityError as exc:
        logger.exception("Falha de integridade ao cadastrar alimento")
        raise ErroServico("Não foi possível cadastrar o alimento; confira os dados informados.") from exc


def listar_alimentos(*, incluir_inativos: bool = False, caminho: str | Path | None = None) -> list[dict[str, object]]:
    conn = conectar(caminho or CAMINHO_BANCO_PADRAO)
    try:
        filtro = "" if incluir_inativos else "WHERE ativo=1"
        return [dict(row) for row in conn.execute(
            f"SELECT id_alimento,nome,categoria,unidade_medida,ativo FROM Alimento {filtro} ORDER BY nome COLLATE NOCASE"
        )]
    finally:
        conn.close()


def desativar_alimento(id_alimento: int, *, caminho: str | Path | None = None) -> None:
    with conexao_aberta(caminho or CAMINHO_BANCO_PADRAO) as conn:
        conn.execute("BEGIN IMMEDIATE")
        result = conn.execute("UPDATE Alimento SET ativo=0 WHERE id_alimento=? AND ativo=1", (id_alimento,))
        if result.rowcount == 0:
            raise ErroServico("Alimento inexistente ou já desativado.")


def criar_usuario(
    nome: object,
    login: object,
    senha: object,
    perfil: object = "OPERADOR",
    *,
    caminho: str | Path | None = None,
) -> int:
    nome_ok = texto_obrigatorio(nome, "o nome")
    login_ok = texto_obrigatorio(login, "o login", minimo=3)
    perfil_ok = str(perfil or "").strip().upper()
    if perfil_ok not in {"ESTOQUE", "OPERADOR"}:
        raise ErroServico("A criação de usuários permite somente os perfis ESTOQUE e OPERADOR.")
    senha_hash = gerar_hash_senha(senha)
    try:
        with conexao_aberta(caminho or CAMINHO_BANCO_PADRAO) as conn:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute("SELECT 1 FROM Usuario WHERE login=? COLLATE NOCASE", (login_ok,)).fetchone():
                raise ErroServico("Já existe um usuário com esse login.")
            result = conn.execute(
                "INSERT INTO Usuario (nome,login,senha_hash,perfil,ativo) VALUES (?,?,?,?,1)",
                (nome_ok, login_ok, senha_hash, perfil_ok),
            )
            return int(result.lastrowid)
    except sqlite3.IntegrityError as exc:
        logger.exception("Falha de integridade ao cadastrar usuário")
        raise ErroServico("Não foi possível cadastrar o usuário; confira os dados informados.") from exc
