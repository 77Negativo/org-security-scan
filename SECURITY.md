# Security Policy

## 🔐 Política de Segurança

Este documento descreve as políticas de segurança para o projeto **org-security-scan** e como reportar vulnerabilidades de forma responsável.

---

## 📋 Versões Suportadas

Atualmente, fornecemos atualizações de segurança para as seguintes versões:

| Versão | Suportada          | Status |
| ------ | ------------------ | ------ |
| main   | :white_check_mark: | Ativa  |
| v1.x   | :white_check_mark: | LTS    |
| < 1.0  | :x:                | EOL    |

---

## 🚨 Reportando uma Vulnerabilidade

**NÃO abra uma issue pública** para reportar vulnerabilidades de segurança.

### Processo de Divulgação Responsável

1. **Envie um relatório privado:**
   - **Email:** security@example.com
   - **GitHub Security Advisory:** Use o recurso [Private vulnerability reporting](https://github.com/77Negativo/observability-sec/security/advisories/new)

2. **Inclua as seguintes informações:**
   - Descrição detalhada da vulnerabilidade
   - Passos para reproduzir o problema
   - Impacto potencial
   - Versão afetada
   - Sugestões de correção (se houver)

3. **Resposta esperada:**
   - **Confirmação:** Dentro de 48 horas
   - **Avaliação inicial:** Dentro de 5 dias úteis
   - **Atualização de progresso:** Semanalmente até resolução
   - **Correção:** Dependendo da severidade (veja SLA abaixo)

### SLA de Resposta por Severidade

| Severidade | Tempo de Resposta | Tempo de Correção |
|------------|-------------------|-------------------|
| Crítica    | 24 horas          | 7 dias            |
| Alta       | 48 horas          | 14 dias           |
| Média      | 5 dias            | 30 dias           |
| Baixa      | 7 dias            | 60 dias           |

---

## 🔒 Escopo de Segurança

### Itens no Escopo

Este projeto lida com informações sensíveis de segurança de organizações GitHub. Os seguintes componentes estão no escopo de segurança:

#### 1. **Autenticação e Autorização**
- Gerenciamento de tokens GitHub (ORG_SECURITY_TOKEN)
- Permissões de acesso aos dados da organização
- Controle de acesso aos workflows

#### 2. **Processamento de Dados**
- Queries SQL do Steampipe
- Scripts Python de auditoria
- Geração de relatórios e dashboards

#### 3. **Armazenamento de Dados**
- Artifacts do GitHub Actions (retenção de 90 dias)
- Relatórios JSON/CSV/HTML
- Logs de execução

#### 4. **Dependências**
- Bibliotecas Python
- Plugin Steampipe GitHub
- GitHub Actions

### Itens Fora do Escopo

- Vulnerabilidades em dependências upstream (reporte ao projeto original)
- Problemas de infraestrutura do GitHub
- Configurações da organização GitHub (responsabilidade do administrador)

---

## 🛡️ Práticas de Segurança Implementadas

### Proteção de Secrets

```yaml
# Secrets gerenciados via GitHub Secrets
secrets:
  - ORG_SECURITY_TOKEN  # Token com permissões mínimas necessárias
```

**Permissões Mínimas Requeridas:**
- `repo` - Acesso a repositórios
- `admin:org:read` - Leitura de organizações
- `read:user` - Leitura de dados de usuários (opcional)

**NÃO conceda:**
- Permissões de escrita desnecessárias
- Acesso a webhooks
- Permissões de admin sem necessidade

### Sanitização de Dados

Todos os dados coletados são sanitizados antes de exibição:

```python
# Exemplo de sanitização
html.escape(user_input)  # Previne XSS
json.dumps(data, default=str)  # Serialização segura
```

### Validação de Entrada

```python
# Validação de paths
Path(file_path).resolve()  # Previne path traversal

# Validação de queries SQL
# Usa parameterização do Steampipe (proteção contra SQL injection)
```

### Isolamento de Execução

- Workflows executam em ambiente isolado (GitHub Actions)
- Sem acesso direto à infraestrutura da organização
- Princípio de privilégio mínimo

---

## 🔍 Vulnerabilidades Conhecidas

### Histórico de Segurança

Atualmente, não há vulnerabilidades conhecidas neste projeto.

**Última auditoria de segurança:** 2025-12-06

### Dependências com Vulnerabilidades

Monitoramos dependências usando:
- ✅ Dependabot (GitHub)
- ✅ Steampipe security scanning
- ✅ Python safety checks

---

## 🚀 Atualizações de Segurança

### Como Aplicar Patches

1. **Pull da branch main:**
   ```bash
   git pull origin main
   ```

2. **Atualizar dependências:**
   ```bash
   # Python
   pip install -r requirements.txt --upgrade

   # Steampipe
   steampipe plugin update github
   ```

3. **Re-executar workflow:**
   ```bash
   # Via GitHub Actions UI
   Actions → Organization Security Scan → Run workflow
   ```

### Notificações de Segurança

Para receber notificações de atualizações de segurança:

1. **Watch este repositório:**
   - Repository → Watch → Custom → Security alerts

2. **Configure GitHub Dependabot:**
   - Settings → Security & analysis → Enable Dependabot alerts

3. **Subscribe ao RSS:**
   - https://github.com/77Negativo/observability-sec/releases.atom

---

## 📊 Auditoria e Compliance

### Logs de Auditoria

Todos os workflows geram logs detalhados:

```
.github/workflows/org-security-scan.yml
├── Execution logs (GitHub Actions)
├── Audit results (JSON/CSV)
└── Dashboard reports (HTML)
```

**Retenção:** 90 dias (GitHub Actions default)

### Compliance

Este projeto auxilia no compliance com:

- ✅ **OWASP Top 10** - Identificação de vulnerabilidades
- ✅ **CIS Controls** - Inventário e controle de ativos
- ✅ **NIST Cybersecurity Framework** - Identificação e proteção
- ✅ **SOC 2** - Controles de segurança e monitoramento

---

## 🤝 Créditos de Segurança

Agradecemos aos pesquisadores de segurança que reportarem vulnerabilidades de forma responsável:

<!-- Nenhum até o momento -->

### Hall of Fame

| Pesquisador | Vulnerabilidade | Severidade | Data |
|-------------|----------------|------------|------|
| -           | -              | -          | -    |

---

## 📚 Recursos Adicionais

### Documentação de Segurança

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Steampipe Security](https://steampipe.io/docs/security)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

### Ferramentas de Segurança

- **Steampipe** - SQL-based security analysis
- **GitHub Advanced Security** - Code scanning e secret scanning
- **Dependabot** - Automated dependency updates

### Treinamento

- [GitHub Security Lab](https://securitylab.github.com/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

## 📞 Contato

### Equipe de Segurança

- **Email:** security@example.com
- **PGP Key:** [Disponível mediante solicitação]
- **Response Time:** 24-48 horas

### Canais Alternativos

- **GitHub Security Advisory:** Método preferido
- **Email criptografado:** security@example.com (PGP)

---

## 🔄 Política de Atualização

Este documento é revisado e atualizado:

- ✅ Trimestralmente (revisão de rotina)
- ✅ Após cada incidente de segurança
- ✅ Quando há mudanças significativas no projeto

**Última atualização:** 2025-12-06
**Próxima revisão:** 2025-03-06

---

## ⚖️ Divulgação de Vulnerabilidades

### Coordinated Disclosure

Seguimos o princípio de **Coordinated Vulnerability Disclosure**:

1. Pesquisador reporta vulnerabilidade privadamente
2. Equipe confirma e investiga
3. Correção é desenvolvida e testada
4. Patch é lançado
5. **Após 90 dias** ou lançamento do patch (o que vier primeiro):
   - Vulnerabilidade é divulgada publicamente
   - Crédito é dado ao pesquisador (se desejado)

### Bug Bounty

Atualmente, não oferecemos um programa de bug bounty formal, mas:

- ✅ Reconhecimento público (Hall of Fame)
- ✅ Créditos em release notes
- ✅ LinkedIn recommendations (mediante solicitação)

---

## 🎯 Melhores Práticas para Usuários

### Configuração Segura

1. **Use tokens com permissões mínimas:**
   ```bash
   # Permissões necessárias:
   - repo (read)
   - admin:org:read
   - read:user (opcional)

   # NÃO conceda:
   - repo (write)
   - admin:org (write)
   - workflow
   ```

2. **Rotacione tokens regularmente:**
   - Recomendado: A cada 90 dias
   - Mínimo: A cada 180 dias

3. **Monitore logs de acesso:**
   ```bash
   # GitHub → Settings → Security log
   # Verifique acessos incomuns
   ```

4. **Habilite 2FA:**
   - Obrigatório para administradores
   - Recomendado para todos os membros

### Armazenamento de Dados

- ⚠️ Dashboards podem conter informações sensíveis
- 🔒 Não compartilhe dashboards publicamente
- 🗑️ Apague artifacts antigos após análise
- 📦 Use criptografia para backups

---

## 📜 Licença e Responsabilidade

### Limitação de Responsabilidade

Este projeto é fornecido "como está", sem garantias de qualquer tipo. O uso deste software é de sua responsabilidade.

**Não nos responsabilizamos por:**
- Uso inadequado de tokens de acesso
- Vazamento de informações sensíveis
- Configurações incorretas da organização
- Danos resultantes de vulnerabilidades não reportadas

### Contribuições

Ao contribuir com patches de segurança:

1. Você concorda com a licença MIT do projeto
2. Você garante que tem direitos sobre o código
3. Você permite divulgação pública após correção

---

## ✅ Checklist de Segurança

Antes de usar este projeto, verifique:

- [ ] Token com permissões mínimas criado
- [ ] Secret `ORG_SECURITY_TOKEN` configurado
- [ ] 2FA habilitado na conta
- [ ] Workflow permissions revisadas
- [ ] Logs de auditoria habilitados
- [ ] Dependabot alerts habilitados
- [ ] Time de segurança notificado sobre deployment
- [ ] Documentação de segurança revisada
- [ ] Plano de resposta a incidentes definido

---

**Obrigado por ajudar a manter este projeto seguro!** 🔒

---

*Desenvolvido com* 🤖 *[Claude Code](https://claude.com/claude-code)*
*Baseado nas melhores práticas de* **OWASP, NIST, e GitHub Security**
