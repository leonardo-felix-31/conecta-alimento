PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Doador (
    id_doador INTEGER PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    tipo TEXT NOT NULL CHECK (tipo IN ('PESSOA_FISICA','EMPRESA','ORGANIZACAO')),
    telefone TEXT,
    email TEXT,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0,1))
) STRICT;

CREATE TABLE IF NOT EXISTS Alimento (
    id_alimento INTEGER PRIMARY KEY,
    nome TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (length(trim(nome)) > 0),
    categoria TEXT NOT NULL CHECK (length(trim(categoria)) > 0),
    unidade_medida TEXT NOT NULL CHECK (unidade_medida IN ('KG','L','UN')),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0,1))
) STRICT;

CREATE TABLE IF NOT EXISTS Instituicao (
    id_instituicao INTEGER PRIMARY KEY,
    nome TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (length(trim(nome)) > 0),
    tipo TEXT NOT NULL CHECK (tipo IN ('COZINHA_SOLIDARIA','ASSOCIACAO','OUTRA')),
    responsavel TEXT NOT NULL CHECK (length(trim(responsavel)) > 0),
    telefone TEXT,
    email TEXT,
    endereco TEXT,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0,1))
) STRICT;

CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INTEGER PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    login TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (length(trim(login)) >= 3),
    senha_hash TEXT NOT NULL CHECK (length(trim(senha_hash)) > 0),
    perfil TEXT NOT NULL CHECK (perfil IN ('ADMINISTRADOR','ESTOQUE','OPERADOR')),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0,1))
) STRICT;

CREATE TABLE IF NOT EXISTS Doacao (
    id_doacao INTEGER PRIMARY KEY,
    id_doador INTEGER NOT NULL REFERENCES Doador(id_doador) ON DELETE RESTRICT,
    id_usuario INTEGER NOT NULL REFERENCES Usuario(id_usuario) ON DELETE RESTRICT,
    data_recebimento TEXT NOT NULL CHECK (date(data_recebimento, '+0 days') IS data_recebimento),
    observacao TEXT
) STRICT;

CREATE TABLE IF NOT EXISTS Lote (
    id_lote INTEGER PRIMARY KEY,
    id_doacao INTEGER NOT NULL REFERENCES Doacao(id_doacao) ON DELETE RESTRICT,
    id_alimento INTEGER NOT NULL REFERENCES Alimento(id_alimento) ON DELETE RESTRICT,
    codigo_lote TEXT NOT NULL UNIQUE CHECK (length(trim(codigo_lote)) > 0),
    codigo_origem TEXT,
    data_validade TEXT NOT NULL CHECK (date(data_validade, '+0 days') IS data_validade),
    observacao TEXT,
    UNIQUE (id_lote, id_alimento)
) STRICT;

CREATE TABLE IF NOT EXISTS Solicitacao (
    id_solicitacao INTEGER PRIMARY KEY,
    id_instituicao INTEGER NOT NULL REFERENCES Instituicao(id_instituicao) ON DELETE RESTRICT,
    id_usuario INTEGER NOT NULL REFERENCES Usuario(id_usuario) ON DELETE RESTRICT,
    data_solicitacao TEXT NOT NULL CHECK (date(data_solicitacao, '+0 days') IS data_solicitacao),
    status TEXT NOT NULL DEFAULT 'ABERTA' CHECK (status IN ('ABERTA','ENCERRADA','CANCELADA')),
    observacao TEXT
) STRICT;

CREATE TABLE IF NOT EXISTS ItemSolicitacao (
    id_item_solicitacao INTEGER PRIMARY KEY,
    id_solicitacao INTEGER NOT NULL REFERENCES Solicitacao(id_solicitacao) ON DELETE RESTRICT,
    id_alimento INTEGER NOT NULL REFERENCES Alimento(id_alimento) ON DELETE RESTRICT,
    quantidade_solicitada INTEGER NOT NULL CHECK (quantidade_solicitada > 0),
    UNIQUE (id_solicitacao, id_alimento),
    UNIQUE (id_item_solicitacao, id_solicitacao),
    UNIQUE (id_item_solicitacao, id_alimento)
) STRICT;

