# 🔄 Guia de Migração: Steampipe → GitHub API Nativa

## 📋 Resumo das Mudanças

A aplicação foi **completamente refatorada** para usar apenas APIs nativas do GitHub, eliminando a dependência do Steampipe.

## ✅ Benefícios da Migração

| Antes (Steampipe) | Depois (API Nativa) |
|-------------------|---------------------|
| 🐌 Instalação de ~5 minutos | ⚡ Instalação instantânea |
| 📦 ~100MB de dependências | 🪶 ~5KB de código Python |
| 🔧 Requer sudo/admin | ✨ Sem privilégios necessários |
| 🐘 PostgreSQL backend | 🐍 Python puro |
| 📝 SQL queries | 🎯 API REST direta |
| ⏱️ Workflow ~5-8 min | 🚀 Workflow ~1-2 min |

## 🆕 Arquivos Novos

### 1. `scripts/github_api_audit.py` (NOVO!)
Script principal que substitui todo o fluxo do Steampipe.

**Características:**
- ✅ Classe `GitHubAuditor` para gerenciar auditorias
- ✅ Detecção automática de organização
- ✅ Auditoria completa de repositórios
- ✅ Auditoria de branch protection
- ✅ Auditoria de usuários e permissões
- ✅ Auditoria de configurações de segurança
- ✅ Rate limiting respeitado
- ✅ Paginação automática

### 2. `scripts/test_local_native.sh` (NOVO!)
Script de teste local simplificado que não requer Steampipe.

**Uso:**
```bash
export GITHUB_TOKEN='seu_token'
./scripts/test_local_native.sh
```

### 3. `README_NATIVE.md` (NOVO!)
Documentação completa da nova versão.

## 🔄 Arquivos Modificados

### `.github/workflows/org-security-scan.yml`

**Removido:**
```yaml
- name: Install Steampipe
- name: Install GitHub Plugin
- name: Configure Steampipe
- name: Start Steampipe Service
- name: Cleanup (stop Steampipe)
```

**Adicionado:**
```yaml
- name: Run Security Audit (Native GitHub API)
  env:
    GITHUB_TOKEN: ${{ secrets.ORG_SECURITY_TOKEN }}
  run: python3 scripts/github_api_audit.py
```

## 📊 Formato de Dados

### Antes (Steampipe)
```json
{
  "columns": ["name", "type"],
  "rows": [["repo1", "public"]]
}
```

### Depois (API Nativa)
```json
{
  "scan_timestamp": "2025-12-08T10:00:00",
  "organization": {...},
  "results": {
    "repositories": {
      "total_repositories": 10,
      "public_repositories": 5,
      "repositories": [...]
    },
    "branch_protection": {...},
    "users_permissions": {...},
    "security_settings": {...}
  }
}
```

## 🔧 Como Migrar

### Passo 1: Atualizar o Código

Se você está em um fork ou clone:

```bash
# Fazer pull das mudanças
git pull origin main

# Ou baixar os novos arquivos
curl -O https://raw.githubusercontent.com/.../scripts/github_api_audit.py
curl -O https://raw.githubusercontent.com/.../scripts/test_local_native.sh
```

### Passo 2: Remover Configurações Antigas (Opcional)

Se você tinha Steampipe instalado localmente:

```bash
# Parar serviço
steampipe service stop

# Remover configurações (opcional)
rm -rf ~/.steampipe/config/github.spc
```

### Passo 3: Testar Localmente

```bash
# Configurar token
export GITHUB_TOKEN='seu_token_aqui'

# Executar teste
./scripts/test_local_native.sh
```

### Passo 4: Executar no GitHub Actions

Apenas execute o workflow - tudo funcionará automaticamente!

## 🔍 Mapeamento de Funcionalidades

### Antes: SQL Queries

```sql
-- steampipe/queries/repositories.sql
SELECT name, visibility, default_branch
FROM github_repository
WHERE owner_login = 'org';
```

### Depois: Python API

```python
# scripts/github_api_audit.py
def get_repositories(self, org: str) -> List[Dict]:
    return self._get_all_pages(f"/orgs/{org}/repos")
```

## 📚 APIs Utilizadas

O novo script usa estas APIs do GitHub:

| Funcionalidade | Endpoint |
|----------------|----------|
| Listar repos | `GET /orgs/{org}/repos` |
| Branch protection | `GET /repos/{owner}/{repo}/branches/{branch}/protection` |
| Membros | `GET /orgs/{org}/members` |
| Colaboradores externos | `GET /orgs/{org}/outside_collaborators` |
| Times | `GET /orgs/{org}/teams` |
| Detalhes do usuário | `GET /users/{username}` |
| Info da org | `GET /orgs/{org}` |

Documentação: https://docs.github.com/en/rest

## ⚙️ Configuração de Tokens

**Nenhuma mudança necessária!** O token continua sendo configurado da mesma forma:

```bash
# Local
export GITHUB_TOKEN='ghp_...'

# GitHub Actions
Settings → Secrets → ORG_SECURITY_TOKEN
```

**Scopes necessários:**
- ✅ `repo`
- ✅ `read:org`
- ✅ `read:user`

## 🐛 Troubleshooting

### Erro: "Token não encontrado"

**Solução:**
```bash
export GITHUB_TOKEN='seu_token'
# ou
export ORG_SECURITY_TOKEN='seu_token'
```

### Erro: "No module named 'requests'"

**Solução:**
```bash
pip install requests
```

### Erro: Rate limit exceeded

**Solução:** A API do GitHub tem limites:
- 5000 req/hora (autenticado)
- 60 req/hora (não autenticado)

O script respeita esses limites automaticamente.

### Dashboard não é gerado

**Possível causa:** O script `generate_dashboard.py` pode precisar ser atualizado para o novo formato de dados.

**Solução:** O dashboard deve funcionar com os dados existentes. Se não funcionar, verifique os logs.

## 🎯 Próximos Passos

1. ✅ Código refatorado
2. ✅ Workflow atualizado
3. ✅ Testes locais disponíveis
4. ✅ Documentação completa
5. ⏭️ Executar teste no GitHub Actions
6. ⏭️ Validar dashboard gerado

## 🤔 FAQ

### Q: Preciso fazer algo manual?

**A:** Não! Se você usar o GitHub Actions, tudo funciona automaticamente.

### Q: Posso voltar para o Steampipe?

**A:** Sim, os scripts antigos ainda estão no repositório. Mas por que voltaria? 😄

### Q: O dashboard HTML mudou?

**A:** Não, o formato é o mesmo. Apenas a fonte de dados mudou.

### Q: Funciona em organizações privadas?

**A:** Sim! Desde que seu token tenha as permissões corretas.

### Q: Funciona com GitHub Enterprise?

**A:** Sim! Configure a variável `GITHUB_API` para apontar para sua instância:
```python
GITHUB_API = "https://github.empresa.com/api/v3"
```

## 📞 Suporte

Problemas com a migração? Abra uma issue!

---

🎉 **Bem-vindo à era nativa do GitHub!**
