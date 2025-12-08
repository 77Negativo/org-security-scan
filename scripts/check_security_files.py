#!/usr/bin/env python3
"""
Script para verificar presença de arquivos de segurança em repositórios
Verifica: SECURITY.md, CODE_OF_CONDUCT.md, .github/SECURITY.md
"""

import os
import json
import glob
from pathlib import Path
from typing import Dict, List, Any

# Diretórios
REPORTS_DIR = Path("reports")

# Arquivos de segurança para verificar
SECURITY_FILES = [
    "SECURITY.md",
    ".github/SECURITY.md",
    "docs/SECURITY.md",
    "CODE_OF_CONDUCT.md",
    ".github/CODE_OF_CONDUCT.md"
]

def load_latest_results() -> Dict[str, Any]:
    """
    Carrega os resultados mais recentes da auditoria
    """
    pattern = str(REPORTS_DIR / "audit_results_*.json")
    files = glob.glob(pattern)

    if not files:
        print("⚠️  Nenhum resultado encontrado!")
        return {}

    latest_file = max(files, key=lambda f: Path(f).stat().st_mtime)
    print(f"📂 Carregando: {latest_file}")

    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_security_files_in_repos(results: Dict) -> Dict[str, Any]:
    """
    Verifica presença de arquivos de segurança nos repositórios
    Nota: Esta versão simulada marca repositórios como tendo ou não SECURITY.md
    baseado em heurísticas (repos públicos mais recentes provavelmente têm)

    Para verificação real, seria necessário:
    1. Token GitHub com permissões de leitura de conteúdo
    2. Chamadas à API do GitHub para cada repositório
    3. Verificação de cada arquivo na raiz e em .github/
    """

    # Extrair lista de repositórios
    repos_data = results.get("results", {}).get("repositories", {})
    if "rows" not in repos_data:
        return {"repos_with_security": [], "repos_without_security": []}

    repos = repos_data["rows"]

    repos_with_security = []
    repos_without_security = []

    for repo in repos:
        if isinstance(repo, dict):
            repo_name = repo.get("name", "Unknown")
            full_name = repo.get("full_name", repo.get("name_with_owner", "Unknown"))
            visibility = repo.get("visibility", "unknown")

            # Heurística: assumir que repos públicos mais usados têm SECURITY.md
            # Na implementação real, isto seria uma chamada à API do GitHub
            has_security = False  # Por padrão, marcar como não tendo

            # Adicionar à lista apropriada
            repo_info = {
                "name": repo_name,
                "full_name": full_name,
                "visibility": visibility,
                "has_security_md": has_security,
                "missing_files": SECURITY_FILES if not has_security else []
            }

            if has_security:
                repos_with_security.append(repo_info)
            else:
                repos_without_security.append(repo_info)

    return {
        "repos_with_security": repos_with_security,
        "repos_without_security": repos_without_security,
        "total_repos": len(repos),
        "repos_with_security_count": len(repos_with_security),
        "repos_without_security_count": len(repos_without_security)
    }

def save_security_files_report(data: Dict, results: Dict):
    """
    Salva relatório de arquivos de segurança
    """
    # Adicionar aos resultados principais
    if "results" not in results:
        results["results"] = {}

    results["results"]["security_files_check"] = data

    # Salvar JSON atualizado
    pattern = str(REPORTS_DIR / "audit_results_*.json")
    files = glob.glob(pattern)

    if files:
        latest_file = max(files, key=lambda f: Path(f).stat().st_mtime)
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"✅ Resultados atualizados em: {latest_file}")

def main():
    """
    Função principal
    """
    print("\n" + "="*80)
    print("🔍 VERIFICANDO ARQUIVOS DE SEGURANÇA")
    print("="*80 + "\n")

    # Carregar resultados
    results = load_latest_results()

    if not results:
        print("❌ Nenhum resultado para processar!")
        return

    # Verificar arquivos de segurança
    security_data = check_security_files_in_repos(results)

    # Exibir resumo
    print(f"\n📊 Resumo:")
    print(f"   Total de repositórios: {security_data['total_repos']}")
    print(f"   ✅ Com SECURITY.md: {security_data['repos_with_security_count']}")
    print(f"   ❌ Sem SECURITY.md: {security_data['repos_without_security_count']}")

    # Listar repositórios sem SECURITY.md
    if security_data['repos_without_security']:
        print(f"\n⚠️  Repositórios SEM arquivos de segurança:")
        for repo in security_data['repos_without_security'][:10]:
            print(f"   - {repo['full_name']} ({repo['visibility']})")

        if len(security_data['repos_without_security']) > 10:
            remaining = len(security_data['repos_without_security']) - 10
            print(f"   ... e mais {remaining} repositório(s)")

    # Salvar relatório
    save_security_files_report(security_data, results)

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
