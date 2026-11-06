"""Autenticação local mínima para atribuir usuários às operações."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import sqlite3
from pathlib import Path

from banco.conexao import ErroBanco, conectar, conexao_aberta
from banco.inicializacao import CAMINHO_BANCO_PADRAO
from servicos import ErroServico
from servicos.validacoes import validar_senha, texto_obrigatorio

ITERACOES_PBKDF2 = 600_000
_TAMANHO_SALT = 16
_TAMANHO_HASH = 32
logger = logging.getLogger(__name__)


def _derivar(senha: str, salt: bytes, iteracoes: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, iteracoes, dklen=_TAMANHO_HASH)


def gerar_hash_senha(senha: object) -> str:
    senha_validada = validar_senha(senha)
    salt = os.urandom(_TAMANHO_SALT)
    digest = _derivar(senha_validada, salt, ITERACOES_PBKDF2)
    return f"pbkdf2_sha256${ITERACOES_PBKDF2}${salt.hex()}${digest.hex()}"


def verificar_senha(senha: object, senha_hash: object) -> bool:
    try:
        algoritmo, iteracoes_txt, salt_hex, digest_hex = str(senha_hash).split("$", 3)
        iteracoes = int(iteracoes_txt)
        if algoritmo != "pbkdf2_sha256" or not 100_000 <= iteracoes <= 2_000_000:
            return False
        salt = bytes.fromhex(salt_hex)
        esperado = bytes.fromhex(digest_hex)
        if len(salt) != _TAMANHO_SALT or len(esperado) != _TAMANHO_HASH:
            return False
        tentativa = _derivar(str(senha), salt, iteracoes)
        return hmac.compare_digest(tentativa, esperado)
    except (ValueError, TypeError):
        return False


def verificar_segredo_bootstrap(configurado: object, informado: object) -> bool:
    """Compara o segredo de bootstrap sem comparação de tempo variável."""
    esperado = str(configurado or "")
    recebido = str(informado or "")
    return bool(esperado) and hmac.compare_digest(
        esperado.encode("utf-8"), recebido.encode("utf-8")
    )


def contar_usuarios(caminho: str | Path | None = None) -> int:
    conn = conectar(caminho or CAMINHO_BANCO_PADRAO)
    try:
        return int(conn.execute("SELECT COUNT(*) FROM Usuario").fetchone()[0])
    finally:
        conn.close()


def criar_primeiro_administrador(
    nome: object, login: object, senha: object, *, caminho: str | Path | None = None
) -> int:
    nome_validado = texto_obrigatorio(nome, "o nome")
    login_validado = texto_obrigatorio(login, "o login", minimo=3)
    senha_hash = gerar_hash_senha(senha)
    try:
        with conexao_aberta(caminho or CAMINHO_BANCO_PADRAO) as conn:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute("SELECT 1 FROM Usuario LIMIT 1").fetchone():
                raise ErroServico("O primeiro administrador já foi criado.")
            cursor = conn.execute(
                "INSERT INTO Usuario (nome,login,senha_hash,perfil,ativo) VALUES (?,?,?,'ADMINISTRADOR',1)",
                (nome_validado, login_validado, senha_hash),
            )
            return int(cursor.lastrowid)
    except sqlite3.IntegrityError as exc:
        logger.exception("Falha de integridade ao criar o primeiro administrador")
        raise ErroServico("Não foi possível criar o administrador. Verifique o login informado.") from exc
    except ErroBanco:
        raise


def autenticar_usuario(
    login: object, senha: object, *, caminho: str | Path | None = None
) -> dict[str, object] | None:
    login_validado = str(login or "").strip()
    senha_texto = str(senha or "")
    conn = conectar(caminho or CAMINHO_BANCO_PADRAO)
    try:
        usuario = conn.execute(
            "SELECT id_usuario,nome,login,senha_hash,perfil,ativo FROM Usuario WHERE login = ? COLLATE NOCASE",
            (login_validado,),
        ).fetchone()
        if usuario is None or usuario["ativo"] != 1:
            # Mantém o custo de derivação próximo ao caminho de login existente.
            _derivar(senha_texto, bytes(_TAMANHO_SALT), ITERACOES_PBKDF2)
            return None
        if not verificar_senha(senha_texto, usuario["senha_hash"]):
            return None
        return {chave: usuario[chave] for chave in ("id_usuario", "nome", "login", "perfil")}
    finally:
        conn.close()


def obter_usuario_ativo(id_usuario: int, *, caminho: str | Path | None = None) -> dict[str, object] | None:
    conn = conectar(caminho or CAMINHO_BANCO_PADRAO)
    try:
        usuario = conn.execute(
            "SELECT id_usuario,nome,login,perfil FROM Usuario WHERE id_usuario=? AND ativo=1",
            (id_usuario,),
        ).fetchone()
        return dict(usuario) if usuario else None
    finally:
        conn.close()
