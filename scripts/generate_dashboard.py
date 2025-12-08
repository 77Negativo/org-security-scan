#!/usr/bin/env python3
"""
Script para gerar dashboard HTML com insights de segurança
"""

import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Diretórios
RESULTS_DIR = Path("reports/results")
REPORTS_DIR = Path("reports")

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

def safe_get_data(results: Dict, key: str) -> List:
    """
    Extrai dados de forma segura, lidando com erros
    """
    if not results or "results" not in results:
        return []

    data = results["results"].get(key, {})

    # Se houver erro, retorna lista vazia
    if "error" in data:
        print(f"⚠️  Query '{key}' teve erro: {data.get('stderr', 'Unknown error')[:100]}")
        return []

    # Retorna rows se existir
    if "rows" in data:
        return data["rows"]

    return []

def count_by_field(data: List, field: str, value: Any) -> int:
    """
    Conta quantos itens têm determinado valor em um campo
    """
    if not data:
        return 0

    count = 0
    for item in data:
        if isinstance(item, dict) and item.get(field) == value:
            count += 1
        elif isinstance(item, list) and len(item) > 0:
            try:
                idx = 0
                if item[idx] == value:
                    count += 1
            except:
                pass
    return count

def extract_insights(results: Dict) -> Dict:
    """
    Extrai insights dos dados
    """
    repos = safe_get_data(results, "repositories")
    orgs = safe_get_data(results, "users_permissions")
    branch_protection = safe_get_data(results, "branch_protection")
    dependabot = safe_get_data(results, "dependabot")
    user_perms = safe_get_data(results, "user_permissions")
    collaborators = safe_get_data(results, "repo_collaborators")
    public_repos_security = safe_get_data(results, "public_repos_security")
    members_2fa = safe_get_data(results, "members_2fa_audit")
    security_files_data = results.get("results", {}).get("security_files_check", {})
    inactive_collaborators_data = results.get("results", {}).get("inactive_collaborators_check", {})

    insights = {
        "total_repos": len(repos),
        "total_orgs": len(orgs),
        "public_repos": 0,
        "private_repos": 0,
        "repos_with_protection": 0,
        "repos_without_protection": 0,
        "repos_with_dependabot": 0,
        "repos_without_dependabot": 0,
        "users_without_2fa": 0,
        "total_users": len(user_perms),
        "total_collaborators": len(collaborators),
        "repos_list": [],
        "public_repos_list": [],
        "private_repos_list": [],
        "orgs_list": [],
        "branch_protection_list": [],
        "repos_protected": [],
        "repos_unprotected": [],
        "dependabot_list": [],
        "repos_with_dep_enabled": [],
        "repos_with_dep_disabled": [],
        "user_permissions_list": [],
        "collaborators_list": [],
        # New security insights
        "public_repos_security_list": [],
        "members_2fa_list": [],
        "members_2fa_critical": [],
        "members_2fa_ok": [],
        "admins_without_2fa": 0,
        "repos_without_security_md": [],
        "repos_with_security_md": [],
        "external_collaborators": [],
        "outside_collaborators_count": 0,
        # Inactive collaborators insights
        "inactive_collaborators": [],
        "inactive_high_risk": [],
        "inactive_count": 0,
        "inactive_threshold_days": 90
    }

    # Processar repositórios
    for repo in repos:
        if isinstance(repo, dict):
            repo_data = {
                "name": repo.get("name", "Unknown"),
                "full_name": repo.get("full_name", repo.get("name", "Unknown")),
                "visibility": repo.get("visibility", "unknown"),
                "created_at": repo.get("created_at", ""),
                "updated_at": repo.get("updated_at", ""),
                "has_vulnerability_alerts": repo.get("has_vulnerability_alerts_enabled", False),
                "is_security_policy_enabled": repo.get("is_security_policy_enabled", False),
                "is_archived": repo.get("is_archived", False),
                "default_branch": repo.get("default_branch", "main")
            }

            insights["repos_list"].append(repo_data)

            visibility = repo.get("visibility", "").upper()
            if visibility == "PUBLIC":
                insights["public_repos"] += 1
                insights["public_repos_list"].append(repo_data)
            elif visibility == "PRIVATE":
                insights["private_repos"] += 1
                insights["private_repos_list"].append(repo_data)

    # Processar organizações
    for org in orgs:
        if isinstance(org, dict):
            insights["orgs_list"].append({
                "login": org.get("login", "Unknown"),
                "name": org.get("name", ""),
                "created_at": org.get("created_at", "")
            })

    # Processar branch protection
    for bp in branch_protection:
        if isinstance(bp, dict):
            protected = bp.get("protected", False)
            bp_data = {
                "repository": bp.get("repository", "Unknown"),
                "branch_name": bp.get("branch_name", bp.get("default_branch", "main")),
                "protected": protected,
                "requires_signatures": bp.get("requires_signatures", "false") == "true",
                "allows_deletions": bp.get("allows_deletions", "false") == "true",
                "allows_force_pushes": bp.get("allows_force_pushes", "false") == "true"
            }
            insights["branch_protection_list"].append(bp_data)

            if protected:
                insights["repos_with_protection"] += 1
                insights["repos_protected"].append(bp_data)
            else:
                insights["repos_without_protection"] += 1
                insights["repos_unprotected"].append(bp_data)

    # Processar Dependabot
    for dep in dependabot:
        if isinstance(dep, dict):
            has_alerts = dep.get("has_vulnerability_alerts_enabled", False)
            dep_data = {
                "name": dep.get("name", "Unknown"),
                "full_name": dep.get("full_name", dep.get("name", "Unknown")),
                "visibility": dep.get("visibility", "unknown"),
                "has_vulnerability_alerts": has_alerts,
                "is_security_policy_enabled": dep.get("is_security_policy_enabled", False),
                "is_archived": dep.get("is_archived", False)
            }
            insights["dependabot_list"].append(dep_data)

            if has_alerts:
                insights["repos_with_dependabot"] += 1
                insights["repos_with_dep_enabled"].append(dep_data)
            else:
                insights["repos_without_dependabot"] += 1
                insights["repos_with_dep_disabled"].append(dep_data)

    # Processar permissões de usuários
    for user in user_perms:
        if isinstance(user, dict):
            has_2fa = user.get("has_two_factor_enabled", False)
            user_data = {
                "organization": user.get("organization", "Unknown"),
                "member_login": user.get("member_login", "Unknown"),
                "role": user.get("role", "MEMBER"),
                "has_two_factor_enabled": has_2fa,
                "member_name": user.get("member_name", ""),
                "member_email": user.get("member_email", "")
            }
            insights["user_permissions_list"].append(user_data)

            if not has_2fa:
                insights["users_without_2fa"] += 1

    # Processar colaboradores
    for collab in collaborators:
        if isinstance(collab, dict):
            insights["collaborators_list"].append({
                "repository": collab.get("repository", "Unknown"),
                "visibility": collab.get("visibility", "unknown"),
                "collaborator": collab.get("collaborator", "Unknown"),
                "permission": collab.get("permission", "UNKNOWN"),
                "affiliation": collab.get("affiliation", "UNKNOWN")
            })

            # Identificar colaboradores externos
            if collab.get("affiliation") == "OUTSIDE":
                insights["external_collaborators"].append({
                    "repository": collab.get("repository", "Unknown"),
                    "collaborator": collab.get("collaborator", "Unknown"),
                    "permission": collab.get("permission", "UNKNOWN"),
                    "visibility": collab.get("visibility", "unknown")
                })
                insights["outside_collaborators_count"] += 1

    # Processar repositórios públicos com foco em segurança
    for pub_repo in public_repos_security:
        if isinstance(pub_repo, dict):
            insights["public_repos_security_list"].append({
                "name": pub_repo.get("name", "Unknown"),
                "full_name": pub_repo.get("full_name", "Unknown"),
                "visibility": pub_repo.get("visibility", "PUBLIC"),
                "security_priority": pub_repo.get("security_priority", "LOW"),
                "updated_at": pub_repo.get("updated_at", "")
            })

    # Processar auditoria de 2FA dos membros
    for member in members_2fa:
        if isinstance(member, dict):
            risk_level = member.get("security_risk_level", "OK")
            has_2fa = member.get("two_factor_enabled", member.get("has_two_factor_enabled", False))
            role = member.get("role", "MEMBER")

            member_data = {
                "organization": member.get("organization", "Unknown"),
                "member_login": member.get("member_login", "Unknown"),
                "role": role,
                "has_two_factor_enabled": has_2fa,
                "security_risk_level": risk_level
            }

            insights["members_2fa_list"].append(member_data)

            if risk_level in ["CRITICAL", "HIGH"]:
                insights["members_2fa_critical"].append(member_data)
                if role == "ADMIN":
                    insights["admins_without_2fa"] += 1
            else:
                insights["members_2fa_ok"].append(member_data)

    # Processar dados de arquivos de segurança (SECURITY.md)
    if security_files_data:
        insights["repos_without_security_md"] = security_files_data.get("repos_without_security", [])
        insights["repos_with_security_md"] = security_files_data.get("repos_with_security", [])

    # Processar dados de colaboradores inativos
    if inactive_collaborators_data:
        insights["inactive_collaborators"] = inactive_collaborators_data.get("inactive_collaborators", [])
        insights["inactive_count"] = inactive_collaborators_data.get("inactive_count", 0)
        insights["inactive_threshold_days"] = inactive_collaborators_data.get("threshold_days", 90)

        # Separar colaboradores de alto risco (com permissão ADMIN)
        for collab in insights["inactive_collaborators"]:
            if collab.get("risk_level") == "HIGH":
                insights["inactive_high_risk"].append(collab)

    return insights

