"""Testes dos serviços com banco SQLite isolado por arquivo."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import re
import sqlite3

import pytest

from banco import conectar, inicializar
import servicos.dashboard as dashboard_module
import servicos.estoque as estoque_module
from servicos import ErroServico
from servicos.autenticacao import autenticar_usuario, criar_primeiro_administrador
from servicos.cadastros import (
    cadastrar_alimento, cadastrar_doador, criar_usuario, desativar_alimento, desativar_doador,
    listar_alimentos, listar_doadores,
)
from servicos.dashboard import obter_indicadores
from servicos.doacoes import receber_doacao
from servicos.estoque import listar_estoque_por_alimento, listar_saldos_por_lote
from servicos.validacoes import (
    data_iso, quantidade_para_exibicao, quantidade_para_unidade_base, validar_data,
)

INSTANTE_FIXO = datetime(2026, 11, 2, 12, 30, 45, tzinfo=timezone(timedelta(hours=-3)))


@pytest.fixture
def db(tmp_path):
    caminho = tmp_path / "servicos.sqlite3"
    inicializar(caminho)
    return caminho


def preparar_referencias(caminho):
    conn = conectar(caminho)
    try:
        conn.executescript("""
        INSERT INTO Doador (id_doador,nome,tipo,ativo)
            VALUES (1,'Doador Exemplo','EMPRESA',1);
        INSERT INTO Alimento (id_alimento,nome,categoria,unidade_medida,ativo)
            VALUES (1,'Arroz','Grãos','KG',1);
        INSERT INTO Alimento (id_alimento,nome,categoria,unidade_medida,ativo)
            VALUES (2,'Óleo','Mercearia','L',1);
        INSERT INTO Usuario (id_usuario,nome,login,senha_hash,perfil,ativo)
            VALUES (1,'Operador','operador','hash-de-teste','OPERADOR',1);
        """)
        conn.commit()
    finally:
        conn.close()


def doacao_exemplo():
    return [
        {"id_alimento": 1, "quantidade": "2,5", "data_validade": date(2026, 11, 7), "codigo_origem": "AR-01"},
        {"id_alimento": 2, "quantidade": "1,75", "data_validade": date(2026, 12, 15), "codigo_origem": None},
    ]


def test_converte_kg_l_un_e_formata_sem_float():
    assert quantidade_para_unidade_base("2,5", "KG") == 2500
    assert quantidade_para_unidade_base(Decimal("1.75"), "L") == 1750
    assert quantidade_para_unidade_base("5", "UN") == 5
    assert quantidade_para_exibicao(2500, "KG") == "2,5"


@pytest.mark.parametrize("valor,unidade", [
    ("0", "KG"), ("-1", "L"), ("NaN", "KG"), ("Infinity", "KG"),
    ("2,5555", "KG"), ("1,5", "UN"), (1.25, "KG"), (True, "UN"),
])
def test_rejeita_quantidades_invalidas_ou_incompativeis(valor, unidade):
    with pytest.raises(ErroServico):
        quantidade_para_unidade_base(valor, unidade)


@pytest.mark.parametrize("valor", ["2026-02-30", "03/11/2026", "2026-1-01", "2026-11-02T00:00:00"])
def test_rejeita_datas_invalidas_ou_formato_nao_canonico(valor):
    with pytest.raises(ErroServico):
        validar_data(valor)


def test_cadastro_desativacao_logica_e_unicidade(db):
    id_doador = cadastrar_doador("  Mercado Central ", "EMPRESA", email="contato@mercado.example", caminho=db)
    with pytest.raises(ErroServico, match="Já existe um doador"):
        cadastrar_doador("mercado central", "EMPRESA", caminho=db)
    assert len(listar_doadores(caminho=db)) == 1
    desativar_doador(id_doador, caminho=db)
    assert listar_doadores(caminho=db) == []
    assert listar_doadores(incluir_inativos=True, caminho=db)[0]["ativo"] == 0

    id_alimento = cadastrar_alimento("Feijão", "Grãos", "KG", caminho=db)
    with pytest.raises(ErroServico, match="Já existe um alimento"):
        cadastrar_alimento("feijão", "Grãos", "KG", caminho=db)
    desativar_alimento(id_alimento, caminho=db)
    assert listar_alimentos(caminho=db) == []
    assert listar_alimentos(incluir_inativos=True, caminho=db)[0]["unidade_medida"] == "KG"


def test_recebe_doacao_com_multiplos_alimentos_lotes_entradas_e_saldos(db):
    preparar_referencias(db)
    resultado = receber_doacao(1, 1, doacao_exemplo(), caminho=db, instante=INSTANTE_FIXO)
    assert resultado["id_doacao"] == 1
    assert len(resultado["codigos_lote"]) == 2
    assert all(re.fullmatch(r"CA-2026-[0-9A-F]{8}", codigo) for codigo in resultado["codigos_lote"])
    assert resultado["data_recebimento"] == "2026-11-02"

    conn = conectar(db)
    try:
        assert conn.execute("SELECT COUNT(*) FROM Doacao").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM Lote").fetchone()[0] == 2
        entradas = conn.execute("SELECT tipo,quantidade,data_movimentacao FROM MovimentacaoEstoque ORDER BY id_alimento").fetchall()
        assert [(row["tipo"], row["quantidade"]) for row in entradas] == [
            ("ENTRADA_DOACAO", 2500), ("ENTRADA_DOACAO", 1750),
        ]
        assert all(row["data_movimentacao"] == "2026-11-02T12:30:45-03:00" for row in entradas)
    finally:
        conn.close()

    saldos = listar_estoque_por_alimento(data_referencia=date(2026, 11, 2), caminho=db)
    assert [(row["alimento"], row["saldo"], row["unidade_medida"]) for row in saldos] == [
        ("Arroz", 2500, "KG"), ("Óleo", 1750, "L"),
    ]


def test_recebimento_falha_no_meio_faz_rollback_integral(db):
    preparar_referencias(db)
    conn = conectar(db)
    try:
        conn.execute("""
            CREATE TRIGGER falha_teste_segundo_alimento
            BEFORE INSERT ON MovimentacaoEstoque
            WHEN NEW.id_alimento=2
            BEGIN SELECT RAISE(ABORT,'falha controlada no teste'); END
        """)
        conn.commit()
    finally:
        conn.close()
    with pytest.raises(ErroServico, match="nenhuma alteração foi gravada"):
        receber_doacao(1, 1, doacao_exemplo(), caminho=db, instante=INSTANTE_FIXO)
    conn = conectar(db)
    try:
        assert conn.execute("SELECT COUNT(*) FROM Doacao").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM Lote").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM MovimentacaoEstoque").fetchone()[0] == 0
    finally:
        conn.close()


def test_nao_recebe_com_doador_alimento_ou_usuario_inativo(db):
    preparar_referencias(db)
    desativar_doador(1, caminho=db)
    with pytest.raises(ErroServico, match="doador ativo"):
        receber_doacao(1, 1, doacao_exemplo(), caminho=db, instante=INSTANTE_FIXO)

    conn = conectar(db)
    try:
        conn.execute("UPDATE Doador SET ativo=1 WHERE id_doador=1")
        conn.commit()
    finally:
        conn.close()
    desativar_alimento(1, caminho=db)
    with pytest.raises(ErroServico, match="inexistente ou inativo"):
        receber_doacao(1, 1, doacao_exemplo(), caminho=db, instante=INSTANTE_FIXO)

    conn = conectar(db)
    try:
        conn.execute("UPDATE Alimento SET ativo=1 WHERE id_alimento=1")
        conn.execute("UPDATE Usuario SET ativo=0 WHERE id_usuario=1")
        conn.commit()
    finally:
        conn.close()
    with pytest.raises(ErroServico, match="usuário responsável"):
        receber_doacao(1, 1, doacao_exemplo(), caminho=db, instante=INSTANTE_FIXO)


def test_estoque_separa_disponivel_vencido_e_proximo_do_vencimento(db):
    preparar_referencias(db)
    itens = [
        {"id_alimento": 1, "quantidade": "1", "data_validade": date(2026, 11, 9)},
        {"id_alimento": 1, "quantidade": "2", "data_validade": date(2026, 11, 1)},
        {"id_alimento": 2, "quantidade": "1", "data_validade": date(2026, 11, 20)},
    ]
    receber_doacao(1, 1, itens, caminho=db, instante=INSTANTE_FIXO)
    todos = listar_saldos_por_lote(data_referencia=date(2026, 11, 2), caminho=db)
    assert len(todos) == 3
    assert len(listar_saldos_por_lote(categoria="vencido", data_referencia=date(2026, 11, 2), caminho=db)) == 1
    proximos = listar_saldos_por_lote(categoria="proximo", data_referencia=date(2026, 11, 2), caminho=db)
    assert [row["data_validade"] for row in proximos] == ["2026-11-09"]
    assert listar_estoque_por_alimento(categoria="vencido", data_referencia=date(2026, 11, 2), caminho=db)[0]["saldo"] == 2000


def test_dashboard_vazio_e_com_dados_reais(db):
    vazio = obter_indicadores(data_referencia=date(2026, 11, 2), caminho=db)
    assert vazio["banco_vazio"] is True
    assert vazio["doacoes_recebidas"] == 0
    assert vazio["estoque_por_alimento"] == []
    preparar_referencias(db)
    receber_doacao(1, 1, doacao_exemplo(), caminho=db, instante=INSTANTE_FIXO)
    dados = obter_indicadores(data_referencia=date(2026, 11, 2), caminho=db)
    assert dados["banco_vazio"] is False
    assert dados["doacoes_recebidas"] == 1
    assert dados["lotes_disponiveis"] == 2
    assert dados["alimentos_disponiveis"] == 2
    assert len(dados["movimentacoes_recentes"]) == 2
    assert len(dados["lotes_proximos_vencimento"]) == 1
    assert dados["lotes_proximos_vencimento"][0]["data_validade"] == "2026-11-07"


def test_dashboard_usa_uma_conexao_e_finaliza_transacao(db, monkeypatch):
    conexao_real = dashboard_module.conectar
    conexoes = []
    instrucoes = []

    def conectar_monitorado(caminho):
        conn = conexao_real(caminho)
        conn.set_trace_callback(instrucoes.append)
        conexoes.append(conn)
        return conn

    def conexao_extra_proibida(*args, **kwargs):
        pytest.fail("O dashboard abriu uma conexão extra pelas consultas de estoque")

    monkeypatch.setattr(dashboard_module, "conectar", conectar_monitorado)
    monkeypatch.setattr(estoque_module, "conectar", conexao_extra_proibida)

    resultado = dashboard_module.obter_indicadores(data_referencia=date(2026, 11, 2), caminho=db)

    assert resultado["banco_vazio"] is True
    assert len(conexoes) == 1
    assert any(instrucao.strip().upper() == "BEGIN" for instrucao in instrucoes)
    assert any(instrucao.strip().upper() == "COMMIT" for instrucao in instrucoes)
    with pytest.raises(sqlite3.ProgrammingError):
        conexoes[0].execute("SELECT 1")


def test_dashboard_reverte_e_fecha_conexao_se_consulta_falhar(db, monkeypatch):
    conexao_real = dashboard_module.conectar
    conexoes = []
    instrucoes = []

    def conectar_monitorado(caminho):
        conn = conexao_real(caminho)
        conn.set_trace_callback(instrucoes.append)
        conexoes.append(conn)
        return conn

    def consulta_com_falha(*args, **kwargs):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(dashboard_module, "conectar", conectar_monitorado)
    monkeypatch.setattr(dashboard_module, "_listar_movimentacoes_recentes_conn", consulta_com_falha)

    with pytest.raises(RuntimeError, match="falha simulada"):
        dashboard_module.obter_indicadores(data_referencia=date(2026, 11, 2), caminho=db)

    assert any(instrucao.strip().upper() == "ROLLBACK" for instrucao in instrucoes)
    with pytest.raises(sqlite3.ProgrammingError):
        conexoes[0].execute("SELECT 1")


def test_primeiro_administrador_hash_e_autenticacao(db):
    id_usuario = criar_primeiro_administrador("Admin", "admin", "Uma senha bem longa! 42", caminho=db)
    conn = conectar(db)
    try:
        senha_hash = conn.execute("SELECT senha_hash FROM Usuario WHERE id_usuario=?", (id_usuario,)).fetchone()[0]
        assert senha_hash.startswith("pbkdf2_sha256$600000$")
        assert "Uma senha bem longa! 42" not in senha_hash
    finally:
        conn.close()
    assert autenticar_usuario("ADMIN", "Uma senha bem longa! 42", caminho=db)["id_usuario"] == id_usuario
    assert autenticar_usuario("admin", "senha errada", caminho=db) is None
    with pytest.raises(ErroServico, match="já foi criado"):
        criar_primeiro_administrador("Outro", "outro", "Outra senha longa! 42", caminho=db)


def test_criar_usuario_permite_somente_perfis_operacionais(db):
    criar_primeiro_administrador("Admin", "admin", "Uma senha bem longa! 42", caminho=db)

    with pytest.raises(ErroServico, match="somente os perfis ESTOQUE e OPERADOR"):
        criar_usuario("Outro admin", "admin2", "Outra senha longa! 42", "ADMINISTRADOR", caminho=db)

    id_estoque = criar_usuario("Pessoa estoque", "estoque", "Senha estoque longa! 42", "ESTOQUE", caminho=db)
    id_operador = criar_usuario("Pessoa operação", "operador", "Senha operador longa! 42", "OPERADOR", caminho=db)
    conn = conectar(db)
    try:
        perfis = dict(conn.execute(
            "SELECT id_usuario,perfil FROM Usuario WHERE id_usuario IN (?,?)", (id_estoque, id_operador)
        ))
        assert perfis == {id_estoque: "ESTOQUE", id_operador: "OPERADOR"}
        assert conn.execute("SELECT COUNT(*) FROM Usuario").fetchone()[0] == 3
    finally:
        conn.close()
