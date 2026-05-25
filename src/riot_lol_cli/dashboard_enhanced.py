"""Dashboard Mejorado - HTML/JS con tabs avanzados para Meta Analyzer.

El contenido HTML/CSS/JS vive extraído en
`src/riot_lol_cli/meta_api/static/dashboard-enhanced/` desde [2026-05-25]
(PR-D3) para facilitar mantenimiento. Este módulo lee los 3 archivos en
import-time y los ensambla en `ENHANCED_DASHBOARD_HTML` manteniendo el
contrato API previo (string completo embebido).
"""

from __future__ import annotations

from pathlib import Path

_STATIC_DIR = Path(__file__).parent / "meta_api" / "static" / "dashboard-enhanced"
_CSS_PATH = _STATIC_DIR / "dashboard.css"
_JS_PATH = _STATIC_DIR / "dashboard.js"
_HTML_PATH = _STATIC_DIR / "index.html"


def _build_dashboard_html() -> str:
    """Lee los 3 archivos extraídos y sustituye placeholders."""
    css = _CSS_PATH.read_text(encoding="utf-8")
    js = _JS_PATH.read_text(encoding="utf-8")
    html = _HTML_PATH.read_text(encoding="utf-8")
    return html.replace("/* {{DASHBOARD_CSS}} */", css).replace(
        "/* {{DASHBOARD_JS}} */", js
    )


ENHANCED_DASHBOARD_HTML = _build_dashboard_html()


def save_enhanced_dashboard(
    output_path: str = "outputs/meta-analyzer-dashboard-enhanced.html",
) -> None:
    """Guarda el dashboard mejorado en archivo."""
    import logging

    _logger = logging.getLogger(__name__)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ENHANCED_DASHBOARD_HTML)
    _logger.info("Dashboard mejorado guardado en: %s", output_path)


if __name__ == "__main__":
    save_enhanced_dashboard()
