#!/usr/bin/env python3
"""
Script para executar queries de auditoria de segurança usando Steampipe
"""

import subprocess
import json
import csv
import os
from datetime import datetime
from pathlib import Path

# Diretórios
QUERIES_DIR = Path("steampipe/queries")
RESULTS_DIR = Path("reports/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Timestamp para os arquivos
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

def run_query(query_file: Path, output_format: str = "json") -> dict:
    """
    Executa uma query SQL do Steampipe e retorna os resultados
    """
    print(f"📋 Executando: {query_file.name}")

    try:
        # Executar query
        result = subprocess.run(
            ["steampipe", "query", str(query_file), "--output", output_format],
            capture_output=True,
            text=True,
            check=True
        )

        if output_format == "json":
            return json.loads(result.stdout)
        else:
            return {"output": result.stdout}

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar {query_file.name}: {e}")
        print(f"STDERR: {e.stderr}")
        return {"error": str(e), "stderr": e.stderr}
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao fazer parse do JSON: {e}")
        return {"error": "JSON parse error", "output": result.stdout}

def save_results(data: dict, filename: str):
    """
    Salva os resultados em formato JSON
    """
    output_file = RESULTS_DIR / f"{filename}_{TIMESTAMP}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print(f"✅ Resultados salvos em: {output_file}")
    return output_file

def save_csv(data: dict, filename: str):
    """
    Salva os resultados em formato CSV
    """
    if "rows" not in data or not data["rows"]:
        print(f"⚠️  Sem dados para salvar em CSV: {filename}")
        return None

    output_file = RESULTS_DIR / f"{filename}_{TIMESTAMP}.csv"

    # Extrair colunas
    columns = [col["name"] for col in data.get("columns", [])]
    rows = data.get("rows", [])

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)

        for row in rows:
            writer.writerow(row)

    print(f"📊 CSV salvo em: {output_file}")
    return output_file

def execute_query_file(query_file: Path) -> dict:
    """
    Executa um arquivo SQL que pode conter múltiplas queries
    """
    print(f"\n{'='*80}")
    print(f"🔍 Processando: {query_file.name}")
    print(f"{'='*80}\n")

    # Ler o arquivo SQL
    with open(query_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Dividir em queries individuais (separadas por ponto-e-vírgula)
    queries = [q.strip() for q in sql_content.split(';') if q.strip() and not q.strip().startswith('--')]

    results = []

    for idx, query in enumerate(queries, 1):
        # Pular comentários
        if query.strip().startswith('--'):
            continue

        # Extrair nome da query do comentário acima
        query_name = f"query_{idx}"
        lines = query.split('\n')
        for line in lines:
            if line.strip().startswith('--') and len(line.strip()) > 3:
                query_name = line.strip()[2:].strip().replace(' ', '_').lower()
                break

        # Executar query
        result = run_steampipe_query(query)

        if result:
            results.append({
                "name": query_name,
                "data": result
            })

    return {
        "file": query_file.name,
        "timestamp": datetime.now().isoformat(),
        "queries": results
    }

def run_steampipe_query(query: str) -> dict:
    """
    Executa uma query SQL diretamente via Steampipe
    """
    try:
        result = subprocess.run(
            ["steampipe", "query", query, "--output", "json"],
            capture_output=True,
            text=True,
            check=True,
            input=query
        )

        return json.loads(result.stdout)

    except Exception as e:
        print(f"⚠️  Erro: {e}")
        return None

def main():
    """
    Função principal
    """
    print("\n" + "="*80)
    print("🔐 AUDITORIA DE SEGURANÇA DA ORGANIZAÇÃO GITHUB")
    print("="*80 + "\n")

    all_results = {
        "scan_timestamp": datetime.now().isoformat(),
        "results": {}
    }

    # Query files
    query_files = [
        QUERIES_DIR / "repositories.sql",
        QUERIES_DIR / "users_permissions.sql",
        QUERIES_DIR / "security_settings.sql",
        QUERIES_DIR / "branch_protection.sql",
        QUERIES_DIR / "dependabot.sql",
        QUERIES_DIR / "user_permissions.sql",
        QUERIES_DIR / "repo_collaborators.sql",
        QUERIES_DIR / "public_repos_security.sql",
        QUERIES_DIR / "members_2fa_audit.sql",
        QUERIES_DIR / "security_files.sql"
    ]

    # Executar cada arquivo de queries
    for query_file in query_files:
        if not query_file.exists():
            print(f"⚠️  Arquivo não encontrado: {query_file}")
            continue

        # Executar queries do arquivo usando steampipe query diretamente
        category = query_file.stem
        print(f"\n🔍 Categoria: {category.upper()}")

        # Executar arquivo completo
        result = run_query(query_file, output_format="json")

        # Salvar resultados
        all_results["results"][category] = result

        # Salvar JSON individual
        save_results(result, category)

        # Tentar salvar CSV se houver dados tabulares
        if "rows" in result:
            save_csv(result, category)

    # Salvar resultado consolidado
    consolidated_file = RESULTS_DIR.parent / f"audit_results_{TIMESTAMP}.json"
    with open(consolidated_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'='*80}")
    print(f"✅ Auditoria concluída!")
    print(f"📁 Resultados salvos em: {RESULTS_DIR}")
    print(f"📄 Arquivo consolidado: {consolidated_file}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
