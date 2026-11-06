# Conecta Alimento

Aplicação local para registrar doações recebidas, lotes e estoque de alimentos. O cenário acadêmico usa a Associação Comunitária Mesa Solidária como referência fictícia; não houve entrevista nem validação operacional com uma organização real.

## Arquitetura

- **Interface:** Streamlit em `app.py` e `interface/`.
- **Serviços:** validações, cadastros, recebimentos, estoque, autenticação mínima e indicadores em `servicos/`.
- **Persistência:** SQLite e `sqlite3` em `banco/`.

A interface chama os serviços e não executa SQL. O saldo é calculado a partir das movimentações; quantidades são armazenadas em gramas, mililitros ou unidades inteiras.

## Requisitos

- Windows com Python 3.12.
- A aplicação cria o arquivo SQLite local em `dados/conecta_alimento.sqlite3` na primeira inicialização.
- O banco e os relatórios locais são ignorados pelo Git.

## Instalar

No PowerShell, na pasta do repositório:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` inclui a dependência da aplicação e as ferramentas de teste. Para instalar somente a aplicação, use `requirements.txt`.

## Inicializar e executar

```powershell
.\.venv\Scripts\python.exe -c "from banco import inicializar; print(inicializar())"
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

O servidor fica restrito ao loopback IPv4 (`127.0.0.1`) e não é publicado na rede.

O caminho local padrão do SQLite é `dados/conecta_alimento.sqlite3`; pode ser substituído pela variável `CONECTA_DB_PATH`. Em ambiente hospedado, defina `CONECTA_ENV=hosted` e configure `CONECTA_BOOTSTRAP_SECRET` em `st.secrets` ou variável de ambiente antes da primeira criação do administrador. Nunca inclua esse segredo em arquivos versionados.

Na primeira abertura, crie o administrador com nome, login e uma senha de pelo menos 12 caracteres. Não há credenciais padrão. O hash da senha é salvo no SQLite; a aplicação não mantém a senha em texto puro.

Falhas internas são registradas no console local que iniciou o Streamlit; a interface exibe mensagens genéricas e não mostra detalhes do SQLite.

Cadastre doadores e alimentos na tela **Cadastros**. Em **Receber doação**, adicione um ou mais lotes e confirme o recebimento; doação, lotes e entradas de estoque são gravados juntos ou revertidos juntos.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=banco --cov=servicos --cov-report=term-missing --cov-report=xml
```

Os testes de serviço usam arquivos SQLite temporários. A cobertura do comando abrange `banco` e `servicos`; não representa a cobertura da interface Streamlit.

Na validação local mais recente, a suíte registrou **56 testes aprovados** e **86% de cobertura** em `banco` e `servicos` (Python 3.12.10, pytest 9.2.0 e pytest-cov 7.1.0).

## Acessibilidade

A interface oferece modo de alto contraste, ativado pelo controle na lateral e mantido durante os reruns da sessão. O modo reforça o contraste de textos, controles, estados e do gráfico do dashboard. Há também realce visível de foco para navegação por teclado. Esses recursos não substituem uma auditoria completa de acessibilidade ou testes com tecnologias assistivas.

## Prontidão para hospedagem

O app ainda não está pronto para uso público com dados operacionais. A limitação de tentativas de login é compartilhada pelo processo e reinicia junto com ele; não protege entre réplicas. O bootstrap hospedado exige segredo de autorização e fica fechado se ele não estiver configurado. Streamlit Community Cloud deve ser tratado apenas como demonstração descartável enquanto usa SQLite local, pois o armazenamento local da aplicação não é garantia de persistência. Não insira dados reais nesse cenário.

Consulte [docs/PRONTIDAO_DEPLOY.md](docs/PRONTIDAO_DEPLOY.md) para comparação de hospedagem, dados, segurança residual e roteiro de validação.

## Estado do MVP

Consulte [docs/STATUS_IMPLEMENTACAO.md](docs/STATUS_IMPLEMENTACAO.md) para ver o que está implementado, testado e ainda pendente. Distribuições de solicitações, perdas/ajustes manuais, CRUD de instituições e relatórios continuam fora do primeiro fluxo vertical.

## Segurança e dados

O repositório é público. Não inclua senhas, tokens, dados pessoais reais ou arquivos de banco. Os usuários e registros de doação devem ser dados reais da organização que utilizará a instalação local; o aplicativo não cria dados de demonstração.
