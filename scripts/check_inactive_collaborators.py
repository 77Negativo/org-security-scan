#!/usr/bin/env python3
"""
Script para identificar colaboradores inativos em repositórios
Verifica a última contribuição de cada colaborador e identifica aqueles
sem atividade por mais de X dias (padrão: 90 dias)
"""

import os
import json
import glob
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Diretórios
REPORTS_DIR = Path("reports")

# Configuração
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_API_BASE = "https://api.github.com"
INACTIVE_DAYS_THRESHOLD = 90  # Dias sem atividade para considerar inativo

def get_headers() -> Dict[str, str]:
    """Retorna headers para requisições à API do GitHub"""
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN não configurado")

    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def load_latest_results() -> Dict[str, Any]:
    """Carrega os resultados mais recentes da auditoria"""
    pattern = str(REPORTS_DIR / "audit_results_*.json")
    files = glob.glob(pattern)

    if not files:
        print("⚠️  Nenhum resultado encontrado!")
        return {}

    latest_file = max(files, key=lambda f: Path(f).stat().st_mtime)
    print(f"📂 Carregando: {latest_file}")

    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_repository_collaborators(repo_full_name: str) -> List[Dict]:
    """
    Obtém lista de colaboradores de um repositório via API

    Args:
        repo_full_name: Nome completo do repo (owner/repo)

    Returns:
        Lista de colaboradores com permissões
    """
    url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/collaborators"

    try:
        response = requests.get(url, headers=get_headers(), timeout=10)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"⚠️  Repositório não encontrado ou sem permissão: {repo_full_name}")
            return []
        else:
            print(f"⚠️  Erro ao obter colaboradores de {repo_full_name}: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro na requisição para {repo_full_name}: {str(e)}")
        return []

def get_user_last_activity(username: str, repo_full_name: str) -> Optional[datetime]:
    """
    Obtém a data da última atividade de um usuário em um repositório

    Args:
        username: Login do usuário GitHub
        repo_full_name: Nome completo do repo (owner/repo)

    Returns:
        Data da última atividade ou None se não houver atividade
    """
    # Endpoint de commits do usuário no repositório
    url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/commits"
    params = {
        "author": username,
        "per_page": 1  # Apenas o commit mais recente
    }

    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=10)

        if response.status_code == 200:
            commits = response.json()
            if commits:
                # Pegar a data do commit mais recente
                commit_date_str = commits[0]["commit"]["author"]["date"]
                # Formato: 2024-01-15T10:30:00Z
                return datetime.strptime(commit_date_str, "%Y-%m-%dT%H:%M:%SZ")
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"⚠️  Erro ao obter última atividade de {username} em {repo_full_name}: {str(e)}")
        return None

def calculate_inactive_days(last_activity: Optional[datetime]) -> int:
    """
    Calcula quantos dias desde a última atividade

    Args:
        last_activity: Data da última atividade

    Returns:
        Número de dias inativos
    """
    if not last_activity:
        return 9999  # Valor alto para indicar "nunca contribuiu"

    now = datetime.utcnow()
    delta = now - last_activity
    return delta.days

