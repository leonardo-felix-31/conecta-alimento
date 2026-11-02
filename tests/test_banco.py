"""Verificações de integração do esquema em arquivos SQLite temporários."""

import sqlite3

import pytest

import banco.inicializacao as inicializacao
from banco import ErroBanco, conectar, inicializar


@pytest.fixture
def db(tmp_path):
    caminho = tmp_path / "teste.sqlite3"
    inicializar(caminho)
    return caminho


def seed(conn):
    conn.executescript("""
    INSERT INTO Doador (id_doador,nome,tipo,telefone,email,ativo)
        VALUES (1,'Doador','PESSOA_FISICA',NULL,NULL,1);
    INSERT INTO Alimento (id_alimento,nome,categoria,unidade_medida,ativo)
        VALUES (1,'Arroz','Grãos','KG',1);
    INSERT INTO Instituicao (id_instituicao,nome,tipo,responsavel,telefone,email,endereco,ativo)
        VALUES (1,'Instituição','ASSOCIACAO','Responsável',NULL,NULL,NULL,1);
    INSERT INTO Usuario (id_usuario,nome,login,senha_hash,perfil,ativo)
        VALUES (1,'Operador','op1','hash','OPERADOR',1);
    INSERT INTO Doacao (id_doacao,id_doador,id_usuario,data_recebimento,observacao)
        VALUES (1,1,1,'2026-01-01',NULL);
    INSERT INTO Lote (id_lote,id_doacao,id_alimento,codigo_lote,codigo_origem,data_validade,observacao)
        VALUES (1,1,1,'CA-001',NULL,'2026-12-31',NULL);
    INSERT INTO MovimentacaoEstoque
        (id_movimentacao,id_lote,id_alimento,id_usuario,tipo,quantidade,data_movimentacao,
         motivo,id_distribuicao,id_item_solicitacao,id_solicitacao,id_movimentacao_original)
        VALUES (1,1,1,1,'ENTRADA_DOACAO',30000,'2026-01-01T10:00:00-03:00',NULL,NULL,NULL,NULL,NULL);
    INSERT INTO Solicitacao (id_solicitacao,id_instituicao,id_usuario,data_solicitacao,status,observacao)
        VALUES (1,1,1,'2026-01-01','ABERTA',NULL);
    INSERT INTO ItemSolicitacao (id_item_solicitacao,id_solicitacao,id_alimento,quantidade_solicitada)
        VALUES (1,1,1,50000);
    INSERT INTO Distribuicao (id_distribuicao,id_solicitacao,id_usuario,data_distribuicao,observacao)
        VALUES (1,1,1,'2026-01-02',NULL);
    INSERT INTO Lote (id_lote,id_doacao,id_alimento,codigo_lote,codigo_origem,data_validade,observacao)
        VALUES (2,1,1,'CA-002',NULL,'2026-12-31',NULL);
    INSERT INTO MovimentacaoEstoque
        (id_movimentacao,id_lote,id_alimento,id_usuario,tipo,quantidade,data_movimentacao,
         motivo,id_distribuicao,id_item_solicitacao,id_solicitacao,id_movimentacao_original)
        VALUES (2,2,1,1,'ENTRADA_DOACAO',40000,'2026-01-01T10:00:00-03:00',NULL,NULL,NULL,NULL,NULL);
    """)