CREATE TABLE IF NOT EXISTS Distribuicao (
    id_distribuicao INTEGER PRIMARY KEY,
    id_solicitacao INTEGER NOT NULL REFERENCES Solicitacao(id_solicitacao) ON DELETE RESTRICT,
    id_usuario INTEGER NOT NULL REFERENCES Usuario(id_usuario) ON DELETE RESTRICT,
    data_distribuicao TEXT NOT NULL CHECK (date(data_distribuicao, '+0 days') IS data_distribuicao),
    observacao TEXT,
    UNIQUE (id_distribuicao, id_solicitacao)
) STRICT;

CREATE TABLE IF NOT EXISTS MovimentacaoEstoque (
    id_movimentacao INTEGER PRIMARY KEY,
    id_lote INTEGER NOT NULL,
    id_alimento INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL REFERENCES Usuario(id_usuario) ON DELETE RESTRICT,
    tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA_DOACAO','AJUSTE_ENTRADA','SAIDA_DISTRIBUICAO','PERDA','AJUSTE_SAIDA','ESTORNO_DISTRIBUICAO')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    data_movimentacao TEXT NOT NULL CHECK (
        length(data_movimentacao) = 25 AND
        data_movimentacao GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9][+-][0-9][0-9]:[0-9][0-9]' AND
        substr(data_movimentacao,20,1) IN ('+','-') AND
        date(substr(data_movimentacao,1,10), '+0 days') IS substr(data_movimentacao,1,10) AND
        time(substr(data_movimentacao,12,8)) IS substr(data_movimentacao,12,8) AND
        CAST(substr(data_movimentacao,12,2) AS INTEGER) BETWEEN 0 AND 23 AND
        CAST(substr(data_movimentacao,15,2) AS INTEGER) BETWEEN 0 AND 59 AND
        CAST(substr(data_movimentacao,18,2) AS INTEGER) BETWEEN 0 AND 59 AND
        CAST(substr(data_movimentacao,21,2) AS INTEGER) BETWEEN 0 AND 14 AND
        CAST(substr(data_movimentacao,24,2) AS INTEGER) BETWEEN 0 AND 59 AND
        (CAST(substr(data_movimentacao,21,2) AS INTEGER) < 14 OR CAST(substr(data_movimentacao,24,2) AS INTEGER) = 0)
    ),
    motivo TEXT,
    id_distribuicao INTEGER,
    id_item_solicitacao INTEGER,
    id_solicitacao INTEGER,
    id_movimentacao_original INTEGER REFERENCES MovimentacaoEstoque(id_movimentacao) ON DELETE RESTRICT,
    FOREIGN KEY (id_lote,id_alimento) REFERENCES Lote(id_lote,id_alimento) ON DELETE RESTRICT,
    FOREIGN KEY (id_distribuicao,id_solicitacao) REFERENCES Distribuicao(id_distribuicao,id_solicitacao) ON DELETE RESTRICT,
    FOREIGN KEY (id_item_solicitacao,id_solicitacao) REFERENCES ItemSolicitacao(id_item_solicitacao,id_solicitacao) ON DELETE RESTRICT,
    FOREIGN KEY (id_item_solicitacao,id_alimento) REFERENCES ItemSolicitacao(id_item_solicitacao,id_alimento) ON DELETE RESTRICT,
    CHECK (
        (tipo IN ('SAIDA_DISTRIBUICAO','ESTORNO_DISTRIBUICAO') AND id_distribuicao IS NOT NULL AND id_item_solicitacao IS NOT NULL AND id_solicitacao IS NOT NULL)
        OR
        (tipo NOT IN ('SAIDA_DISTRIBUICAO','ESTORNO_DISTRIBUICAO') AND id_distribuicao IS NULL AND id_item_solicitacao IS NULL AND id_solicitacao IS NULL)
    ),
    CHECK ((tipo = 'ESTORNO_DISTRIBUICAO' AND id_movimentacao_original IS NOT NULL) OR (tipo <> 'ESTORNO_DISTRIBUICAO' AND id_movimentacao_original IS NULL)),
    CHECK (tipo NOT IN ('PERDA','AJUSTE_ENTRADA','AJUSTE_SAIDA','ESTORNO_DISTRIBUICAO') OR length(trim(motivo)) > 0)
) STRICT;

