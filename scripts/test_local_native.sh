#!/bin/bash
# Script para testar o org-security-scan localmente usando apenas GitHub API nativa
# NÃO requer instalação do Steampipe!

set -e

echo "========================================"
echo "🧪 TESTE LOCAL - ORG SECURITY SCAN"
echo "   (Usando GitHub API Nativa)"
echo "========================================"
echo ""

# Verificar Python
echo "1️⃣  Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    exit 1
fi
echo "✅ Python instalado: $(python3 --version)"
echo ""

# Verificar biblioteca requests
echo "2️⃣  Verificando biblioteca requests..."
if ! python3 -c "import requests" &> /dev/null; then
    echo "⚠️  Biblioteca requests não encontrada. Instalando..."
    pip install requests
else
    echo "✅ Biblioteca requests instalada"
fi
echo ""

# Verificar token do GitHub
echo "3️⃣  Verificando token do GitHub..."
if [ -z "$GH_TOKEN" ] && [ -z "$ORG_SECURITY_TOKEN" ] && [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Token do GitHub não encontrado!"
    echo ""
    echo "💡 Configure uma das variáveis de ambiente:"
    echo "   export GH_TOKEN='seu_token_aqui'"
    echo "   ou"
    echo "   export ORG_SECURITY_TOKEN='seu_token_aqui'"
    echo ""
    echo "🔗 Obtenha seu token em: https://github.com/settings/tokens"
    echo "   Scopes necessários: repo, read:org, read:user"
    exit 1
fi
echo "✅ Token do GitHub configurado"
echo ""

# Criar diretórios necessários
echo "4️⃣  Criando diretórios..."
mkdir -p reports/results
echo "✅ Diretórios criados"
echo ""

# Executar auditoria
echo "========================================"
echo "🔍 EXECUTANDO AUDITORIA"
echo "========================================"
echo ""

python3 scripts/github_api_audit.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "📊 GERANDO DASHBOARD"
    echo "========================================"
    echo ""

    python3 scripts/generate_dashboard.py

    if [ $? -eq 0 ]; then
        echo ""
        echo "========================================"
        echo "✅ TESTE CONCLUÍDO COM SUCESSO!"
        echo "========================================"
        echo ""
        echo "📁 Verifique os resultados em:"
        echo "   - reports/security_dashboard_latest.html"
        echo "   - reports/audit_results_*.json"
        echo "   - reports/results/"
        echo ""
        echo "💡 Abra o dashboard no navegador:"
        if command -v xdg-open &> /dev/null; then
            echo "   xdg-open reports/security_dashboard_latest.html"
        elif command -v open &> /dev/null; then
            echo "   open reports/security_dashboard_latest.html"
        else
            echo "   Abra manualmente: reports/security_dashboard_latest.html"
        fi
        echo ""
    else
        echo "❌ Erro ao gerar dashboard"
        exit 1
    fi
else
    echo "❌ Erro ao executar auditoria"
    exit 1
fi

echo ""
echo "🎉 Teste local concluído!"
echo ""
echo "ℹ️  Este script usa APENAS a GitHub API REST nativa"
echo "   Não requer instalação de Steampipe ou outras ferramentas"
