#!/usr/bin/env python3
"""Resumen del estado documental/runtime del Dashboard mejorado."""

from pathlib import Path

from riot_lol_cli.paths import BASE_DIR


def exists(path: str) -> str:
    target = Path(path)
    if not target.is_absolute():
        target = BASE_DIR / target
    return "OK" if target.exists() else "MISSING"


def line(path: str, label: str) -> None:
    print(f"{exists(path):7} {path} - {label}")


def main() -> None:
    print("\nLOLCLI - Dashboard Enhanced")
    print("=" * 32)

    print("\nRuntime")
    line("src/riot_lol_cli/dashboard_enhanced.py", "generador dashboard enhanced")
    line("src/riot_lol_cli/dashboard.py", "dashboard standalone base")
    line("src/riot_lol_cli/meta_api/app.py", "FastAPI real del Meta Analyzer")
    line("scripts/generate_dashboard.py", "generacion HTML standalone")
    line("scripts/run_api.py", "runner API :8000")

    print("\nDocumentacion canonica")
    line("docs/dashboard/README.md", "guia del dashboard")
    line("docs/meta_analyzer/README.md", "guia del Meta Analyzer")
    line("docs/README.md", "indice de docs")
    line("projects/active/meta-analyzer-dashboard/README.md", "manifest de proyecto")
    line("AGENTS.md", "mapa maestro para agentes")

    print("\nHistorico absorbido")
    line("docs/dashboard/README.md", "guia canonica dashboard")
    line("bitacora_de_cambios.md", "historial de cambios significativos")

    print("\nURLs locales")
    print("Meta API: http://localhost:8000")
    print("Dashboard: http://localhost:8000/dashboard-enhanced")
    print("OpenAPI: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