CREATE INDEX IF NOT EXISTS idx_doacao_doador ON Doacao(id_doador);
CREATE INDEX IF NOT EXISTS idx_doacao_usuario ON Doacao(id_usuario);
CREATE INDEX IF NOT EXISTS idx_lote_alimento_validade ON Lote(id_alimento,data_validade);
CREATE INDEX IF NOT EXISTS idx_lote_doacao ON Lote(id_doacao);
CREATE INDEX IF NOT EXISTS idx_solicitacao_instituicao_data ON Solicitacao(id_instituicao,data_solicitacao);
CREATE INDEX IF NOT EXISTS idx_item_solicitacao_alimento ON ItemSolicitacao(id_alimento);
CREATE INDEX IF NOT EXISTS idx_distribuicao_solicitacao_data ON Distribuicao(id_solicitacao,data_distribuicao);
CREATE INDEX IF NOT EXISTS idx_movimentacao_lote ON MovimentacaoEstoque(id_lote);
CREATE INDEX IF NOT EXISTS idx_movimentacao_item_tipo ON MovimentacaoEstoque(id_item_solicitacao,tipo);
CREATE UNIQUE INDEX IF NOT EXISTS uq_movimentacao_entrada_lote ON MovimentacaoEstoque(id_lote) WHERE tipo='ENTRADA_DOACAO';
CREATE UNIQUE INDEX IF NOT EXISTS uq_movimentacao_saida_linha ON MovimentacaoEstoque(id_distribuicao,id_item_solicitacao,id_lote) WHERE tipo='SAIDA_DISTRIBUICAO';
CREATE UNIQUE INDEX IF NOT EXISTS uq_movimentacao_estorno_origem ON MovimentacaoEstoque(id_movimentacao_original) WHERE tipo='ESTORNO_DISTRIBUICAO';

CREATE TRIGGER IF NOT EXISTS trg_movimentacao_immutable_update BEFORE UPDATE ON MovimentacaoEstoque BEGIN SELECT RAISE(ABORT,'Movimentações são imutáveis'); END;
CREATE TRIGGER IF NOT EXISTS trg_movimentacao_immutable_delete BEFORE DELETE ON MovimentacaoEstoque BEGIN SELECT RAISE(ABORT,'Movimentações são imutáveis'); END;
CREATE TRIGGER IF NOT EXISTS trg_movimentacao_requires_entry BEFORE INSERT ON MovimentacaoEstoque
WHEN NEW.tipo <> 'ENTRADA_DOACAO' AND NOT EXISTS (SELECT 1 FROM MovimentacaoEstoque WHERE id_lote=NEW.id_lote AND tipo='ENTRADA_DOACAO')
BEGIN SELECT RAISE(ABORT,'O lote precisa de entrada de doação antes de outras movimentações'); END;
CREATE TRIGGER IF NOT EXISTS trg_movimentacao_no_negative_or_expired BEFORE INSERT ON MovimentacaoEstoque
WHEN NEW.tipo IN ('SAIDA_DISTRIBUICAO','PERDA','AJUSTE_SAIDA') AND (
    NEW.quantidade > COALESCE((SELECT SUM(CASE WHEN tipo IN ('ENTRADA_DOACAO','AJUSTE_ENTRADA','ESTORNO_DISTRIBUICAO') THEN quantidade ELSE -quantidade END) FROM MovimentacaoEstoque WHERE id_lote=NEW.id_lote),0)
    OR (NEW.tipo='SAIDA_DISTRIBUICAO' AND (SELECT l.data_validade < d.data_distribuicao FROM Lote l JOIN Distribuicao d ON d.id_distribuicao=NEW.id_distribuicao WHERE l.id_lote=NEW.id_lote))
)
BEGIN SELECT RAISE(ABORT,'Saldo insuficiente ou lote vencido'); END;
CREATE TRIGGER IF NOT EXISTS trg_movimentacao_request_limit BEFORE INSERT ON MovimentacaoEstoque
WHEN NEW.tipo='SAIDA_DISTRIBUICAO' AND (
    COALESCE((SELECT status FROM Solicitacao WHERE id_solicitacao=NEW.id_solicitacao),'') <> 'ABERTA'
    OR NEW.quantidade > COALESCE((SELECT i.quantidade_solicitada - SUM(CASE WHEN m.tipo='SAIDA_DISTRIBUICAO' THEN m.quantidade WHEN m.tipo='ESTORNO_DISTRIBUICAO' THEN -m.quantidade ELSE 0 END)
        FROM ItemSolicitacao i LEFT JOIN MovimentacaoEstoque m ON m.id_item_solicitacao=i.id_item_solicitacao
        WHERE i.id_item_solicitacao=NEW.id_item_solicitacao GROUP BY i.id_item_solicitacao),0)
)
BEGIN SELECT RAISE(ABORT,'Solicitação fechada ou quantidade acima do pendente'); END;
CREATE TRIGGER IF NOT EXISTS trg_alimento_unidade_immutable BEFORE UPDATE OF unidade_medida ON Alimento
WHEN NEW.unidade_medida <> OLD.unidade_medida AND (EXISTS(SELECT 1 FROM Lote WHERE id_alimento=OLD.id_alimento) OR EXISTS(SELECT 1 FROM ItemSolicitacao WHERE id_alimento=OLD.id_alimento))
BEGIN SELECT RAISE(ABORT,'Unidade não pode mudar após uso'); END;
CREATE TRIGGER IF NOT EXISTS trg_movimentacao_refund_integrity BEFORE INSERT ON MovimentacaoEstoque
WHEN NEW.tipo='ESTORNO_DISTRIBUICAO' AND NOT EXISTS (
    SELECT 1 FROM MovimentacaoEstoque o WHERE o.id_movimentacao=NEW.id_movimentacao_original
      AND o.tipo='SAIDA_DISTRIBUICAO' AND o.id_lote=NEW.id_lote AND o.id_alimento=NEW.id_alimento
      AND o.id_distribuicao=NEW.id_distribuicao AND o.id_item_solicitacao=NEW.id_item_solicitacao
      AND o.id_solicitacao=NEW.id_solicitacao AND o.quantidade=NEW.quantidade
)
BEGIN SELECT RAISE(ABORT,'Estorno deve corresponder integralmente à saída original'); END;

