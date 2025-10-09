from __future__ import annotations

import os
from pathlib import Path
from typing import Dict


TEMPLATES_DIR = Path(__file__).parent / "templates"


def ensure_out_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def render_template(template_name: str, placeholders: Dict[str, str]) -> str:
    template_path = TEMPLATES_DIR / f"{template_name}.html"
    if not template_path.exists():
        raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
    html = template_path.read_text(encoding="utf-8")
    # Reemplazo simple de llaves dobles {{key}}
    for k, v in placeholders.items():
        html = html.replace(f"{{{{{k}}}}}", str(v))
    return html
