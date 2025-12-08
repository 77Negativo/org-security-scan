# 🚀 Quick Start Guide

Guia rápido para começar a usar o org-security-scan em 5 minutos!

## ⚡ Setup Rápido

### 1. Criar GitHub Token (2 minutos)

1. Acesse: https://github.com/settings/tokens/new
2. Nome do token: `org-security-scan`
3. Selecione os scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `admin:org` → marque apenas `read:org`
   - ✅ `read:user` (Read ALL user profile data)
4. Clique em `Generate token`
5. **Copie o token gerado** (você não verá novamente!)

### 2. Adicionar Secret no Repositório (1 minuto)

1. No seu repositório GitHub, vá para: `Settings` → `Secrets and variables` → `Actions`
2. Clique em `New repository secret`
3. **Name:** `ORG_SECURITY_TOKEN`
4. **Value:** Cole o token do passo 1
5. Clique em `Add secret`

### 3. Habilitar Permissões do Workflow (1 minuto)

1. Ainda em Settings, vá para: `Actions` → `General`
2. Em "Workflow permissions", selecione:
   - ✅ `Read and write permissions`
3. Clique em `Save`

### 4. Executar o Workflow (1 minuto)

1. Vá para a aba `Actions`
2. Selecione `Organization Security Scan` na lista de workflows
3. Clique em `Run workflow`
4. Selecione a branch `main`
5. Clique em `Run workflow` (botão verde)

### 5. Visualizar Resultados

Aguarde alguns minutos e depois:

1. **Dashboard HTML:**
   - Vá para a execução do workflow
   - Baixe o artifact `security-reports-XXX`
   - Extraia e abra `security_dashboard_TIMESTAMP.html` no navegador

2. **Issue Criada:**
   - Verifique a aba `Issues`
   - Uma nova issue será criada com os achados (se houver)

3. **Commit no Repo:**
   - Os reports são commitados automaticamente na pasta `reports/`

## 🧪 Teste Local (Opcional)

Para testar localmente antes de rodar no GitHub:

### 1. Instalar Steampipe

```bash
# Linux/macOS
sudo /bin/sh -c "$(curl -fsSL https://steampipe.io/install/steampipe.sh)"

# Verificar instalação
steampipe -v
```

### 2. Instalar Plugin GitHub

```bash
steampipe plugin install github
```

### 3. Configurar Credenciais

```bash
# Copiar exemplo
cp steampipe.spc.example ~/.steampipe/config/github.spc

# Editar e adicionar seu token
nano ~/.steampipe/config/github.spc
# (substitua "ghp_your_token_here" pelo seu token real)
```

### 4. Executar Teste

```bash
# Dar permissão de execução
chmod +x scripts/test_local.sh

# Rodar teste
./scripts/test_local.sh
```

## 📊 O Que Você Verá

O dashboard mostrará:

### Métricas Principais
- 📦 Total de repositórios analisados
- 👥 Número de usuários e times
- 🔒 Configurações de segurança
- ⚠️ Achados críticos

### Achados Comuns

**CRÍTICO:**
- 🔐 Usuários sem autenticação de dois fatores (2FA)
- 📦 Repositórios públicos com código sensível

**ALTO:**
- 🛡️ Repositórios sem branch protection
- 🔍 Secret scanning desabilitado
- 🤖 Dependabot desabilitado

**MÉDIO:**
- 📝 Repositórios sem descrição
- 📋 Licença não definida
- 👥 Colaboradores externos sem revisão

## 🔄 Execução Automática

O workflow roda automaticamente:
- ⏰ **Semanalmente:** Toda segunda-feira às 9h UTC
- 📝 **Em push para main:** Para testes

Para mudar o horário, edite o arquivo `.github/workflows/org-security-scan.yml`:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Formato: minuto hora dia-do-mês mês dia-da-semana
```

Exemplos de cron:
- `'0 0 * * *'` - Diariamente à meia-noite
- `'0 9 * * 1,4'` - Segunda e quinta às 9h
- `'0 */6 * * *'` - A cada 6 horas

## 🎯 Próximos Passos

Após a primeira execução:

1. **Revisar Achados:**
   - Abra o dashboard gerado
   - Revise a issue criada
   - Priorize ações críticas

2. **Implementar Correções:**
   - Habilitar 2FA para todos os usuários
   - Configurar branch protection
   - Ativar secret scanning e Dependabot

3. **Customizar:**
   - Adicione suas próprias queries SQL
   - Ajuste o dashboard conforme necessário
   - Configure alertas adicionais

## ❓ Problemas Comuns

### "Resource not accessible by integration"
**Solução:** Habilite "Read and write permissions" em Settings → Actions → General

### "Authentication failed"
**Solução:** Verifique se o secret `ORG_SECURITY_TOKEN` está configurado corretamente

### Dashboard não gerado
**Solução:** Verifique os logs do workflow na aba Actions

### Queries muito lentas
**Solução:** O GitHub API tem rate limits. O Steampipe respeita esses limites automaticamente.

## 📚 Recursos Adicionais

- [README Completo](README.md) - Documentação detalhada
- [Steampipe Docs](https://steampipe.io/docs) - Documentação do Steampipe
- [GitHub Tables](https://hub.steampipe.io/plugins/turbot/github/tables) - Tabelas disponíveis
- [GitHub Security](https://docs.github.com/en/code-security) - Boas práticas de segurança

## 🆘 Precisa de Ajuda?

1. Revise o README completo
2. Verifique os logs do workflow
3. Consulte a documentação do Steampipe
4. Abra uma issue neste repositório

---

**Pronto!** 🎉 Você agora tem um dashboard automático de segurança para sua organização GitHub!