CREATE TRIGGER IF NOT EXISTS trg_distribuicao_data_immutable_after_output BEFORE UPDATE OF data_distribuicao ON Distribuicao
WHEN NEW.data_distribuicao <> OLD.data_distribuicao AND EXISTS (
    SELECT 1 FROM MovimentacaoEstoque WHERE id_distribuicao=OLD.id_distribuicao AND tipo='SAIDA_DISTRIBUICAO'
)
BEGIN SELECT RAISE(ABORT,'Data da distribuição não pode mudar após saída registrada'); END;

CREATE TRIGGER IF NOT EXISTS trg_lote_validade_immutable_after_output BEFORE UPDATE OF data_validade ON Lote
WHEN NEW.data_validade <> OLD.data_validade AND EXISTS (
    SELECT 1 FROM MovimentacaoEstoque WHERE id_lote=OLD.id_lote AND tipo='SAIDA_DISTRIBUICAO'
)
BEGIN SELECT RAISE(ABORT,'Validade do lote não pode mudar após distribuição registrada'); END;

CREATE VIEW IF NOT EXISTS vw_saldo_por_lote AS
SELECT l.id_lote,l.codigo_lote,l.id_alimento,l.data_validade,
       COALESCE(SUM(CASE WHEN m.tipo IN ('ENTRADA_DOACAO','AJUSTE_ENTRADA','ESTORNO_DISTRIBUICAO') THEN m.quantidade ELSE -m.quantidade END),0) AS saldo
FROM Lote l LEFT JOIN MovimentacaoEstoque m ON m.id_lote=l.id_lote GROUP BY l.id_lote;

CREATE VIEW IF NOT EXISTS vw_atendimento_itens AS
SELECT i.id_item_solicitacao,i.id_solicitacao,i.id_alimento,i.quantidade_solicitada,
       COALESCE(SUM(CASE WHEN m.tipo='SAIDA_DISTRIBUICAO' THEN m.quantidade WHEN m.tipo='ESTORNO_DISTRIBUICAO' THEN -m.quantidade ELSE 0 END),0) AS quantidade_entregue,
       i.quantidade_solicitada-COALESCE(SUM(CASE WHEN m.tipo='SAIDA_DISTRIBUICAO' THEN m.quantidade WHEN m.tipo='ESTORNO_DISTRIBUICAO' THEN -m.quantidade ELSE 0 END),0) AS quantidade_pendente
FROM ItemSolicitacao i LEFT JOIN MovimentacaoEstoque m ON m.id_item_solicitacao=i.id_item_solicitacao AND m.tipo IN ('SAIDA_DISTRIBUICAO','ESTORNO_DISTRIBUICAO')
GROUP BY i.id_item_solicitacao;
