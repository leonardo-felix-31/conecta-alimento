"""Persistência SQLite do Conecta Alimento."""

from banco.conexao import ErroBanco, conectar, conexao_aberta
from banco.inicializacao import inicializar, validar_compatibilidade

__all__ = ["ErroBanco", "conectar", "conexao_aberta", "inicializar", "validar_compatibilidade"]
