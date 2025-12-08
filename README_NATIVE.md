# 🔐 GitHub Organization Security Scan (Native API)

**Dashboard contínuo de segurança para QUALQUER organização GitHub** usando **GitHub API REST nativa**.

[![Generic](https://img.shields.io/badge/works-any%20org-brightgreen)]()
[![Auto-detect](https://img.shields.io/badge/auto--detect-organization-blue)]()
[![No Dependencies](https://img.shields.io/badge/no%20external%20deps-native%20API-orange)]()
[![MIT](https://img.shields.io/badge/license-MIT-green)]()

## 🌟 Características Principais

✅ **100% Nativo do GitHub** - Usa apenas GitHub API REST (sem dependências externas)
✅ **Zero Instalação** - Não precisa instalar Steampipe ou outras ferramentas
✅ **Funciona em qualquer organização** - Detecção automática via token
✅ **Setup em 2 passos** - Pronto em menos de 3 minutos
✅ **Totalmente automatizado** - Execução semanal + manual
✅ **Dashboard interativo** - HTML com insights visuais

## 🚀 Quick Start (3 Minutos)

### 1. Criar GitHub Token

1. Acesse: https://github.com/settings/tokens
2. Clique em `Generate new token (classic)`
3. Selecione os scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:org` (Read org and team membership)
   - ✅ `read:user` (Read user profile data)
4. Copie o token

### 2. Configurar no GitHub Actions

1. Vá para `Settings` → `Secrets and variables` → `Actions`
2. Clique em `New repository secret`
3. Nome: `ORG_SECURITY_TOKEN`
4. Valor: Cole o token
5. Clique em `Add secret`

### 3. Executar!

1. Vá para `Actions` no repositório
2. Selecione `Organization Security Scan`
3. Clique em `Run workflow`

**Pronto!** 🎉 O workflow vai executar e gerar o dashboard automaticamente.

## 💻 Teste Local (Opcional)

Quer testar localmente antes de rodar no GitHub Actions?

```bash
# 1. Configure seu token
export GITHUB_TOKEN='seu_token_aqui'

# 2. Execute o teste
./scripts/test_local_native.sh
```

**Requisitos locais:**
- ✅ Python 3.7+
- ✅ Biblioteca `requests` (`pip install requests`)
- ✅ Token do GitHub

**Isso é tudo!** Não precisa instalar Steampipe, PostgreSQL ou qualquer outra ferramenta.

## 🔍 O Que é Auditado?

### 📦 Repositórios
- Total de repositórios (público/privados)
- Repositórios sem descrição
- Repositórios inativos (>6 meses)
- Repositórios sem licença
- Repositórios públicos (potencial exposição)

### 🛡️ Branch Protection
- Repositórios com/sem branch protection
- Configurações de proteção
- Regras aplicadas no branch principal

### 👥 Usuários e Permissões
- Total de membros
- Colaboradores externos
- Times da organização
- Membros sem 2FA (quando disponível)

### 🔒 Segurança
- Secret scanning habilitado
- Dependabot habilitado
- Configurações de segurança por repositório

## 📊 Saída

O script gera:

1. **Dashboard HTML** - Visualização interativa com gráficos
   - `reports/security_dashboard_latest.html`

2. **Relatório JSON Consolidado** - Todos os dados em um arquivo
   - `reports/audit_results_TIMESTAMP.json`

3. **Relatórios Individuais** - Por categoria
   - `reports/results/repositories_TIMESTAMP.json`
   - `reports/results/branch_protection_TIMESTAMP.json`
   - `reports/results/users_permissions_TIMESTAMP.json`
   - `reports/results/security_settings_TIMESTAMP.json`

## 🆚 Steampipe vs API Nativa

| Característica | Steampipe (Antigo) | API Nativa (Novo) |
|----------------|-------------------|-------------------|
| Instalação | ❌ Requer sudo | ✅ Não requer instalação |
| Dependências | ❌ PostgreSQL, plugins | ✅ Apenas Python + requests |
| Tamanho | ❌ ~100MB | ✅ ~5KB de código |
| Velocidade | ⚠️ Média | ✅ Rápida |
| Manutenção | ❌ Alta | ✅ Baixa |
| Portabilidade | ❌ Limitada | ✅ Máxima |

## 🔧 Arquitetura

```
┌─────────────────────────────────────────┐
│        GitHub Actions Workflow          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   github_api_audit.py (NEW!)            │
│   - GitHubAuditor class                 │
│   - Direct REST API calls               │
│   - No external dependencies            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         GitHub REST API                 │
│   - /orgs/{org}/repos                   │
│   - /orgs/{org}/members                 │
│   - /repos/{owner}/{repo}/branches      │
│   - etc.                                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│       generate_dashboard.py             │
│       - Parse JSON results              │
│       - Generate HTML dashboard         │
└─────────────────────────────────────────┘
```

## 📝 Comparação de Código

### Antes (Steampipe):
```bash
# Instalar Steampipe
sudo /bin/sh -c "$(curl -fsSL https://steampipe.io/install/steampipe.sh)"

# Instalar plugin
steampipe plugin install github

# Configurar
mkdir -p ~/.steampipe/config
echo 'connection "github" { ... }' > ~/.steampipe/config/github.spc

# Iniciar serviço
steampipe service start

# Executar queries SQL
steampipe query "SELECT * FROM github_repository WHERE ..."
```

### Agora (API Nativa):
```bash
# Apenas Python!
export GITHUB_TOKEN='seu_token'
python3 scripts/github_api_audit.py
```

## 🚀 Workflow GitHub Actions

O workflow foi simplificado drasticamente:

```yaml
- name: Install Python Dependencies
  run: pip install requests

- name: Run Security Audit (Native GitHub API)
  env:
    GITHUB_TOKEN: ${{ secrets.ORG_SECURITY_TOKEN }}
  run: python3 scripts/github_api_audit.py

- name: Generate Security Dashboard
  run: python3 scripts/generate_dashboard.py
```

**Tempo de execução:**
- Antes: ~5-8 minutos (instalação do Steampipe + plugins)
- Agora: ~1-2 minutos (apenas API calls)

## 🎯 Casos de Uso

1. **Auditoria Contínua** - Execução semanal automática
2. **Compliance** - Validar configurações de segurança
3. **Relatórios Executivos** - Dashboard visual para stakeholders
4. **Detecção de Riscos** - Identificar repos sem proteção
5. **Governança** - Monitorar usuários sem 2FA

## 🤝 Contribuindo

Agora que o código é 100% Python nativo, é muito mais fácil contribuir!

```bash
# Fork o repositório
git clone https://github.com/seu-usuario/org-security-scan
cd org-security-scan

# Edite o código
vim scripts/github_api_audit.py

# Teste localmente
export GITHUB_TOKEN='seu_token'
./scripts/test_local_native.sh

# Commit e PR
git add .
git commit -m "feat: adicionar nova auditoria"
git push
```

## 📚 Documentação da API

Este projeto usa as seguintes APIs do GitHub:

- [REST API - Repositories](https://docs.github.com/en/rest/repos)
- [REST API - Organizations](https://docs.github.com/en/rest/orgs)
- [REST API - Teams](https://docs.github.com/en/rest/teams)
- [REST API - Users](https://docs.github.com/en/rest/users)

## 🛡️ Segurança

- ✅ Token nunca é exposto em logs
- ✅ Apenas leitura (read-only scopes)
- ✅ Sem armazenamento de credenciais
- ✅ Rate limiting respeitado

## 📄 Licença

MIT License - Sinta-se livre para usar e modificar!

## 🆘 Suporte

Problemas? Abra uma issue!

---

🚀 **Auditoria de segurança simplificada com ferramentas nativas do GitHub!**

*Powered by GitHub REST API + Python*
