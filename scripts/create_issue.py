#!/usr/bin/env python3
"""
Script para criar GitHub Issue com achados de segurança
"""

import json
import glob
import os
from datetime import datetime
from pathlib import Path
import subprocess

# Diretórios
RESULTS_DIR = Path("reports/results")
REPORTS_DIR = Path("reports")

def load_latest_results() -> dict:
    """
    Carrega os resultados mais recentes
    """
    pattern = str(REPORTS_DIR / "audit_results_*.json")
    files = glob.glob(pattern)

    if not files:
        print("⚠️  Nenhum resultado encontrado!")
        return {}

    latest_file = max(files, key=lambda f: Path(f).stat().st_mtime)

    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_results(results: dict) -> dict:
    """
    Analisa os resultados e identifica problemas
    """
    summary = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": [],
        "info": []
    }

    if not results or "results" not in results:
        return summary

    data = results["results"]

    # Analisar repositórios
    if "repositories" in data and "rows" in data["repositories"]:
        rows = data["repositories"]["rows"]

        # Contar repositórios públicos (simplificado)
        public_count = sum(1 for r in rows if isinstance(r, list) and "public" in str(r).lower())
        if public_count > 0:
            summary["high"].append(
                f"📦 **{public_count} repositório(s) público(s)** - Verificar se contêm código sensível"
            )

    # Analisar usuários
    if "users_permissions" in data and "rows" in data["users_permissions"]:
        summary["critical"].append(
            "🔐 **Verificar 2FA** - Garantir que todos os usuários têm autenticação de dois fatores habilitada"
        )

    # Analisar configurações de segurança
    if "security_settings" in data and "rows" in data["security_settings"]:
        summary["high"].append(
            "🛡️ **Verificar Branch Protection** - Garantir que repositórios ativos têm proteção de branch configurada"
        )
        summary["high"].append(
            "🔍 **Verificar Secret Scanning** - Habilitar em todos os repositórios"
        )

    return summary

def create_issue_body(results: dict, summary: dict) -> str:
    """
    Cria o corpo da issue
    """
    timestamp = results.get("scan_timestamp", datetime.now().isoformat())

    body = f"""# 🔐 Relatório de Segurança da Organização

**Data da Varredura:** {timestamp}

## 📊 Resumo Executivo

Esta issue foi criada automaticamente pelo workflow de segurança organizacional.

## 🚨 Achados Críticos

"""

    if summary["critical"]:
        for item in summary["critical"]:
            body += f"- {item}\n"
    else:
        body += "✅ Nenhum achado crítico.\n"

    body += "\n## ⚠️ Achados de Alta Severidade\n\n"

    if summary["high"]:
        for item in summary["high"]:
            body += f"- {item}\n"
    else:
        body += "✅ Nenhum achado de alta severidade.\n"

    body += """
## 📋 Recomendações

### Imediatas
- [ ] Habilitar 2FA para todos os usuários da organização
- [ ] Configurar branch protection em repositórios ativos
- [ ] Ativar secret scanning e push protection

### Curto Prazo
- [ ] Revisar permissões de colaboradores externos
- [ ] Habilitar Dependabot em todos os repositórios
- [ ] Arquivar repositórios inativos

### Médio Prazo
- [ ] Implementar política de revisão de código obrigatória
- [ ] Configurar webhooks para auditoria em tempo real
- [ ] Criar documentação de governança

## 📁 Arquivos Gerados

Os relatórios detalhados estão disponíveis nos artifacts do workflow:
- Dashboard HTML interativo
- Resultados em formato JSON
- Dados tabulares em CSV

## 🔗 Links Úteis

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [Requiring Two-Factor Authentication](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-two-factor-authentication-for-your-organization)

---

🤖 *Esta issue foi gerada automaticamente pelo org-security-scan workflow*
"""

    return body

def create_github_issue(title: str, body: str) -> bool:
    """
    Cria uma issue no GitHub usando gh CLI
    """
    try:
        # Criar issue usando gh CLI
        result = subprocess.run(
            [
                "gh", "issue", "create",
                "--title", title,
                "--body", body,
                "--label", "security,automated"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        print(f"✅ Issue criada com sucesso!")
        print(f"🔗 {result.stdout.strip()}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar issue: {e}")
        print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print("⚠️  gh CLI não encontrado. Pulando criação de issue.")
        print("💡 Para habilitar: instale o GitHub CLI (gh)")
        return False

def should_create_issue(summary: dict) -> bool:
    """
    Decide se deve criar uma issue baseado nos achados
    """
    # Criar issue se houver achados críticos ou de alta severidade
    has_critical = len(summary.get("critical", [])) > 0
    has_high = len(summary.get("high", [])) > 0

    return has_critical or has_high

def main():
    """
    Função principal
    """
    print("\n" + "="*80)
    print("📝 CRIANDO GITHUB ISSUE COM ACHADOS DE SEGURANÇA")
    print("="*80 + "\n")

    # Carregar resultados
    results = load_latest_results()

    if not results:
        print("❌ Nenhum resultado para processar!")
        return

    # Analisar resultados
    summary = analyze_results(results)

    # Verificar se deve criar issue
    if not should_create_issue(summary):
        print("ℹ️  Nenhum achado crítico. Issue não será criada.")
        return

    # Criar corpo da issue
    timestamp = datetime.now().strftime("%Y-%m-%d")
    title = f"🔐 Relatório de Segurança - {timestamp}"
    body = create_issue_body(results, summary)

    # Verificar se já existe uma issue similar recente
    print("🔍 Verificando issues existentes...")

    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--label", "security,automated", "--limit", "1", "--json", "title,createdAt"],
            capture_output=True,
            text=True,
            check=True
        )

        existing_issues = json.loads(result.stdout)

        if existing_issues:
            latest_issue = existing_issues[0]
            latest_date = latest_issue.get("createdAt", "")

            # Se já existe uma issue de hoje, não criar outra
            if timestamp in latest_date:
                print(f"ℹ️  Já existe uma issue de segurança criada hoje: {latest_issue.get('title')}")
                print("⏭️  Pulando criação de nova issue.")
                return

    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        print("⚠️  Não foi possível verificar issues existentes. Prosseguindo...")

    # Criar issue
    create_github_issue(title, body)

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