def inserir_movimento(conn, *, id_movimentacao, id_lote=1, tipo, quantidade,
                      timestamp="2026-01-02T10:00:00-03:00", motivo=None,
                      distribuicao=None, item=None, solicitacao=None, original=None):
    conn.execute("""
        INSERT INTO MovimentacaoEstoque
            (id_movimentacao,id_lote,id_alimento,id_usuario,tipo,quantidade,data_movimentacao,
             motivo,id_distribuicao,id_item_solicitacao,id_solicitacao,id_movimentacao_original)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (id_movimentacao,id_lote,1,1,tipo,quantidade,timestamp,motivo,
          distribuicao,item,solicitacao,original))


def test_esquema_completo_idempotente_sem_saldo_e_com_objetos(db):
    conn = conectar(db)
    try:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        seed(conn)
        conn.commit()
        inicializar(db)
    finally:
        conn.close()

    outra = conectar(db)
    try:
        assert outra.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert outra.execute("PRAGMA user_version").fetchone()[0] == inicializacao.VERSAO_ESQUEMA
        assert outra.execute("SELECT count(*) FROM Doador").fetchone()[0] == 1
        tabelas = {r[0] for r in outra.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        assert tabelas == set(inicializacao.COLUNAS_ESPERADAS)
        assert {r[0] for r in outra.execute("SELECT name FROM sqlite_master WHERE type='trigger'")} == inicializacao.TRIGGERS_ESPERADOS
        assert {r[0] for r in outra.execute("SELECT name FROM sqlite_master WHERE type='view'")} == inicializacao.VIEWS_ESPERADAS
        indices = {r[0] for r in outra.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")}
        assert indices == inicializacao.INDICES_ESPERADOS
        assert "saldo" not in {r[1] for r in outra.execute("PRAGMA table_info(Lote)")}
        assert outra.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        outra.close()


def test_distribuicao_parcial_multiplos_lotes_saldo_e_estorno(db):
    conn = conectar(db)
    try:
        seed(conn)
        inserir_movimento(conn,id_movimentacao=3,tipo='SAIDA_DISTRIBUICAO',quantidade=20000,distribuicao=1,item=1,solicitacao=1)
        inserir_movimento(conn,id_movimentacao=4,id_lote=2,tipo='SAIDA_DISTRIBUICAO',quantidade=5000,distribuicao=1,item=1,solicitacao=1)
        assert conn.execute("SELECT saldo FROM vw_saldo_por_lote WHERE id_lote=1").fetchone()[0] == 10000
        assert conn.execute("SELECT quantidade_pendente FROM vw_atendimento_itens WHERE id_item_solicitacao=1").fetchone()[0] == 25000
        inserir_movimento(conn,id_movimentacao=5,tipo='ESTORNO_DISTRIBUICAO',quantidade=20000,motivo='Correção',distribuicao=1,item=1,solicitacao=1,original=3)
        assert conn.execute("SELECT saldo FROM vw_saldo_por_lote WHERE id_lote=1").fetchone()[0] == 30000
        assert conn.execute("SELECT quantidade_entregue FROM vw_atendimento_itens WHERE id_item_solicitacao=1").fetchone()[0] == 5000
    finally:
        conn.close()


def test_bloqueia_saldo_negativo(db):
    conn = conectar(db)
    try:
        seed(conn)
        with pytest.raises(sqlite3.IntegrityError, match="Saldo insuficiente"):
            inserir_movimento(conn,id_movimentacao=3,tipo='AJUSTE_SAIDA',quantidade=30001,motivo='motivo')
    finally:
        conn.close()


def test_bloqueia_quantidade_acima_do_solicitado(db):
    conn = conectar(db)
    try:
        seed(conn)
        inserir_movimento(conn,id_movimentacao=3,tipo='AJUSTE_ENTRADA',quantidade=50000,motivo='Contagem')
        with pytest.raises(sqlite3.IntegrityError, match="acima do pendente"):
            inserir_movimento(conn,id_movimentacao=4,tipo='SAIDA_DISTRIBUICAO',quantidade=50001,distribuicao=1,item=1,solicitacao=1)
    finally:
        conn.close()


def test_bloqueia_lote_vencido_estorno_parcial_e_duplicado(db):
    conn = conectar(db)
    try:
        seed(conn)
        conn.execute("UPDATE Lote SET data_validade='2026-01-01' WHERE id_lote=1")
        with pytest.raises(sqlite3.IntegrityError, match="Saldo insuficiente ou lote vencido"):
            inserir_movimento(conn,id_movimentacao=3,tipo='SAIDA_DISTRIBUICAO',quantidade=1,distribuicao=1,item=1,solicitacao=1)
        conn.execute("UPDATE Lote SET data_validade='2026-12-31' WHERE id_lote=1")
        inserir_movimento(conn,id_movimentacao=3,tipo='SAIDA_DISTRIBUICAO',quantidade=1000,distribuicao=1,item=1,solicitacao=1)
        with pytest.raises(sqlite3.IntegrityError, match="integralmente"):
            inserir_movimento(conn,id_movimentacao=4,tipo='ESTORNO_DISTRIBUICAO',quantidade=999,motivo='erro',distribuicao=1,item=1,solicitacao=1,original=3)
        inserir_movimento(conn,id_movimentacao=5,tipo='ESTORNO_DISTRIBUICAO',quantidade=1000,motivo='erro',distribuicao=1,item=1,solicitacao=1,original=3)
        with pytest.raises(sqlite3.IntegrityError, match="UNIQUE constraint failed: MovimentacaoEstoque.id_movimentacao_original"):
            inserir_movimento(conn,id_movimentacao=6,tipo='ESTORNO_DISTRIBUICAO',quantidade=1000,motivo='erro',distribuicao=1,item=1,solicitacao=1,original=3)
    finally:
        conn.close()


@pytest.mark.parametrize("timestamp", [
    "2026-01-01T10:00:00-03:00", "2026-01-01T10:00:00+14:00", "2026-01-01T10:00:00-14:00",
])
def test_timestamp_iso_valido(timestamp, db):
    conn = conectar(db)
    try:
        seed(conn)
        inserir_movimento(conn,id_movimentacao=3,tipo='AJUSTE_ENTRADA',quantidade=1,timestamp=timestamp,motivo='Teste')
    finally:
        conn.close()


@pytest.mark.parametrize("timestamp", [
    "2026x01-01T10:00:00-03:00",  # caractere não numérico na data
    "2026-02-30T10:00:00-03:00",  # dia inexistente
    "2026-01-01T25:00:00-03:00",  # hora inválida
    "2026-01-01T10:60:00-03:00",  # minuto inválido
    "2026-01-01T10:00:60-03:00",  # segundo inválido
    "2026-01-01T10:00:00+14:01",  # limite superior excedido
    "2026-01-01T10:00:00-15:00",  # horas fora da faixa
    "2026-01-01T10:00:00+13:60",  # minutos fora da faixa
])
def test_timestamp_iso_invalido_e_rejeitado(timestamp, db):
    conn = conectar(db)
    try:
        seed(conn)
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            inserir_movimento(conn,id_movimentacao=3,tipo='AJUSTE_ENTRADA',quantidade=1,timestamp=timestamp,motivo='Teste')
    finally:
        conn.close()


@pytest.mark.parametrize("tabela,coluna", [
    ("Doacao", "data_recebimento"), ("Lote", "data_validade"),
    ("Solicitacao", "data_solicitacao"), ("Distribuicao", "data_distribuicao"),
])
def test_datas_de_negocio_rejeitam_dias_inexistentes(tabela, coluna, db):
    conn = conectar(db)
    try:
        seed(conn)
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            conn.execute(f"UPDATE {tabela} SET {coluna}='2026-02-30' WHERE rowid=1")
    finally:
        conn.close()


def test_datas_de_distribuicao_e_validade_ficam_fixadas_apos_saida_e_estorno(db):
    conn = conectar(db)
    try:
        seed(conn)
        # Correções são permitidas enquanto ainda não existe saída.
        conn.execute("UPDATE Distribuicao SET data_distribuicao='2026-01-03' WHERE id_distribuicao=1")
        conn.execute("UPDATE Lote SET data_validade='2026-12-30' WHERE id_lote=1")
        inserir_movimento(conn,id_movimentacao=3,tipo='SAIDA_DISTRIBUICAO',quantidade=1000,distribuicao=1,item=1,solicitacao=1)
        inserir_movimento(conn,id_movimentacao=4,tipo='ESTORNO_DISTRIBUICAO',quantidade=1000,motivo='Estorno',distribuicao=1,item=1,solicitacao=1,original=3)
        with pytest.raises(sqlite3.IntegrityError, match="Data da distribuição não pode mudar"):
            conn.execute("UPDATE Distribuicao SET data_distribuicao='2026-01-01' WHERE id_distribuicao=1")
        with pytest.raises(sqlite3.IntegrityError, match="Validade do lote não pode mudar"):
            conn.execute("UPDATE Lote SET data_validade='2025-12-31' WHERE id_lote=1")
    finally:
        conn.close()


def test_banco_sem_versao_com_objetos_e_recusado_sem_alteracao(tmp_path):
    caminho = tmp_path / "legado.sqlite3"
    conn = sqlite3.connect(caminho)
    conn.execute("CREATE TABLE legado (id INTEGER PRIMARY KEY)")
    conn.execute("INSERT INTO legado (id) VALUES (7)")
    conn.commit()
    conn.close()
    with pytest.raises(ErroBanco, match="sem versão"):
        inicializar(caminho)
    conn = sqlite3.connect(caminho)
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 0
        assert conn.execute("SELECT id FROM legado").fetchone()[0] == 7
    finally:
        conn.close()


def test_versao_futura_e_rejeitada_sem_alteracao(tmp_path):
    caminho = tmp_path / "futuro.sqlite3"
    conn = sqlite3.connect(caminho)
    conn.execute("CREATE TABLE preservada (id INTEGER)")
    conn.execute("INSERT INTO preservada (id) VALUES (9)")
    conn.execute("PRAGMA user_version = 99")
    conn.commit()
    conn.close()
    with pytest.raises(ErroBanco, match="futura e não suportada"):
        inicializar(caminho)
    conn = sqlite3.connect(caminho)
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 99
        assert conn.execute("SELECT id FROM preservada").fetchone()[0] == 9
    finally:
        conn.close()


def test_versao_atual_com_estrutura_incompativel_e_rejeitada(tmp_path):
    caminho = tmp_path / "incompativel.sqlite3"
    conn = sqlite3.connect(caminho)
    conn.execute("CREATE TABLE Doador (id_doador INTEGER PRIMARY KEY)")
    conn.execute(f"PRAGMA user_version = {inicializacao.VERSAO_ESQUEMA}")
    conn.commit()
    conn.close()
    with pytest.raises(ErroBanco, match="Estrutura incompatível"):
        inicializar(caminho)


def test_versao_atual_com_definicao_sql_alterada_e_rejeitada(db):
    conn = conectar(db)
    try:
        conn.execute("DROP VIEW vw_saldo_por_lote")
        conn.execute("CREATE VIEW vw_saldo_por_lote AS SELECT id_lote, 0 AS saldo FROM Lote")
    finally:
        conn.close()
    with pytest.raises(ErroBanco, match="Estrutura incompatível"):
        inicializar(db)


def test_falha_no_script_reverte_esquema_e_user_version(tmp_path, monkeypatch):
    caminho = tmp_path / "falha.sqlite3"
    schema_ruim = tmp_path / "schema_ruim.sql"
    schema_ruim.write_text("CREATE TABLE temporaria (id INTEGER);\nCREATE TABLE SQL inválido;\n", encoding="utf-8")
    monkeypatch.setattr(inicializacao, "CAMINHO_SCHEMA", schema_ruim)
    with pytest.raises(ErroBanco):
        inicializar(caminho)
    conn = sqlite3.connect(caminho)
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 0
        assert conn.execute("SELECT name FROM sqlite_master WHERE name='temporaria'").fetchone() is None
    finally:
        conn.close()


def test_falha_apos_definir_versao_reverte_esquema_e_user_version(tmp_path, monkeypatch):
    caminho = tmp_path / "falha_validacao.sqlite3"

    def falhar_validacao(conn, schema):
        raise ErroBanco("Falha simulada na validação final")

    monkeypatch.setattr(inicializacao, "_validar_esquema", falhar_validacao)
    with pytest.raises(ErroBanco, match="Falha simulada"):
        inicializar(caminho)
    conn = sqlite3.connect(caminho)
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 0
        assert conn.execute("SELECT name FROM sqlite_master WHERE name='Doador'").fetchone() is None
    finally:
        conn.close()
