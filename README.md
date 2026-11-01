# Conecta Alimento

Sistema local de gestão de doações alimentares, estoque, solicitações e distribuição.

> **Status: fase inicial de implementação.** Este repositório acabou de ser configurado. Ainda não há código, banco de dados, testes automatizados ou pipeline de CI. As seções abaixo descrevem o que o projeto pretende entregar, não o que já está pronto.

## Sobre o projeto

O Conecta Alimento é um projeto da disciplina de Projeto de Software, do curso de Ciência da Computação. O objetivo é construir uma aplicação simples e funcional que substitua registros dispersos em planilhas e anotações por um sistema organizado, com banco de dados relacional e regras de negócio centralizadas.

O cenário de referência usado na modelagem inicial é a Associação Comunitária Mesa Solidária, uma organização **fictícia**. Não houve entrevista nem visita a uma organização real nesta etapa.

O software busca melhorar a eficiência operacional, o acompanhamento de lotes e validades e a rastreabilidade dos alimentos recebidos e distribuídos. Ele não é apresentado como solução para a insegurança alimentar, e não há dados que comprovem redução da fome ou do desperdício.

## Escopo planejado do MVP

- Cadastro de doadores, alimentos, instituições atendidas e usuários internos
- Registro de doações, criação de lotes e controle de datas de validade
- Controle de entradas e saídas de estoque, com perdas e ajustes justificados
- Consulta de estoque por alimento e lote
- Solicitações e distribuições, incluindo atendimento parcial
- Dashboard com indicadores calculados automaticamente a partir dos registros
- Relatórios operacionais (exportação em CSV desejável)
- Testes automatizados e preparação para distribuição no Windows

Fora do escopo do MVP: portal público de doações, API REST, aplicativo móvel, acesso remoto simultâneo, inteligência artificial e integrações externas complexas.

## Decisões de arquitetura

- Arquitetura monolítica modular em camadas: apresentação, regras de negócio e persistência
- Python 3.12, Streamlit para a interface e SQLite (módulo `sqlite3`) para persistência
- pytest para testes, GitHub Actions para integração contínua e PyInstaller para o pacote Windows
- O saldo de estoque nunca é digitado: é sempre derivado das movimentações registradas
- Execução local, com a aplicação escutando apenas em loopback

As versões exatas das dependências serão definidas e fixadas durante a configuração do ambiente.

## Situação atual

| Item | Situação |
|---|---|
| Repositório e documentação inicial | Em configuração |
| Implementação do MVP | Não iniciada |
| Testes automatizados | Não iniciados |
| Integração contínua | Não configurada |
| Validação com participantes reais | Não realizada |

Esta tabela será atualizada à medida que cada etapa for concluída e comprovada.

## Como executar

Ainda não disponível. As instruções de instalação e execução serão adicionadas quando houver uma primeira versão funcional.

## Dados e segurança

Este repositório é público. Ele não deve conter senhas, tokens, dados pessoais reais nem arquivos de banco de dados. O `.gitignore` foi configurado para reduzir esse risco, mas não substitui a atenção a cada commit.

## Autoria

Projeto acadêmico individual desenvolvido por Leonardo Felix.
