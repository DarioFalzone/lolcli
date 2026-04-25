#!/usr/bin/env python3
"""Genera el dashboard mejorado del Meta Analyzer."""

from pathlib import Path

from riot_lol_cli.dashboard_enhanced import save_enhanced_dashboard
from riot_lol_cli.settings import get_meta_api_port


def main() -> int:
    print("\n" + "=" * 70)
    print("🎨 GENERADOR DE DASHBOARD MEJORADO - LOLCLI Meta Analyzer")
    print("=" * 70)

    try:
        output_path = Path("outputs/meta-analyzer-dashboard-enhanced.html")
        save_enhanced_dashboard(str(output_path))

        api_port = get_meta_api_port()
        print("\n✅ Dashboard mejorado generado exitosamente")
        print(f"📁 Ubicación: {output_path}")
        print("\n🌐 Acceso:")
        print(f"   - Local: file:///{output_path.absolute()}")
        print(f"   - API: http://localhost:{api_port}/dashboard-enhanced")
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
