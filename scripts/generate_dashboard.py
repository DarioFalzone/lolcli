#!/usr/bin/env python3
"""
Generate Enhanced Dashboard
Script para generar el dashboard mejorado con tabs avanzados
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from riot_lol_cli.dashboard_enhanced import save_enhanced_dashboard


def main():
    """Genera el dashboard mejorado"""
    print("\n" + "="*70)
    print("🎨 GENERADOR DE DASHBOARD MEJORADO - LOLCLI Meta Analyzer")
    print("="*70)
    
    try:
        output_path = "outputs/meta-analyzer-dashboard-enhanced.html"
        save_enhanced_dashboard(output_path)
        
        print(f"\n✅ Dashboard mejorado generado exitosamente")
        print(f"📁 Ubicación: {output_path}")
        print(f"\n🌐 Acceso:")
        print(f"   - Local: file:///{Path(output_path).absolute()}")
        print(f"   - API: http://localhost:8000/dashboard-enhanced")
        
        print(f"\n📊 Características del dashboard mejorado:")
        print(f"   ✓ Dashboard - Tier List de ADCs actuales")
        print(f"   ✓ Matchups - Historial con grilla filtrable")
        print(f"   ✓ Items - Análisis de construcción por campeón")
        print(f"   ✓ Raw Data - Datos sin filtrar con source logging")
        print(f"   ✓ Click en campeón → Ver detalles en modal")
        print(f"   ✓ Filtros por campeón, horas, límite")
        print(f"   ✓ Data source attribution en cada registro")
        
        print(f"\n⚙️ Requiere que esté corriendo:")
        print(f"   1. Base de datos: python setup_meta_analyzer.py")
        print(f"   2. API server: python run_api.py")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
