# Status da implementação — Conecta Alimento

Atualizado em 04/11/2026.

## Implementado

- Esquema SQLite versionado com as dez entidades, chaves, restrições, índices, triggers e views documentados.
- CI GitHub Actions configurada para Windows e Python 3.12.
- Camada de persistência centralizada em `banco/`, com chaves estrangeiras ativadas em cada conexão.
- Serviços de relógio, validação com `Decimal`, cadastros/desativação de doadores e alimentos, bootstrap do primeiro administrador, autenticação, recebimento atômico, consultas de estoque e indicadores do dashboard.
- `criar_usuario()` permite somente os perfis `ESTOQUE` e `OPERADOR`; a criação do primeiro administrador permanece separada.
- Dashboard lê contagens, saldos e movimentos em uma única conexão e transação de leitura.
- Interface Streamlit disponível em `app.py`: bootstrap, login/logout, cadastros de doadores e alimentos, recebimento de doações com múltiplos lotes e dashboard.
- Streamlit configurado para escutar apenas em `127.0.0.1`; erros internos são registrados pelo logging local e apresentados com mensagens genéricas.
- O caminho do SQLite aceita `CONECTA_DB_PATH`, preservando `dados/conecta_alimento.sqlite3` como padrão local.
- Bootstrap do administrador hospedado requer `CONECTA_BOOTSTRAP_SECRET` em secrets/ambiente; limitação de cinco falhas de login por usuário, mantida no processo.
- Banco padrão: `dados/conecta_alimento.sqlite3`. Testes usam bancos temporários isolados.

## Testado

- **Suíte anterior:** 54 aprovados, 0 falhas, em Python 3.12.10 e SQLite 3.49.1, com pytest 9.2.0.
- **Suíte de auditoria (04/11/2026):** 56 aprovados, 0 falhas, 0 ignorados, em Python 3.12.10 e pytest 9.2.0.
- **Cobertura:** 86% no conjunto medido de `banco` e `servicos`; `servicos/limite_autenticacao.py` ficou em 77%. A interface Streamlit não está incluída nessa métrica.
- `python -m compileall -q app.py banco servicos interface tests` concluído sem erros.
- Smoke test HTTP do Streamlit respondido em loopback; listener verificado com `Get-NetTCPConnection` em `127.0.0.1`, sem listener do processo em `0.0.0.0` ou `::`.
- Testes automatizados de persistência e serviços; não são testes visuais do navegador.

## Planejado

- Fluxos completos de solicitação e distribuição, incluindo saídas de estoque e estornos.
- Registro operacional de perdas e ajustes justificados.
- Cadastro de instituições e administração de usuários pela interface, com política de autorização explícita.
- Relatórios e preparação de pacote Windows.

## Pendente

- Validação manual de todas as telas e fluxos no navegador Windows.
- Verificação da versão SQLite embutida no futuro executável PyInstaller; o Python 3.12.10 do ambiente de desenvolvimento usa SQLite 3.49.1.
- Não há entrevista nem validação operacional com organização real.
- O limitador por login é apenas local ao processo. Antes de uma demonstração pública persistente, precisa de armazenamento/distribuição compartilhada e proteção por origem/rede.
- Rate limit atual usa memória do processo, sem persistência nem compartilhamento entre réplicas; não constitui proteção suficiente contra ataques distribuídos ou reinicializações.
- A aplicação continua usando SQLite local por padrão. Para hospedagem pública sem perda de dados, é necessária uma decisão e implementação de persistência durável; não cadastrar dados reais em armazenamento efêmero.
- A exigência do segredo de bootstrap se aplica quando `CONECTA_ENV=hosted`; a instalação local preserva o primeiro cadastro sem segredo.
