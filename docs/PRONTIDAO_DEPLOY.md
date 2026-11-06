# Prontidão para demonstração e operação

Atualizado em 04/11/2026. Não significa que o app foi implantado.

## Decisão de uso

O MVP local pode ser executado em um único computador. Não use a versão atual para registrar dados reais em uma hospedagem pública: o app continua com SQLite local e ainda não há persistência/backup em nuvem demonstrados.

Para uma avaliação acadêmica, a opção recomendada é uma demonstração descartável, com dados fictícios identificados como demonstração, sem dados pessoais nem promessa de retenção. O Streamlit Community Cloud suporta configuração de secrets pela interface da plataforma; não versione `secrets.toml`. Defina `CONECTA_ENV=hosted` e `CONECTA_BOOTSTRAP_SECRET` antes de liberar a primeira criação administrativa. O caminho do banco é configurável por `CONECTA_DB_PATH`, mas apontá-lo para o filesystem de uma hospedagem não o torna persistente.

## Alternativas de persistência

| Alternativa | Custo/limite conhecido | Adequação |
|---|---|---|
| A. Streamlit Community Cloud + SQLite local | Sem cobrança para a demonstração; armazenamento local não é uma garantia de retenção/recuperação. | Boa para avaliação descartável; não usar com registros reais. |
| B. PostgreSQL gerenciado, por exemplo Supabase | Plano gratuito anunciado com 500 MB e pausa do projeto após uma semana sem atividade; backups automáticos não estão incluídos no plano gratuito. | Caminho melhor para uso multiusuário depois de migrar/revalidar as consultas e regras SQLite, ativar backups e proteger a conexão com secrets. O plano gratuito, isoladamente, não é garantia operacional. |
| C. Streamlit em serviço pago com disco persistente, por exemplo Render | Disco persistente informado a US$ 0,25/GB/mês, além do compute; disco só fica disponível em serviço pago e uma instância com disco não escala horizontalmente. | Menor migração inicial para um app pequeno de instância única; exige dimensionar custo, backup externo e aceitar a limitação de escala. Não é opção gratuita com persistência. |

**Recomendação:** usar A apenas como demo sem dados reais. Para operação, preferir B com PostgreSQL pago/backup adequado se houver mais de um operador ou necessidade de escala. C pode reduzir a migração se for deliberadamente uma instalação pequena, de instância única, com disco pago e rotina de backup testada. Nenhuma das opções foi contratada, configurada ou implantada.

Fontes consultadas em 04/11/2026: [secrets no Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management), [preços Supabase](https://supabase.com/pricing), [limitações do plano gratuito Render](https://render.com/docs/free), [discos persistentes Render](https://render.com/docs/disks).

## Autenticação e ameaças residuais

- Senhas são derivadas com PBKDF2-HMAC-SHA256, salt aleatório individual e 600.000 iterações; comparação do digest usa `hmac.compare_digest`.
- Na instalação local vazia, o primeiro administrador é criado localmente. Quando `CONECTA_ENV=hosted`, a criação exige segredo configurado em `st.secrets` ou `CONECTA_BOOTSTRAP_SECRET`; sem segredo, o formulário fica fechado. A operação de banco ainda bloqueia segundo bootstrap de forma transacional.
- O login limita a cinco falhas por identificador durante uma janela de 15 minutos, compartilhada no processo. Reinício limpa a contagem, várias réplicas não compartilham o estado e não há limitação por endereço de origem. Portanto, isso é uma mitigação básica, não defesa suficiente para uma aplicação pública/operacional.
- A sessão guarda o ID do usuário em `st.session_state` e revalida se ele ainda está ativo a cada execução; não há política de expiração temporal da sessão nem MFA. Para uso público, avaliar provedor de identidade, expiração/revogação apropriada e rate limit persistente/distribuído.
- SQL dos serviços é parametrizado. Blocos HTML usam texto fixo ou escapam valores de cadastro antes de interpolar. Erros internos são registrados no servidor e a interface apresenta mensagens genéricas.

## Dados, backup e observabilidade

- Local: padrão `dados/conecta_alimento.sqlite3`; `CONECTA_DB_PATH` pode direcionar para outro arquivo. Não reutilizar o banco local em hospedagem.
- Backup local recomendado: usar API de backup do SQLite ou parar a aplicação e gerar cópia consistente; guardar cópia cifrada fora do computador e fazer teste periódico de restauração. A aplicação ainda não automatiza nem monitora backup/restore.
- Monitoramento não está ativo. Na implantação, habilitar logs e alertas de falha/reinicialização na plataforma, monitorar o endpoint HTTP de saúde do Streamlit (`/_stcore/health`) com um serviço de ping externo e testar periodicamente login, consulta e escrita/leitura de uma doação de teste. Alertas HTTP não provam persistência: incluir teste controlado após reinicialização e revisão dos backups.
- Não registrar senhas, segredo de bootstrap, conteúdo de formulários ou hashes nos logs. As mensagens de erro destinadas ao usuário permanecem genéricas.

## Roteiro de validação manual

1. Com banco temporário e usuário fictício, verificar bootstrap, login válido/inválido e logout.
2. Percorrer menu, cadastro, recebimento com dois lotes, resumo, confirmação e dashboard; conferir transação e saldos no banco temporário.
3. Testar cinco senhas incorretas, a mensagem de espera, liberação após a janela e o comportamento após reiniciar o processo.
4. Repetir com alto contraste ligado e navegar por teclado, verificando foco, campos, tabela, estados e gráfico em viewport estreito.
5. Em ambiente hospedado, testar ausência de segredo (bootstrap bloqueado), segredo incorreto/correto e reinicialização. Não inserir dados reais até que a estratégia de persistência e recuperação tenha sido comprovada.