def generate_html_dashboard(results: Dict) -> str:
    """
    Gera dashboard HTML com os resultados
    """
    timestamp = results.get("scan_timestamp", datetime.now().isoformat())
    insights = extract_insights(results)

    has_data = insights["total_repos"] > 0 or insights["total_orgs"] > 0

    # CSS e HTML Header
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Segurança - GitHub Organization</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        .header h1 {{
            color: #2d3748;
            font-size: 32px;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            color: #718096;
            font-size: 16px;
        }}

        .header .timestamp {{
            color: #a0aec0;
            font-size: 14px;
            margin-top: 10px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-card .icon {{
            font-size: 40px;
            margin-bottom: 15px;
        }}

        .stat-card .value {{
            font-size: 36px;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 5px;
        }}

        .stat-card .label {{
            color: #718096;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .stat-card .detail {{
            color: #4a5568;
            font-size: 12px;
            margin-top: 10px;
        }}

        .stat-card.warning {{
            border-left: 4px solid #f59e0b;
        }}

        .stat-card.danger {{
            border-left: 4px solid #ef4444;
        }}

        .stat-card.success {{
            border-left: 4px solid #10b981;
        }}

        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        .section h2 {{
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 24px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }}

        .section h3 {{
            color: #4a5568;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            overflow-x: auto;
        }}

        .data-table th {{
            background: #edf2f7;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #2d3748;
            border-bottom: 2px solid #cbd5e0;
        }}

        .data-table td {{
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            color: #4a5568;
        }}

        .data-table tr:hover {{
            background: #f7fafc;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}

        .badge.public {{
            background: #fed7d7;
            color: #742a2a;
        }}

        .badge.private {{
            background: #c6f6d5;
            color: #22543d;
        }}

        .badge.protected {{
            background: #bee3f8;
            color: #2c5282;
        }}

        .badge.unprotected {{
            background: #feebc8;
            color: #7c2d12;
        }}

        .badge.enabled {{
            background: #c6f6d5;
            color: #22543d;
        }}

        .badge.disabled {{
            background: #fed7d7;
            color: #742a2a;
        }}

        .badge.admin {{
            background: #e9d5ff;
            color: #581c87;
        }}

        .badge.member {{
            background: #dbeafe;
            color: #1e3a8a;
        }}

        .badge.outside {{
            background: #fef3c7;
            color: #78350f;
        }}

        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }}

        .no-data {{
            text-align: center;
            padding: 60px 20px;
            color: #718096;
        }}

        .no-data .icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}

        .alert {{
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}

        .alert.warning {{
            background: #fef3c7;
            color: #78350f;
            border-left: 4px solid #f59e0b;
        }}

        .alert.info {{
            background: #dbeafe;
            color: #1e3a8a;
            border-left: 4px solid #3b82f6;
        }}

        .alert.danger {{
            background: #fee2e2;
            color: #7f1d1d;
            border-left: 4px solid #ef4444;
        }}

        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .data-table {{
                font-size: 14px;
            }}

            .data-table th, .data-table td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Dashboard de Segurança da Organização</h1>
            <div class="subtitle">Auditoria Contínua de Segurança - GitHub Organization</div>
            <div class="timestamp">Última atualização: {timestamp}</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📦</div>
                <div class="value">{insights["total_repos"]}</div>
                <div class="label">Repositórios</div>
                <div class="detail">
                    {insights["public_repos"]} públicos • {insights["private_repos"]} privados
                </div>
            </div>

            <div class="stat-card">
                <div class="icon">🏢</div>
                <div class="value">{insights["total_orgs"]}</div>
                <div class="label">Organizações</div>
                <div class="detail">Detectadas via token</div>
            </div>

            <div class="stat-card {'warning' if insights['repos_without_protection'] > 0 else 'success'}">
                <div class="icon">🛡️</div>
                <div class="value">{insights["repos_with_protection"]}/{insights["total_repos"]}</div>
                <div class="label">Branch Protection</div>
                <div class="detail">
                    {insights["repos_without_protection"]} sem proteção
                </div>
            </div>

            <div class="stat-card {'warning' if insights['repos_without_dependabot'] > 0 else 'success'}">
                <div class="icon">🤖</div>
                <div class="value">{insights["repos_with_dependabot"]}/{insights["total_repos"]}</div>
                <div class="label">Dependabot</div>
                <div class="detail">
                    {insights["repos_without_dependabot"]} sem alertas
                </div>
            </div>

            <div class="stat-card {'danger' if insights['users_without_2fa'] > 0 else 'success'}">
                <div class="icon">🔐</div>
                <div class="value">{insights["total_users"] - insights["users_without_2fa"]}/{insights["total_users"]}</div>
                <div class="label">2FA Habilitado</div>
                <div class="detail">
                    {insights["users_without_2fa"]} sem 2FA
                </div>
            </div>

            <div class="stat-card">
                <div class="icon">👥</div>
                <div class="value">{insights["total_collaborators"]}</div>
                <div class="label">Colaboradores</div>
                <div class="detail">Total em repos</div>
            </div>
        </div>
"""

    if has_data:
        # Alertas importantes
        if insights["repos_without_protection"] > 0 or insights["users_without_2fa"] > 0:
            html += """
        <div class="section">
            <h2>⚠️ Alertas de Segurança</h2>
"""
            if insights["repos_without_protection"] > 0:
                html += f"""
            <div class="alert danger">
                <strong>Branch Protection Ausente:</strong> {insights["repos_without_protection"]} repositório(s) sem proteção no branch principal.
            </div>
"""
            if insights["users_without_2fa"] > 0:
                html += f"""
            <div class="alert danger">
                <strong>2FA Desabilitado:</strong> {insights["users_without_2fa"]} usuário(s) sem autenticação de dois fatores habilitada.
            </div>
"""
            if insights["repos_without_dependabot"] > 0:
                html += f"""
            <div class="alert warning">
                <strong>Dependabot Desabilitado:</strong> {insights["repos_without_dependabot"]} repositório(s) sem alertas de vulnerabilidade habilitados.
            </div>
"""
            html += """
        </div>
"""

        # Nova Seção: Compliance de 2FA - CRÍTICO
        if insights["members_2fa_critical"]:
            html += f"""
        <div class="section">
            <h2>🔐 Compliance de 2FA - AÇÃO NECESSÁRIA</h2>

            <div class="alert danger">
                <strong>CRÍTICO:</strong> {len(insights["members_2fa_critical"])} membro(s) sem 2FA habilitado!
                {f"Incluindo {insights['admins_without_2fa']} administrador(es)!" if insights["admins_without_2fa"] > 0 else ""}
            </div>

            <table class="data-table">
                <thead>
                    <tr>
                        <th>Usuário</th>
                        <th>Organização</th>
                        <th>Role</th>
                        <th>Status 2FA</th>
                        <th>Nível de Risco</th>
                        <th>Ação Recomendada</th>
                    </tr>
                </thead>
                <tbody>
"""
            for member in insights["members_2fa_critical"][:20]:
                role_class = "admin" if member["role"] == "ADMIN" else "member"
                risk_class = "danger" if member["security_risk_level"] == "CRITICAL" else "warning"

                html += f"""
                    <tr>
                        <td><strong>{member["member_login"]}</strong></td>
                        <td>{member["organization"]}</td>
                        <td><span class="badge {role_class}">{member["role"]}</span></td>
                        <td><span class="badge disabled">SEM 2FA</span></td>
                        <td><span class="badge {risk_class}">{member["security_risk_level"]}</span></td>
                        <td>Exigir 2FA imediatamente</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
"""

        # Nova Seção: Arquivos de Segurança Ausentes
        if insights["repos_without_security_md"]:
            html += f"""
        <div class="section">
            <h2>📋 Repositórios SEM Arquivos de Segurança</h2>

            <div class="alert warning">
                <strong>Atenção:</strong> {len(insights["repos_without_security_md"])} repositório(s) não possuem SECURITY.md ou CODE_OF_CONDUCT.md
            </div>

            <p style="margin-bottom: 15px; color: #4a5568;">
                Arquivos de segurança são essenciais para comunicar políticas de divulgação responsável e práticas de segurança.
            </p>

            <table class="data-table">
                <thead>
                    <tr>
                        <th>Repositório</th>
                        <th>Visibilidade</th>
                        <th>Arquivos Ausentes</th>
                        <th>Ação Recomendada</th>
                    </tr>
                </thead>
                <tbody>
"""
            for repo in insights["repos_without_security_md"][:30]:
                vis_class = repo.get("visibility", "unknown").lower()
                missing = ", ".join(repo.get("missing_files", ["SECURITY.md"]))[:50]

                html += f"""
                    <tr>
                        <td><strong>{repo.get("name", "Unknown")}</strong></td>
                        <td><span class="badge {vis_class}">{repo.get("visibility", "UNKNOWN").upper()}</span></td>
                        <td>{missing}</td>
                        <td>Criar SECURITY.md na raiz ou .github/</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>

            <div style="margin-top: 20px; padding: 15px; background: #f7fafc; border-left: 4px solid #3b82f6; border-radius: 4px;">
                <strong>Template Recomendado:</strong>
                <pre style="margin-top: 10px; background: white; padding: 10px; border-radius: 4px; overflow-x: auto;">
# Security Policy

## Reporting a Vulnerability

Para reportar vulnerabilidades de segurança, envie um email para security@example.com

Responderemos em até 48 horas e manteremos você informado sobre o progresso.</pre>
            </div>
        </div>
"""

        # Nova Seção: Colaboradores Externos
        if insights["external_collaborators"]:
            html += f"""
        <div class="section">
            <h2>👥 Colaboradores Externos - Auditoria Necessária</h2>

            <div class="alert warning">
                <strong>Atenção:</strong> {insights["outside_collaborators_count"]} colaborador(es) externo(s) com acesso aos repositórios
            </div>

            <p style="margin-bottom: 15px; color: #4a5568;">
                Colaboradores externos (OUTSIDE) não são membros da organização mas têm acesso direto aos repositórios.
                Revise periodicamente essas permissões.
            </p>

            <table class="data-table">
                <thead>
                    <tr>
                        <th>Colaborador</th>
                        <th>Repositório</th>
                        <th>Permissão</th>
                        <th>Visibilidade do Repo</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
            for collab in insights["external_collaborators"][:50]:
                perm_class = "admin" if collab["permission"] == "ADMIN" else "member"
                vis_class = collab.get("visibility", "unknown").lower()

                html += f"""
                    <tr>
                        <td><strong>{collab["collaborator"]}</strong></td>
                        <td>{collab["repository"]}</td>
                        <td><span class="badge {perm_class}">{collab["permission"]}</span></td>
                        <td><span class="badge {vis_class}">{collab.get("visibility", "UNKNOWN").upper()}</span></td>
                        <td><span class="badge outside">EXTERNAL</span></td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
"""

        # Nova Seção: Colaboradores Inativos
        if insights["inactive_collaborators"]:
            html += f"""
        <div class="section">
            <h2>⏰ Colaboradores Inativos - Revisão Recomendada</h2>

            <div class="alert warning">
                <strong>Atenção:</strong> {insights["inactive_count"]} colaborador(es) sem atividade por mais de {insights["inactive_threshold_days"]} dias
            </div>

            <p style="margin-bottom: 15px; color: #4a5568;">
                Colaboradores sem contribuições recentes podem representar um risco de segurança.
                Considere revisar e remover acessos desnecessários.
            </p>

            <table class="data-table">
                <thead>
                    <tr>
                        <th>Colaborador</th>
                        <th>Repositório</th>
                        <th>Última Atividade</th>
                        <th>Dias Inativo</th>
                        <th>Permissões</th>
                        <th>Nível de Risco</th>
                        <th>Ação Recomendada</th>
                    </tr>
                </thead>
                <tbody>
"""
            # Ordenar por risco (HIGH primeiro) e depois por dias inativos
            sorted_inactive = sorted(
                insights["inactive_collaborators"],
                key=lambda x: (0 if x.get("risk_level") == "HIGH" else 1,
                              0 if x.get("inactive_days") == "∞" else int(x.get("inactive_days", 0))),
                reverse=True
            )

            for collab in sorted_inactive[:50]:
                username = collab.get("username", "Unknown")
                repo = collab.get("repository", "Unknown")
                last_activity = collab.get("last_activity", "Nunca")
                inactive_days = collab.get("inactive_days", "∞")
                permissions = collab.get("permissions", {})
                risk_level = collab.get("risk_level", "MEDIUM")
                status = collab.get("status", "Inativo")

                # Determinar classe CSS baseada no risco
                risk_class = "danger" if risk_level == "HIGH" else "warning"

                # Formatar permissões
                perm_list = []
                if permissions.get("admin"):
                    perm_list.append("ADMIN")
                if permissions.get("push"):
                    perm_list.append("WRITE")
                if permissions.get("pull"):
                    perm_list.append("READ")
                perm_str = ", ".join(perm_list) if perm_list else "UNKNOWN"

                # Ação recomendada
                if risk_level == "HIGH":
                    action = "⚠️ Revisar e remover acesso ADMIN imediatamente"
                elif inactive_days == "∞":
                    action = "Remover acesso (nunca contribuiu)"
                else:
                    action = "Verificar necessidade de acesso"

                html += f"""
                    <tr>
                        <td><strong>{username}</strong></td>
                        <td>{repo}</td>
                        <td>{last_activity}</td>
                        <td><span class="badge {risk_class}">{inactive_days} dias</span></td>
                        <td><span class="badge member">{perm_str}</span></td>
                        <td><span class="badge {risk_class}">{risk_level}</span></td>
                        <td style="font-size: 0.9em; color: #4a5568;">{action}</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>

            <div style="margin-top: 20px; padding: 15px; background-color: #f7fafc; border-left: 4px solid #4299e1; border-radius: 4px;">
                <strong style="color: #2c5282;">📝 Ações Recomendadas:</strong>
                <ul style="margin-top: 10px; margin-left: 20px; color: #4a5568;">
                    <li>Revisar colaboradores de <strong>ALTO RISCO</strong> (com permissão ADMIN) imediatamente</li>
                    <li>Contatar colaboradores inativos para verificar se ainda precisam de acesso</li>
                    <li>Remover acessos de colaboradores que nunca contribuíram (∞ dias)</li>
                    <li>Estabelecer política de revisão trimestral de acessos</li>
                </ul>
            </div>
        </div>
"""

        # Nova Seção: Revisão de Segurança de Repositórios Públicos
        if insights["public_repos_security_list"]:
            html += f"""
        <div class="section">
            <h2>🌍 Repositórios Públicos - Revisão de Segurança</h2>

            <div class="alert info">
                <strong>Info:</strong> {len(insights["public_repos_security_list"])} repositório(s) público(s) requerem revisão de configurações de segurança
            </div>

            <p style="margin-bottom: 15px; color: #4a5568;">
                Repositórios públicos têm maior exposição e requerem atenção especial em:
                • Branch protection • Secret scanning • Dependabot • Code scanning
            </p>

            <table class="data-table">
                <thead>
                    <tr>
                        <th>Repositório</th>
                        <th>Prioridade</th>
                        <th>Última Atualização</th>
                        <th>Itens para Verificar</th>
                    </tr>
                </thead>
                <tbody>
"""
            for repo in insights["public_repos_security_list"][:30]:
                priority = repo.get("security_priority", "LOW")
                priority_class = "danger" if priority == "CRITICAL" else "warning"
                updated = repo["updated_at"][:10] if repo.get("updated_at") else "N/A"

                html += f"""
                    <tr>
                        <td><strong>{repo["name"]}</strong></td>
                        <td><span class="badge {priority_class}">{priority}</span></td>
                        <td>{updated}</td>
                        <td>
                            <ul style="margin: 0; padding-left: 20px; font-size: 12px;">
                                <li>Branch protection rules</li>
                                <li>Secret scanning enabled</li>
                                <li>Dependabot alerts active</li>
                                <li>SECURITY.md presente</li>
                            </ul>
                        </td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
"""

        # Seção de Repositórios Públicos (original)
        if insights["public_repos_list"]:
            html += """
        <div class="section">
            <h2>🌍 Repositórios Públicos</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Visibilidade</th>
                        <th>Dependabot</th>
                        <th>Security Policy</th>
                        <th>Última Atualização</th>
                    </tr>
                </thead>
                <tbody>
"""
            for repo in insights["public_repos_list"][:50]:
                dep_badge = "enabled" if repo.get("has_vulnerability_alerts") else "disabled"
                dep_text = "✓" if repo.get("has_vulnerability_alerts") else "✗"
                sec_policy = "✓" if repo.get("is_security_policy_enabled") else "✗"
                updated = repo["updated_at"][:10] if repo["updated_at"] else "N/A"

                html += f"""
                    <tr>
                        <td><strong>{repo["name"]}</strong></td>
                        <td><span class="badge public">PUBLIC</span></td>
                        <td><span class="badge {dep_badge}">{dep_text}</span></td>
                        <td>{sec_policy}</td>
                        <td>{updated}</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
"""

        # Seção de Repositórios Privados
        if insights["private_repos_list"]:
            html += """
        <div class="section">
            <h2>🔒 Repositórios Privados</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Visibilidade</th>
                        <th>Dependabot</th>
                        <th>Security Policy</th>
                        <th>Última Atualização</th>
                    </tr>
                </thead>
                <tbody>
"""
            for repo in insights["private_repos_list"][:50]:
                dep_badge = "enabled" if repo.get("has_vulnerability_alerts") else "disabled"
                dep_text = "✓" if repo.get("has_vulnerability_alerts") else "✗"
                sec_policy = "✓" if repo.get("is_security_policy_enabled") else "✗"
                updated = repo["updated_at"][:10] if repo["updated_at"] else "N/A"

                html += f"""
                    <tr>
                        <td><strong>{repo["name"]}</strong></td>
                        <td><span class="badge private">PRIVATE</span></td>
                        <td><span class="badge {dep_badge}">{dep_text}</span></td>
                        <td>{sec_policy}</td>
                        <td>{updated}</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
"""

        # Seção de Branch Protection
        if insights["branch_protection_list"]:
            html += """
        <div class="section">
            <h2>🛡️ Status de Branch Protection</h2>

            <h3>✅ Repositórios COM proteção</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Repositório</th>
                        <th>Branch</th>
                        <th>Status</th>
                        <th>Assinaturas</th>
                        <th>Permite Deleção</th>
                        <th>Permite Force Push</th>
                    </tr>
                </thead>
                <tbody>
"""
            for bp in insights["repos_protected"][:30]:
                html += f"""
                    <tr>
                        <td><strong>{bp["repository"]}</strong></td>
                        <td>{bp["branch_name"]}</td>
                        <td><span class="badge protected">PROTEGIDO</span></td>
                        <td>{'✓' if bp.get('requires_signatures') else '✗'}</td>
                        <td>{'⚠️' if bp.get('allows_deletions') else '✓'}</td>
                        <td>{'⚠️' if bp.get('allows_force_pushes') else '✓'}</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>

            <h3>❌ Repositórios SEM proteção</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Repositório</th>
                        <th>Branch</th>
                        <th>Status</th>
                        <th>Ação Recomendada</th>
                    </tr>
                </thead>
                <tbody>
"""
            for bp in insights["repos_unprotected"][:30]:
                html += f"""
                    <tr>
                        <td><strong>{bp["repository"]}</strong></td>
                        <td>{bp["branch_name"]}</td>
                        <td><span class="badge unprotected">SEM PROTEÇÃO</span></td>
                        <td>Configurar branch protection rules</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
"""

        # Seção de Dependabot
        if insights["dependabot_list"]:
            html += f"""
        <div class="section">
            <h2>🤖 Status de Dependabot e Alertas de Vulnerabilidade</h2>

            <div class="alert info">
                <strong>Resumo:</strong> {insights["repos_with_dependabot"]} repositórios com alertas habilitados,
                {insights["repos_without_dependabot"]} sem alertas.
            </div>

            <h3>✅ Repositórios COM Dependabot habilitado</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Visibilidade</th>
                        <th>Alertas</th>
                        <th>Security Policy</th>
                    </tr>
                </thead>
                <tbody>
"""
            for dep in insights["repos_with_dep_enabled"][:30]:
                vis_class = dep["visibility"].lower()
                sec_policy = "✓" if dep.get("is_security_policy_enabled") else "✗"

                html += f"""
                    <tr>
                        <td><strong>{dep["name"]}</strong></td>
                        <td><span class="badge {vis_class}">{dep["visibility"].upper()}</span></td>
                        <td><span class="badge enabled">HABILITADO</span></td>
                        <td>{sec_policy}</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>

            <h3>❌ Repositórios SEM Dependabot habilitado</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Visibilidade</th>
                        <th>Alertas</th>
                        <th>Ação Recomendada</th>
                    </tr>
                </thead>
                <tbody>
"""
            for dep in insights["repos_with_dep_disabled"][:30]:
                vis_class = dep["visibility"].lower()
                archived = " (arquivado)" if dep.get("is_archived") else ""

                html += f"""
                    <tr>
                        <td><strong>{dep["name"]}</strong>{archived}</td>
                        <td><span class="badge {vis_class}">{dep["visibility"].upper()}</span></td>
                        <td><span class="badge disabled">DESABILITADO</span></td>
                        <td>Habilitar vulnerability alerts nas configurações</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
"""

        # Seção de Permissões de Usuários
        if insights["user_permissions_list"]:
            html += f"""
        <div class="section">
            <h2>👥 Auditoria de Permissões de Usuários</h2>

            {f'<div class="alert danger"><strong>Atenção:</strong> {insights["users_without_2fa"]} usuário(s) sem 2FA habilitado!</div>' if insights["users_without_2fa"] > 0 else ''}

            <table class="data-table">
                <thead>
                    <tr>
                        <th>Usuário</th>
                        <th>Nome</th>
                        <th>Organização</th>
                        <th>Role</th>
                        <th>2FA</th>
                        <th>Email</th>
                    </tr>
                </thead>
                <tbody>
"""
            for user in insights["user_permissions_list"][:100]:
                role_class = "admin" if user["role"] == "ADMIN" else "member"
                tfa_badge = "enabled" if user.get("has_two_factor_enabled") else "disabled"
                tfa_text = "✓" if user.get("has_two_factor_enabled") else "✗"

                html += f"""
                    <tr>
                        <td><strong>{user["member_login"]}</strong></td>
                        <td>{user.get("member_name") or "—"}</td>
                        <td>{user["organization"]}</td>
                        <td><span class="badge {role_class}">{user["role"]}</span></td>
                        <td><span class="badge {tfa_badge}">{tfa_text}</span></td>
                        <td>{user.get("member_email") or "—"}</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
"""

        # Seção de Colaboradores de Repositórios
        if insights["collaborators_list"]:
            html += """
        <div class="section">
            <h2>🤝 Auditoria de Permissões de Repositórios</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Repositório</th>
                        <th>Colaborador</th>
                        <th>Permissão</th>
                        <th>Afiliação</th>
                        <th>Visibilidade do Repo</th>
                    </tr>
                </thead>
                <tbody>
"""
            for collab in insights["collaborators_list"][:100]:
                perm_class = "admin" if collab["permission"] == "ADMIN" else "member"
                affil_class = "outside" if collab["affiliation"] == "OUTSIDE" else "member"
                vis_class = collab["visibility"].lower()

                html += f"""
                    <tr>
                        <td><strong>{collab["repository"]}</strong></td>
                        <td>{collab["collaborator"]}</td>
                        <td><span class="badge {perm_class}">{collab["permission"]}</span></td>
                        <td><span class="badge {affil_class}">{collab["affiliation"]}</span></td>
                        <td><span class="badge {vis_class}">{collab["visibility"].upper()}</span></td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
"""

        # Seção de Organizações
        if insights["orgs_list"]:
            html += """
        <div class="section">
            <h2>🏢 Organizações Acessíveis</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Login</th>
                        <th>Nome</th>
                        <th>Criado Em</th>
                    </tr>
                </thead>
                <tbody>
"""
            for org in insights["orgs_list"]:
                created = org["created_at"][:10] if org["created_at"] else "N/A"

                html += f"""
                    <tr>
                        <td><strong>{org["login"]}</strong></td>
                        <td>{org["name"] or "—"}</td>
                        <td>{created}</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
"""

    else:
        # Sem dados
        html += """
        <div class="section">
            <div class="no-data">
                <div class="icon">🔍</div>
                <h2>Nenhum Dado Coletado</h2>
                <p>Verifique se o token <code>ORG_SECURITY_TOKEN</code> está configurado corretamente.</p>
                <p style="margin-top: 10px;">O token precisa ter permissões: <code>repo</code>, <code>admin:org:read</code>, <code>read:user</code></p>
            </div>
        </div>
"""

    html += """
        <div class="section">
            <h2>📝 Próximos Passos Recomendados</h2>
            <ul style="color: #4a5568; line-height: 2;">
                <li>🔐 Revisar repositórios públicos e suas configurações de segurança</li>
                <li>🛡️ Configurar branch protection em todos os repositórios principais</li>
                <li>🤖 Habilitar Dependabot em repositórios sem alertas de vulnerabilidade</li>
                <li>🔑 Exigir 2FA para todos os membros da organização</li>
                <li>👥 Auditar permissões de colaboradores externos</li>
                <li>📋 Criar ou atualizar SECURITY.md em todos os repositórios</li>
                <li>🔍 Revisar e remover colaboradores inativos</li>
            </ul>
        </div>

        <div class="footer">
            <p>Gerado automaticamente pelo org-security-scan</p>
            <p style="margin-top: 10px; opacity: 0.8;">Powered by Steampipe + GitHub Actions</p>
        </div>
    </div>
</body>
</html>
"""

    return html

def main():
    """
    Função principal
    """
    print("\n" + "="*80)
    print("📊 GERANDO DASHBOARD DE SEGURANÇA")
    print("="*80 + "\n")

    # Carregar resultados
    results = load_latest_results()

    if not results:
        print("❌ Nenhum resultado para processar!")
        return

    # Gerar HTML
    html_content = generate_html_dashboard(results)

    # Salvar dashboard
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dashboard_file = REPORTS_DIR / f"security_dashboard_{timestamp}.html"

    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Criar link simbólico para o mais recente
    latest_link = REPORTS_DIR / "security_dashboard_latest.html"
    if latest_link.exists():
        latest_link.unlink()
    latest_link.write_text(html_content)

    print(f"✅ Dashboard gerado: {dashboard_file}")
    print(f"🔗 Link para o último: {latest_link}")
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
