#!/usr/bin/env python3
"""
Script para executar auditoria de segurança usando GitHub API REST nativa
Elimina a dependência do Steampipe
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Configuração
GITHUB_TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('ORG_SECURITY_TOKEN') or os.environ.get('GITHUB_TOKEN')
GITHUB_API = "https://api.github.com"

# Diretórios
RESULTS_DIR = Path("reports/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Timestamp
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

class GitHubAuditor:
    """Classe para auditoria de segurança usando GitHub API"""

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.org_login = None

    def _get(self, endpoint: str, params: Dict = None) -> Any:
        """Faz requisição GET para a API do GitHub"""
        url = f"{GITHUB_API}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _get_all_pages(self, endpoint: str, params: Dict = None) -> List[Dict]:
        """Obtém todos os resultados paginados"""
        results = []
        page = 1
        per_page = 100

        if params is None:
            params = {}
        params['per_page'] = per_page

        while True:
            params['page'] = page
            data = self._get(endpoint, params)

            if isinstance(data, list):
                if not data:
                    break
                results.extend(data)
                if len(data) < per_page:
                    break
            else:
                # Se não for lista, retornar como está
                return data

            page += 1

        return results

    def get_authenticated_user(self) -> Dict:
        """Obtém informações do usuário autenticado"""
        return self._get("/user")

    def get_user_orgs(self) -> List[Dict]:
        """Obtém organizações do usuário"""
        return self._get_all_pages("/user/orgs")

    def detect_organization(self) -> str:
        """Detecta automaticamente a organização baseado no contexto"""
        # Primeiro tenta pegar do ambiente do GitHub Actions
        github_repo = os.environ.get('GITHUB_REPOSITORY')
        if github_repo and '/' in github_repo:
            org = github_repo.split('/')[0]
            print(f"✅ Organização detectada do GITHUB_REPOSITORY: {org}")
            return org

        # Se não estiver no GitHub Actions, lista as orgs do usuário
        orgs = self.get_user_orgs()
        if orgs:
            org = orgs[0]['login']
            print(f"✅ Usando primeira organização do usuário: {org}")
            if len(orgs) > 1:
                print(f"ℹ️  Outras organizações disponíveis: {[o['login'] for o in orgs[1:]]}")
            return org

        # Fallback: usar o login do usuário
        user = self.get_authenticated_user()
        print(f"⚠️  Usando login do usuário: {user['login']}")
        return user['login']

    def get_organization(self, org: str) -> Dict:
        """Obtém informações da organização"""
        return self._get(f"/orgs/{org}")

    def get_repositories(self, org: str) -> List[Dict]:
        """Obtém todos os repositórios da organização"""
        print(f"📦 Buscando repositórios de {org}...")
        return self._get_all_pages(f"/orgs/{org}/repos", {"type": "all"})

    def get_organization_members(self, org: str) -> List[Dict]:
        """Obtém membros da organização"""
        print(f"👥 Buscando membros de {org}...")
        return self._get_all_pages(f"/orgs/{org}/members")

    def get_outside_collaborators(self, org: str) -> List[Dict]:
        """Obtém colaboradores externos"""
        print(f"🔍 Buscando colaboradores externos de {org}...")
        try:
            return self._get_all_pages(f"/orgs/{org}/outside_collaborators")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return []
            raise

    def get_teams(self, org: str) -> List[Dict]:
        """Obtém times da organização"""
        print(f"👨‍👩‍👧‍👦 Buscando times de {org}...")
        try:
            return self._get_all_pages(f"/orgs/{org}/teams")
        except requests.exceptions.HTTPError:
            return []

    def get_branch_protection(self, org: str, repo: str, branch: str) -> Dict:
        """Obtém configurações de branch protection"""
        try:
            return self._get(f"/repos/{org}/{repo}/branches/{branch}/protection")
        except requests.exceptions.HTTPError:
            return None

    def audit_repositories(self, org: str) -> Dict:
        """Audita repositórios"""
        repos = self.get_repositories(org)

        public_repos = [r for r in repos if not r['private']]
        inactive_repos = []
        repos_without_description = [r for r in repos if not r['description']]
        repos_without_license = [r for r in repos if not r.get('license')]

        # Verificar repos inativos (>6 meses)
        six_months_ago = datetime.now() - timedelta(days=180)
        for repo in repos:
            if repo['pushed_at']:
                last_push = datetime.strptime(repo['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")
                if last_push < six_months_ago:
                    inactive_repos.append(repo)

        return {
            "total_repositories": len(repos),
            "public_repositories": len(public_repos),
            "private_repositories": len(repos) - len(public_repos),
            "inactive_repositories": len(inactive_repos),
            "repos_without_description": len(repos_without_description),
            "repos_without_license": len(repos_without_license),
            "repositories": repos,
            "public_repos_list": public_repos,
            "inactive_repos_list": inactive_repos,
            "repos_without_description_list": repos_without_description,
            "repos_without_license_list": repos_without_license
        }

    def audit_branch_protection(self, org: str, repos: List[Dict]) -> Dict:
        """Audita branch protection"""
        print(f"🛡️  Auditando branch protection...")

        protected_repos = []
        unprotected_repos = []

        for repo in repos[:50]:  # Limitar para não fazer muitas requisições
            default_branch = repo['default_branch']
            protection = self.get_branch_protection(org, repo['name'], default_branch)

            if protection:
                protected_repos.append({
                    "name": repo['name'],
                    "branch": default_branch,
                    "protection": protection
                })
            else:
                unprotected_repos.append({
                    "name": repo['name'],
                    "branch": default_branch
                })

        return {
            "total_checked": len(repos[:50]),
            "protected_repos": len(protected_repos),
            "unprotected_repos": len(unprotected_repos),
            "protected_repos_list": protected_repos,
            "unprotected_repos_list": unprotected_repos
        }

    def audit_users_and_permissions(self, org: str) -> Dict:
        """Audita usuários e permissões"""
        members = self.get_organization_members(org)
        outside_collaborators = self.get_outside_collaborators(org)
        teams = self.get_teams(org)

        # Obter detalhes de cada membro
        members_details = []
        members_without_2fa = []

        for member in members[:50]:  # Limitar para não fazer muitas requisições
            try:
                user_detail = self._get(f"/users/{member['login']}")
                members_details.append(user_detail)

                # Verificar 2FA (requer permissões admin)
                try:
                    org_membership = self._get(f"/orgs/{org}/memberships/{member['login']}")
                    if org_membership.get('two_factor_requirement_enabled') == False:
                        members_without_2fa.append(member)
                except:
                    pass
            except:
                pass

        return {
            "total_members": len(members),
            "outside_collaborators": len(outside_collaborators),
            "total_teams": len(teams),
            "members_without_2fa": len(members_without_2fa),
            "members_list": members,
            "members_details": members_details,
            "outside_collaborators_list": outside_collaborators,
            "teams_list": teams,
            "members_without_2fa_list": members_without_2fa
        }

    def audit_security_settings(self, org: str, repos: List[Dict]) -> Dict:
        """Audita configurações de segurança"""
        print(f"🔒 Auditando configurações de segurança...")

        repos_with_secret_scanning = []
        repos_without_secret_scanning = []
        repos_with_dependabot = []
        repos_without_dependabot = []

        for repo in repos[:50]:  # Limitar para não fazer muitas requisições
            # Verificar se tem secret scanning e dependabot habilitados
            # (essas informações estão nos detalhes do repo)
            if repo.get('security_and_analysis'):
                secret_scanning = repo['security_and_analysis'].get('secret_scanning', {})
                if secret_scanning.get('status') == 'enabled':
                    repos_with_secret_scanning.append(repo['name'])
                else:
                    repos_without_secret_scanning.append(repo['name'])

                dependabot = repo['security_and_analysis'].get('dependabot_security_updates', {})
                if dependabot.get('status') == 'enabled':
                    repos_with_dependabot.append(repo['name'])
                else:
                    repos_without_dependabot.append(repo['name'])

        return {
            "total_checked": len(repos[:50]),
            "repos_with_secret_scanning": len(repos_with_secret_scanning),
            "repos_without_secret_scanning": len(repos_without_secret_scanning),
            "repos_with_dependabot": len(repos_with_dependabot),
            "repos_without_dependabot": len(repos_without_dependabot),
            "repos_with_secret_scanning_list": repos_with_secret_scanning,
            "repos_without_secret_scanning_list": repos_without_secret_scanning,
            "repos_with_dependabot_list": repos_with_dependabot,
            "repos_without_dependabot_list": repos_without_dependabot
        }

    def run_full_audit(self, org: str = None) -> Dict:
        """Executa auditoria completa"""
        if not org:
            org = self.detect_organization()

        self.org_login = org

        print(f"\n{'='*80}")
        print(f"🔐 AUDITORIA DE SEGURANÇA DA ORGANIZAÇÃO: {org}")
        print(f"{'='*80}\n")

        # Obter informações da organização
        try:
            org_info = self.get_organization(org)
            print(f"✅ Organização: {org_info['name']} ({org_info['login']})")
        except:
            org_info = {"login": org, "name": org}
            print(f"✅ Usando owner: {org}")

        # Executar auditorias
        results = {
            "scan_timestamp": datetime.now().isoformat(),
            "organization": org_info,
            "results": {}
        }

        # 1. Auditoria de Repositórios
        print(f"\n{'='*80}")
        print("📦 AUDITANDO REPOSITÓRIOS")
        print(f"{'='*80}\n")
        repos_audit = self.audit_repositories(org)
        results["results"]["repositories"] = repos_audit

        # 2. Auditoria de Branch Protection
        print(f"\n{'='*80}")
        print("🛡️  AUDITANDO BRANCH PROTECTION")
        print(f"{'='*80}\n")
        branch_audit = self.audit_branch_protection(org, repos_audit["repositories"])
        results["results"]["branch_protection"] = branch_audit

        # 3. Auditoria de Usuários e Permissões
        print(f"\n{'='*80}")
        print("👥 AUDITANDO USUÁRIOS E PERMISSÕES")
        print(f"{'='*80}\n")
        users_audit = self.audit_users_and_permissions(org)
        results["results"]["users_permissions"] = users_audit

        # 4. Auditoria de Segurança
        print(f"\n{'='*80}")
        print("🔒 AUDITANDO CONFIGURAÇÕES DE SEGURANÇA")
        print(f"{'='*80}\n")
        security_audit = self.audit_security_settings(org, repos_audit["repositories"])
        results["results"]["security_settings"] = security_audit

        return results


def convert_to_steampipe_format(data: Dict) -> Dict:
    """
    Converte dados do formato nativo para formato compatível com Steampipe
    para manter compatibilidade com dashboard existente
    """
    converted = {
        "scan_timestamp": data.get("scan_timestamp"),
        "organization": data.get("organization"),
        "results": {}
    }

    for category, category_data in data.get("results", {}).items():
        if not isinstance(category_data, dict):
            converted["results"][category] = {"rows": []}
            continue

        # Mapear categorias para suas listas de dados
        rows_data = []

        if category == "repositories":
            rows_data = category_data.get("repositories", [])
        elif category == "branch_protection":
            # Combinar listas protegidas e não protegidas
            protected = category_data.get("protected_repos_list", [])
            unprotected = category_data.get("unprotected_repos_list", [])
            rows_data = protected + unprotected
        elif category == "users_permissions":
            rows_data = category_data.get("members_list", [])
        elif category == "security_settings":
            # Para security settings, usar os repositórios verificados
            rows_data = category_data.get("repos_with_secret_scanning_list", []) + \
                       category_data.get("repos_without_secret_scanning_list", [])
        else:
            # Para categorias desconhecidas, tentar pegar qualquer lista
            for key, value in category_data.items():
                if isinstance(value, list) and len(value) > 0:
                    rows_data = value
                    break

        # Criar estrutura compatível com Steampipe
        converted["results"][category] = {
            "columns": [],  # Dashboard não usa isso realmente
            "rows": rows_data
        }

        # Manter também os dados originais para compatibilidade
        converted["results"][category].update(category_data)

    return converted


def save_results(data: Dict, filename: str = "audit_results"):
    """Salva os resultados em JSON (formato compatível com dashboard)"""
    # Converter para formato compatível com dashboard existente
    compatible_data = convert_to_steampipe_format(data)

    output_file = RESULTS_DIR.parent / f"{filename}_{TIMESTAMP}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(compatible_data, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'='*80}")
    print(f"✅ AUDITORIA CONCLUÍDA!")
    print(f"{'='*80}")
    print(f"📁 Resultados salvos em: {output_file}")
    print(f"{'='*80}\n")

    return output_file


def main():
    """Função principal"""
    if not GITHUB_TOKEN:
        print("❌ ERRO: Token do GitHub não encontrado!")
        print("💡 Configure a variável de ambiente GITHUB_TOKEN ou ORG_SECURITY_TOKEN")
        exit(1)

    print("🔑 Token do GitHub encontrado")

    # Criar auditor
    auditor = GitHubAuditor(GITHUB_TOKEN)

    # Executar auditoria completa
    results = auditor.run_full_audit()

    # Salvar resultados
    save_results(results)

    # Salvar resultados individuais para compatibilidade
    for category, data in results["results"].items():
        category_file = RESULTS_DIR / f"{category}_{TIMESTAMP}.json"
        with open(category_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"📄 {category}: {category_file}")


if __name__ == "__main__":
    main()