def check_inactive_collaborators(results: Dict, days_threshold: int = INACTIVE_DAYS_THRESHOLD) -> Dict[str, Any]:
    """
    Verifica colaboradores inativos em todos os repositórios

    Args:
        results: Resultados da auditoria
        days_threshold: Número de dias para considerar inativo

    Returns:
        Dicionário com dados de colaboradores inativos
    """
    print(f"\n🔍 Verificando colaboradores inativos (threshold: {days_threshold} dias)...")

    # Extrair repositórios
    repos_data = results.get("results", {}).get("repositories", {})
    if "rows" not in repos_data:
        print("❌ Nenhum repositório encontrado nos resultados")
        return {"inactive_collaborators": [], "total_checked": 0}

    repos = repos_data["rows"]
    inactive_collaborators = []
    total_collaborators_checked = 0

    for repo in repos:
        if not isinstance(repo, dict):
            continue

        repo_name = repo.get("name", "Unknown")
        repo_full_name = repo.get("full_name") or repo.get("name_with_owner")

        if not repo_full_name:
            continue

        print(f"\n📦 Verificando repositório: {repo_full_name}")

        # Obter colaboradores do repositório
        collaborators = get_repository_collaborators(repo_full_name)

        for collaborator in collaborators:
            username = collaborator.get("login")
            permissions = collaborator.get("permissions", {})

            if not username:
                continue

            total_collaborators_checked += 1

            # Obter última atividade
            last_activity = get_user_last_activity(username, repo_full_name)
            inactive_days = calculate_inactive_days(last_activity)

            # Se inativo por mais que o threshold
            if inactive_days >= days_threshold:
                status = "NUNCA CONTRIBUIU" if inactive_days == 9999 else f"{inactive_days} dias inativo"

                inactive_data = {
                    "username": username,
                    "repository": repo_full_name,
                    "last_activity": last_activity.strftime("%Y-%m-%d") if last_activity else "Nunca",
                    "inactive_days": inactive_days if inactive_days != 9999 else "∞",
                    "permissions": {
                        "admin": permissions.get("admin", False),
                        "push": permissions.get("push", False),
                        "pull": permissions.get("pull", False)
                    },
                    "risk_level": "HIGH" if permissions.get("admin") else "MEDIUM",
                    "status": status
                }

                inactive_collaborators.append(inactive_data)
                print(f"   ⚠️  {username}: {status}")
            else:
                print(f"   ✅ {username}: Ativo ({inactive_days} dias)")

    return {
        "inactive_collaborators": inactive_collaborators,
        "total_checked": total_collaborators_checked,
        "inactive_count": len(inactive_collaborators),
        "threshold_days": days_threshold,
        "check_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

def save_inactive_collaborators_report(data: Dict, results: Dict):
    """
    Salva relatório de colaboradores inativos

    Args:
        data: Dados de colaboradores inativos
        results: Resultados completos da auditoria
    """
    # Adicionar aos resultados principais
    if "results" not in results:
        results["results"] = {}

    results["results"]["inactive_collaborators_check"] = data

    # Salvar JSON atualizado
    pattern = str(REPORTS_DIR / "audit_results_*.json")
    files = glob.glob(pattern)

    if files:
        latest_file = max(files, key=lambda f: Path(f).stat().st_mtime)
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n✅ Resultados salvos em: {latest_file}")

def main():
    """Função principal"""
    print("\n" + "="*80)
    print("⏰ VERIFICANDO COLABORADORES INATIVOS")
    print("="*80 + "\n")

    # Verificar token
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN não configurado!")
        print("   Configure a variável de ambiente GITHUB_TOKEN")
        return

    print(f"🔑 Token GitHub configurado")
    print(f"📅 Threshold de inatividade: {INACTIVE_DAYS_THRESHOLD} dias")

    # Carregar resultados
    results = load_latest_results()

    if not results:
        print("❌ Nenhum resultado para processar!")
        return

    # Verificar colaboradores inativos
    inactive_data = check_inactive_collaborators(results, INACTIVE_DAYS_THRESHOLD)

    # Exibir resumo
    print(f"\n{'='*80}")
    print(f"📊 RESUMO:")
    print(f"   Total de colaboradores verificados: {inactive_data['total_checked']}")
    print(f"   Colaboradores inativos: {inactive_data['inactive_count']}")
    print(f"   Threshold: {inactive_data['threshold_days']} dias")
    print(f"   Data da verificação: {inactive_data['check_date']}")

    # Listar colaboradores inativos por nível de risco
    if inactive_data['inactive_collaborators']:
        print(f"\n⚠️  COLABORADORES INATIVOS IDENTIFICADOS:")

        # Separar por nível de risco
        high_risk = [c for c in inactive_data['inactive_collaborators'] if c['risk_level'] == 'HIGH']
        medium_risk = [c for c in inactive_data['inactive_collaborators'] if c['risk_level'] == 'MEDIUM']

        if high_risk:
            print(f"\n   🔴 ALTO RISCO (com permissão ADMIN):")
            for collab in high_risk[:5]:
                print(f"      - {collab['username']} em {collab['repository']}")
                print(f"        Última atividade: {collab['last_activity']} ({collab['status']})")

        if medium_risk:
            print(f"\n   🟡 MÉDIO RISCO (sem permissão ADMIN):")
            for collab in medium_risk[:5]:
                print(f"      - {collab['username']} em {collab['repository']}")
                print(f"        Última atividade: {collab['last_activity']} ({collab['status']})")

        if len(inactive_data['inactive_collaborators']) > 10:
            remaining = len(inactive_data['inactive_collaborators']) - 10
            print(f"\n   ... e mais {remaining} colaborador(es) inativo(s)")
    else:
        print(f"\n✅ Nenhum colaborador inativo encontrado!")

    # Salvar relatório
    save_inactive_collaborators_report(inactive_data, results)

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
