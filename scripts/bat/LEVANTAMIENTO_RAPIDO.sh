#!/bin/bash
# ============================================================================
# LOLCLI Meta Analyzer - Script de Levantamiento Rápido (Linux/Mac)
# ============================================================================

# Navegar al root del repo
cd "$(dirname "$0")/../.."
META_API_PORT="${LOLCLI_META_API_PORT:-8000}"

clear

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   LOLCLI Meta Analyzer - Levantamiento Rápido            ║"
echo "║   [BD + API + Frontend]                                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Paso 1: Instalar dependencias
echo "[1/4] Instalando dependencias..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Error instalando dependencias"
    exit 1
fi
echo "✅ Dependencias instaladas"

# Paso 2: Setup BD + datos demo
echo ""
echo "[2/4] Inicializando BD y generando datos demo..."
python3 scripts/setup_meta_analyzer.py --demo
if [ $? -ne 0 ]; then
    echo "❌ Error en setup"
    exit 1
fi
echo "✅ BD lista"

# Paso 3: Información
echo ""
echo "[3/4] Información del sistema:"
echo ""
echo "   📊 Base de datos: data/meta_analyzer.db"
echo "   🎨 Frontend: outputs/meta-analyzer-dashboard.html"
echo "   🚀 API Backend: http://localhost:${META_API_PORT}"
echo "   📚 Docs: http://localhost:${META_API_PORT}/docs"
echo ""

# Paso 4: Levantar API (opcional)
echo "[4/4] ¿Deseas levantar el API Backend? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "✅ Levantando API en puerto ${META_API_PORT}..."
    echo ""
    echo "📝 Cuando veas 'Uvicorn running on http://0.0.0.0:${META_API_PORT}', abre en otra terminal:"
    echo "   open outputs/meta-analyzer-dashboard.html  (Mac)"
    echo "   xdg-open outputs/meta-analyzer-dashboard.html  (Linux)"
    echo ""
    
    python3 -m uvicorn riot_lol_cli.api_server:app --reload --port "${META_API_PORT}"
else
    echo ""
    echo "⚠️  API no levantado. Para levantarlo manualmente:"
    echo "   python3 -m uvicorn riot_lol_cli.api_server:app --reload"
    echo ""
    echo "📱 Para ver el frontend sin API (datos estáticos):"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   open outputs/meta-analyzer-dashboard.html"
    else
        echo "   xdg-open outputs/meta-analyzer-dashboard.html"
    fi
    echo ""
fi

echo ""
echo "✨ ¡Listo!"
