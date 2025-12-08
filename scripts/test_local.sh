#!/bin/bash
# Script para testar o org-security-scan localmente

set -e

echo "========================================"
echo "🧪 TESTE LOCAL - ORG SECURITY SCAN"
echo "========================================"
echo ""

# Verificar se Steampipe está instalado
echo "1️⃣  Verificando Steampipe..."
if ! command -v steampipe &> /dev/null; then
    echo "❌ Steampipe não encontrado!"
    echo "💡 Instale com: sudo /bin/sh -c \"\$(curl -fsSL https://steampipe.io/install/steampipe.sh)\""
    exit 1
fi
echo "✅ Steampipe instalado: $(steampipe -v)"
echo ""

# Verificar plugin GitHub
echo "2️⃣  Verificando plugin GitHub..."
if ! steampipe plugin list | grep -q "github"; then
    echo "⚠️  Plugin GitHub não encontrado. Instalando..."
    steampipe plugin install github
else
    echo "✅ Plugin GitHub instalado"
fi
echo ""

# Verificar configuração
echo "3️⃣  Verificando configuração..."
if [ ! -f ~/.steampipe/config/github.spc ]; then
    echo "⚠️  Configuração não encontrada em ~/.steampipe/config/github.spc"
    echo "💡 Copie o arquivo exemplo:"
    echo "   cp steampipe.spc.example ~/.steampipe/config/github.spc"
    echo "   Edite o arquivo e adicione seu GitHub token"
    exit 1
fi
echo "✅ Configuração encontrada"
echo ""

# Verificar Python
echo "4️⃣  Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    exit 1
fi
echo "✅ Python instalado: $(python3 --version)"
echo ""

# Iniciar Steampipe service
echo "5️⃣  Iniciando Steampipe service..."
steampipe service start
sleep 5
echo "✅ Steampipe service iniciado"
echo ""

# Criar diretórios necessários
echo "6️⃣  Criando diretórios..."
mkdir -p reports/results
echo "✅ Diretórios criados"
echo ""

# Executar auditoria
echo "========================================"
echo "🔍 EXECUTANDO AUDITORIA"
echo "========================================"
echo ""

python3 scripts/run_audit.py

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
        echo "   - reports/results/"
        echo ""
        echo "💡 Abra o dashboard no navegador:"
        echo "   xdg-open reports/security_dashboard_latest.html"
        echo "   (ou abra manualmente o arquivo HTML)"
        echo ""
    else
        echo "❌ Erro ao gerar dashboard"
        exit 1
    fi
else
    echo "❌ Erro ao executar auditoria"
    exit 1
fi

# Parar Steampipe service
echo "Parando Steampipe service..."
steampipe service stop

echo ""
echo "🎉 Teste local concluído!"
