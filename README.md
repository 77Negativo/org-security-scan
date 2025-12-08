# 🔐 GitHub Organization Security Scan

**Dashboard contínuo de segurança para QUALQUER organização GitHub** usando **Steampipe** e **GitHub Actions**.

[![Generic](https://img.shields.io/badge/works-any%20org-brightgreen)]()
[![Auto-detect](https://img.shields.io/badge/auto--detect-organization-blue)]()
[![MIT](https://img.shields.io/badge/license-MIT-green)]()

## 🌟 Características Principais

✅ **Funciona em qualquer organização** - Detecção automática via token
✅ **Setup em 3 passos** - Pronto em menos de 5 minutos
✅ **Zero configuração** - Não precisa especificar nome da org
✅ **Totalmente automatizado** - Execução semanal + manual
✅ **Dashboard interativo** - HTML com insights visuais

## 📋 Visão Geral

Este projeto fornece uma solução **plug-and-play** automatizada para auditar continuamente a postura de segurança de **qualquer organização GitHub**, gerando insights valiosos sobre:

- 📦 **Repositórios** - Visibilidade, configurações, atividade
- 👥 **Usuários e Permissões** - 2FA, roles, colaboradores externos
- 🛡️ **Branch Protection** - Regras de proteção configuradas
- 🔒 **Configurações de Segurança** - Secret scanning, Dependabot, webhooks

### 🎯 Funcionalidades

✅ Execução automática semanal via GitHub Actions
✅ Dashboard HTML interativo com visualizações
✅ Relatórios em JSON e CSV para análise
✅ Criação automática de issues com achados críticos
✅ Histórico de scans para tracking de melhorias
✅ Queries SQL customizáveis do Steampipe

## 🚀 Quick Start

**Quer começar agora? Veja o [INSTALL.md](INSTALL.md) para setup em 3 passos!**

### Instalação Rápida

1. **Copie** a pasta `org-security-scan` para seu repositório
2. **Crie** um GitHub token com scopes: `repo`, `admin:org:read`, `read:user`
3. **Adicione** como secret `ORG_SECURITY_TOKEN`
4. **Pronto!** Execute o workflow em Actions

Detalhes completos: [INSTALL.md](INSTALL.md)

---

## 🚀 Setup Detalhado

### Pré-requisitos

1. **Qualquer GitHub Organization** - Funciona automaticamente!
2. **GitHub Token** com permissões:
   - `repo` (acesso completo aos repositórios)
   - `admin:org` → `read:org` (leitura de dados da organização)
   - `read:user` (leitura de informações de usuários)

### 1. Criar GitHub Token

1. Acesse: `Settings` → `Developer settings` → `Personal access tokens` → `Tokens (classic)`
2. Clique em `Generate new token (classic)`
3. Selecione os scopes necessários:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `admin:org` → `read:org` (Read org and team membership, read org projects)
   - ✅ `read:user` (Read ALL user profile data)
4. Copie o token gerado

### 2. Configurar Secrets no Repositório

Adicione o token como secret no repositório:

1. Vá para `Settings` → `Secrets and variables` → `Actions`
2. Clique em `New repository secret`
3. Nome: `ORG_SECURITY_TOKEN`
4. Valor: Cole o token gerado
5. Clique em `Add secret`

### 3. Ajustar Permissões do Workflow

No repositório, vá para:
- `Settings` → `Actions` → `General` → `Workflow permissions`
- Selecione: ✅ `Read and write permissions`
- Salve as alterações

### 4. Configurar Branch Protection (Opcional)

Para permitir que o workflow faça commit dos reports:

1. `Settings` → `Branches` → `Add rule`
2. Branch name pattern: `main` (ou sua branch principal)
3. Marque: ✅ `Allow specified actors to bypass required pull requests`
4. Adicione: `github-actions[bot]`

## 📂 Estrutura do Projeto

```
org-security-scan/
├── .github/
│   └── workflows/
│       └── org-security-scan.yml    # Workflow principal
├── steampipe/
│   └── queries/
│       ├── repositories.sql         # Auditoria de repositórios
│       ├── users_permissions.sql    # Auditoria de usuários
│       └── security_settings.sql    # Auditoria de segurança
├── scripts/
│   ├── run_audit.py                 # Executa queries Steampipe
│   ├── generate_dashboard.py       # Gera dashboard HTML
│   └── create_issue.py             # Cria issue com achados
├── reports/                         # Gerado automaticamente
│   ├── security_dashboard_latest.html
│   ├── audit_results_TIMESTAMP.json
│   └── results/
│       ├── repositories_TIMESTAMP.json
│       ├── users_permissions_TIMESTAMP.json
│       └── security_settings_TIMESTAMP.json
└── README.md
```

## 🔧 Como Usar

### Execução Automática

O workflow roda automaticamente:
- **Semanalmente**: Toda segunda-feira às 9h UTC
- **Em push para main**: Para testes e validação

### Execução Manual

1. Vá para `Actions` no repositório
2. Selecione o workflow `Organization Security Scan`
3. Clique em `Run workflow`
4. Selecione a branch e clique em `Run workflow`

### Acessar Resultados

Os resultados ficam disponíveis em três formatos:

#### 1. Dashboard HTML
- Arquivo: `reports/security_dashboard_latest.html`
- Acesse diretamente no navegador após o workflow
- Interface visual com gráficos e métricas

#### 2. Artifacts do Workflow
- Vá para a execução do workflow
- Baixe o artifact `security-reports-{run_number}`
- Contém todos os relatórios JSON, HTML e CSV

#### 3. Commit no Repositório
- Os reports são commitados automaticamente
- Histórico completo de scans disponível no Git

## 📊 Categorias de Auditoria

### 1. Repositórios

- ✅ Visão geral (visibilidade, branch padrão, atividade)
- ✅ Repositórios públicos (risco de exposição)
- ✅ Repositórios sem descrição
- ✅ Repositórios inativos (>6 meses)
- ✅ Configuração de features (issues, wiki, projects)
- ✅ Forks desatualizados
- ✅ Repositórios sem licença
- ✅ Estatísticas gerais

### 2. Usuários e Permissões

- ✅ Membros da organização
- ✅ **Usuários SEM 2FA** (CRÍTICO)
- ✅ Administradores
- ✅ Colaboradores externos
- ✅ Times e suas configurações
- ✅ Membros por time
- ✅ Permissões de times em repositórios
- ✅ Usuários com acesso admin
- ✅ Estatísticas de membros
- ✅ Contas inativas

### 3. Branch Protection e Segurança

- ✅ Status de proteção de branches
- ✅ Detalhes de branch protection rules
- ✅ **Repositórios SEM proteção** (CRÍTICO)
- ✅ Configurações de segurança (secret scanning, Dependabot)
- ✅ **Repos sem secret scanning** (CRÍTICO)
- ✅ Repos sem Dependabot
- ✅ Webhooks configurados
- ✅ Regras de proteção fracas
- ✅ Deploy keys
- ✅ Estatísticas de segurança

## 🎨 Dashboard Features

O dashboard HTML gerado inclui:

- 📊 Métricas em cards visuais
- 🚨 Achados críticos destacados
- 📈 Estatísticas consolidadas
- 💡 Recomendações de segurança
- 🎯 Checklist de ações
- 🔗 Links para documentação oficial

## 🔍 Queries Customizadas

Você pode adicionar suas próprias queries SQL:

1. Crie um arquivo `.sql` em `steampipe/queries/`
2. Escreva queries usando as tabelas do [GitHub Plugin](https://hub.steampipe.io/plugins/turbot/github/tables)
3. O script `run_audit.py` executará automaticamente

### Exemplo de Query Customizada

```sql
-- Repositórios com muitas issues abertas
SELECT
  name as "Repositório",
  open_issues_count as "Issues Abertas",
  visibility as "Visibilidade"
FROM
  github_repository
WHERE
  owner_login = (SELECT login FROM github_organization LIMIT 1)
  AND open_issues_count > 50
ORDER BY
  open_issues_count DESC;
```

## 📝 Issues Automáticas

O workflow cria automaticamente uma GitHub Issue quando:

- ✅ Achados críticos são detectados
- ✅ Achados de alta severidade são encontrados

A issue inclui:
- 📋 Resumo executivo
- 🚨 Achados críticos e de alta severidade
- 📋 Checklist de recomendações
- 🔗 Links para documentação

## 🛠️ Troubleshooting

### Erro: "Resource not accessible by integration"

**Solução**: Verifique as permissões do workflow:
1. `Settings` → `Actions` → `General`
2. Selecione `Read and write permissions`

### Erro: "Steampipe plugin not found"

**Solução**: O workflow instala automaticamente. Se persistir:
1. Verifique logs do step "Install GitHub Plugin"
2. Pode ser problema temporário de rede

### Token sem permissões suficientes

**Solução**: Recrie o token com os scopes:
- `repo`, `admin:org` (read), `read:user`

### Dashboard não está sendo gerado

**Solução**:
1. Verifique se Python 3.11+ está instalado
2. Revise logs do step "Generate Security Dashboard"

## 📚 Referências

- [Steampipe Documentation](https://steampipe.io/docs)
- [GitHub Plugin Tables](https://hub.steampipe.io/plugins/turbot/github/tables)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 🤝 Contribuindo

Contribuições são bem-vindas! Para adicionar:

1. Novas queries SQL
2. Melhorias no dashboard
3. Análises adicionais
4. Exportação para outros formatos

Faça um fork e envie um PR!

## 📄 Licença

MIT License - Sinta-se livre para usar e modificar!

## 🆘 Suporte

Precisa de ajuda?

1. Verifique a seção [Troubleshooting](#-troubleshooting)
2. Revise os logs do workflow no GitHub Actions
3. Consulte a [documentação do Steampipe](https://steampipe.io/docs)
4. Abra uma issue neste repositório

---

🤖 **Automatize sua governança de segurança com org-security-scan!**

*Powered by Steampipe + GitHub Actions*
