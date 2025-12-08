# 🚀 Instalação Rápida - Qualquer Organização

Este workflow funciona em **qualquer organização GitHub** detectando automaticamente via token!

## ⚡ Setup em 3 Passos

### 1️⃣ Copiar Arquivos

Clone ou copie esta pasta `org-security-scan` para seu repositório:

```bash
# Opção A: Clone todo o repo
git clone https://github.com/77Negativo/observability-sec.git
cd observability-sec
cp -r org-security-scan/* seu-repositorio/

# Opção B: Download direto
# Baixe o ZIP e extraia a pasta org-security-scan
```

**Estrutura necessária:**
```
seu-repositorio/
├── .github/
│   └── workflows/
│       └── org-security-scan.yml   # ← Workflow principal
└── org-security-scan/
    ├── steampipe/queries/          # ← Queries SQL
    ├── scripts/                    # ← Scripts Python
    └── README.md
```

### 2️⃣ Criar GitHub Token

1. Acesse: https://github.com/settings/tokens/new
2. Nome: `org-security-scan`
3. **Scopes necessários:**
   - ✅ `repo` - Full control of repositories
   - ✅ `admin:org` → `read:org` - Read org data
   - ✅ `read:user` - Read user data
4. **Generate token** e copie

### 3️⃣ Configurar Secret

1. No seu repositório: `Settings` → `Secrets and variables` → `Actions`
2. `New repository secret`
3. **Name:** `ORG_SECURITY_TOKEN`
4. **Value:** Cole o token do passo 2
5. `Add secret`

## ✅ Pronto!

O workflow já está configurado para:
- ✅ **Detectar automaticamente** sua organização via token
- ✅ Executar **semanalmente** (segundas 9h UTC)
- ✅ Gerar **dashboard HTML** com insights
- ✅ Criar **issues** com achados críticos
- ✅ Salvar **relatórios** em JSON/CSV

## 🎯 Primeira Execução

### Executar Manualmente

1. Vá para: `Actions` no seu repositório
2. Selecione: `Organization Security Scan`
3. `Run workflow` → `Run workflow`
4. Aguarde 2-3 minutos

### Ver Resultados

**Dashboard:**
- Vá para a execução do workflow
- Baixe o artifact `security-reports-X`
- Abra: `security_dashboard_latest.html`

**Reports commitados:**
- Pasta: `org-security-scan/reports/`

**Issue criada:**
- Aba `Issues` (se houver achados críticos)

## ⚙️ Configurações Opcionais

### Alterar Frequência

Edite `.github/workflows/org-security-scan.yml`:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Segunda 9h UTC
```

Exemplos:
- `'0 0 * * *'` - Diariamente à meia-noite
- `'0 9 * * 1,4'` - Segunda e quinta 9h
- `'0 */6 * * *'` - A cada 6 horas

### Workflow Permissions

Se o commit de reports falhar:

1. `Settings` → `Actions` → `General`
2. Workflow permissions: `Read and write permissions`
3. `Save`

## 🔧 Troubleshooting

### Erro: "Resource not accessible"
→ Configure "Read and write permissions" em Settings → Actions

### Erro: "Authentication failed"
→ Verifique se `ORG_SECURITY_TOKEN` está configurado

### Dashboard vazio
→ Verifique se o token tem os scopes `admin:org` e `read:org`

### Queries falhando
→ O token precisa ter acesso à organização

## 📊 O Que Será Auditado

✅ **Repositórios:**
- Visibilidade (público/privado)
- Atividade e última atualização
- Configurações gerais

✅ **Usuários:**
- Membros da organização
- Funções (admin/member)
- Data de entrada

✅ **Segurança:**
- Branch protection (onde configurado)
- Secret scanning status
- Dependabot status
- Vulnerability alerts

## 🌟 Recursos Avançados

### Customizar Queries

Edite os arquivos em `org-security-scan/steampipe/queries/`:
- `repositories.sql` - Dados de repos
- `users_permissions.sql` - Usuários e permissões
- `security_settings.sql` - Configurações de segurança

Consulte: https://hub.steampipe.io/plugins/turbot/github/tables

### Múltiplas Organizações

Para escanear múltiplas organizações:

1. Crie tokens separados para cada org
2. Configure secrets diferentes: `ORG1_TOKEN`, `ORG2_TOKEN`
3. Duplique o workflow alterando o secret usado

## 📝 Licença

MIT - Use livremente!

## 🆘 Suporte

- [Issues](https://github.com/77Negativo/observability-sec/issues)
- [Steampipe Docs](https://steampipe.io/docs)
- [GitHub Security](https://docs.github.com/en/code-security)

---

**Desenvolvido com** 🤖 [Claude Code](https://claude.com/claude-code)
