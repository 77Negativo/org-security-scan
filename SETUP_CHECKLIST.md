# ✅ Setup Checklist

Use este checklist para garantir que tudo está configurado corretamente.

## 📋 Pré-Requisitos

- [ ] Você tem acesso a uma GitHub Organization (ou conta pessoal)
- [ ] Você tem permissões de admin na organização
- [ ] Você pode criar Personal Access Tokens
- [ ] Você pode configurar GitHub Actions no repositório

## 🔑 GitHub Token

- [ ] Token criado em: https://github.com/settings/tokens/new
- [ ] Nome do token definido (ex: `org-security-scan`)
- [ ] Scopes selecionados:
  - [ ] `repo` (Full control of private repositories)
  - [ ] `admin:org` → `read:org` (Read org and team membership)
  - [ ] `read:user` (Read ALL user profile data)
- [ ] Token copiado e salvo temporariamente

## 🔐 Repository Secrets

- [ ] Secret criado: `Settings` → `Secrets and variables` → `Actions`
- [ ] Nome do secret: `ORG_SECURITY_TOKEN`
- [ ] Valor do secret: Token do passo anterior
- [ ] Secret salvo com sucesso

## ⚙️ Repository Settings

### Workflow Permissions

- [ ] Acessado: `Settings` → `Actions` → `General`
- [ ] Selecionado: `Read and write permissions`
- [ ] Configuração salva

### Branch Protection (Opcional mas Recomendado)

- [ ] Acessado: `Settings` → `Branches`
- [ ] Regra criada para branch principal
- [ ] `github-actions[bot]` adicionado aos bypass actors
- [ ] Regra salva

## 📁 Arquivos do Projeto

- [ ] Estrutura de diretórios criada:
  ```
  org-security-scan/
  ├── .github/workflows/
  ├── steampipe/queries/
  ├── scripts/
  └── reports/
  ```

- [ ] Workflow criado: `.github/workflows/org-security-scan.yml`
- [ ] Queries criadas em `steampipe/queries/`:
  - [ ] `repositories.sql`
  - [ ] `users_permissions.sql`
  - [ ] `security_settings.sql`
- [ ] Scripts criados em `scripts/`:
  - [ ] `run_audit.py`
  - [ ] `generate_dashboard.py`
  - [ ] `create_issue.py`

## 🧪 Teste Local (Opcional)

Se você quer testar localmente primeiro:

- [ ] Steampipe instalado
  ```bash
  sudo /bin/sh -c "$(curl -fsSL https://steampipe.io/install/steampipe.sh)"
  ```

- [ ] Plugin GitHub instalado
  ```bash
  steampipe plugin install github
  ```

- [ ] Configuração criada: `~/.steampipe/config/github.spc`
  ```bash
  cp steampipe.spc.example ~/.steampipe/config/github.spc
  # Editar e adicionar token
  ```

- [ ] Teste executado com sucesso
  ```bash
  ./scripts/test_local.sh
  ```

## 🚀 Primeira Execução

- [ ] Acessado: Aba `Actions` do repositório
- [ ] Workflow `Organization Security Scan` selecionado
- [ ] Clicado em `Run workflow`
- [ ] Branch selecionada: `main`
- [ ] Workflow iniciado

## ✅ Validação dos Resultados

Aguarde o workflow terminar (5-10 minutos) e verifique:

- [ ] Workflow executado com sucesso (status verde ✅)
- [ ] Artifact gerado: `security-reports-{run_number}`
- [ ] Reports commitados na pasta `reports/`
- [ ] Issue criada (se houver achados críticos)

### Dashboard HTML

- [ ] Artifact baixado
- [ ] Arquivo `security_dashboard_*.html` aberto no navegador
- [ ] Métricas carregadas corretamente
- [ ] Achados exibidos (se houver)

### Arquivos JSON/CSV

- [ ] Arquivos JSON gerados em `reports/`
- [ ] Arquivos CSV gerados em `reports/results/`
- [ ] Dados parecem corretos

### Issue Automatizada

Se houver achados críticos:
- [ ] Issue criada automaticamente
- [ ] Título: `🔐 Relatório de Segurança - YYYY-MM-DD`
- [ ] Labels: `security`, `automated`
- [ ] Conteúdo com resumo executivo
- [ ] Checklist de recomendações

## 📅 Execução Automática

- [ ] Verificado: Workflow configurado para rodar semanalmente
- [ ] Cron schedule confirmado: `'0 9 * * 1'` (Segunda-feira 9h UTC)
- [ ] Ajustado horário se necessário

## 🔧 Troubleshooting

Se algo não funcionou:

- [ ] Logs do workflow revisados na aba `Actions`
- [ ] Erros identificados e corrigidos
- [ ] Documentação consultada (README.md, QUICKSTART.md)

### Problemas Comuns Verificados

- [ ] ✅ Permissões do workflow configuradas
- [ ] ✅ Secret com nome correto (`ORG_SECURITY_TOKEN`)
- [ ] ✅ Token com scopes necessários
- [ ] ✅ Token não expirado

## 📝 Customização (Opcional)

Após tudo funcionar:

- [ ] Queries customizadas adicionadas (se necessário)
- [ ] Dashboard personalizado (se necessário)
- [ ] Horário de execução ajustado
- [ ] Notificações configuradas (Slack, Teams, etc.)

## 🎯 Próximos Passos

- [ ] Revisar primeiro relatório gerado
- [ ] Priorizar achados críticos
- [ ] Implementar correções recomendadas
- [ ] Agendar revisão semanal dos reports

---

## ✨ Tudo Pronto!

Se todos os itens estão marcados, parabéns! 🎉

Você agora tem um sistema automatizado de auditoria de segurança rodando!

### 📚 Recursos

- [README Completo](README.md)
- [Quick Start Guide](QUICKSTART.md)
- [Exemplos de Queries](steampipe/queries/examples_custom.sql)

### 🆘 Precisa de Ajuda?

Se algum item não está funcionando:
1. Revise os logs do workflow
2. Consulte a seção de troubleshooting no README
3. Verifique a documentação do Steampipe
4. Abra uma issue neste repositório

---

**Data de Conclusão:** _____________

**Testado por:** _____________

**Status:** ⬜ Em Progresso | ⬜ Concluído
