"""Revierte doble-encoding UTF-8 en archivos JSON.

PowerShell `Out-File -Encoding utf8` lee strings como Latin-1 y re-codifica
como UTF-8, generando bytes doble-codificados. Este script detecta y revierte
esos casos via reemplazo de patrones específicos (no re-codificación completa,
para evitar romper caracteres Unicode legítimos como ⇒, →, etc.).

Uso:
    python scripts/fix_double_encoding.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Tabla de reemplazos: secuencia mojibake → carácter correcto.
# Cada clave es la secuencia que aparece cuando un carácter UTF-8 fue
# leído como Latin-1 y re-codificado como UTF-8 ("doble encoding").
MOJIBAKE_REPLACEMENTS = {
    "Ã¡": "á",
    "Ã©": "é",
    "Ã­": "í",
    "Ã³": "ó",
    "Ãº": "ú",
    "Ã±": "ñ",
    "Ã\x81": "Á",
    "Ã\x89": "É",
    "Ã\x8d": "Í",
    "Ã\x93": "Ó",
    "Ã\x9a": "Ú",
    "Ã\x91": "Ñ",
    "Â¡": "¡",
    "Â¿": "¿",
    "Â°": "°",
    "Â·": "·",
    "Â´": "´",
    "â\x80\x99": "'",
    "â\x80\x9c": '"',
    "â\x80\x9d": '"',
    "â\x80\x93": "-",
    "â\x80\x94": "—",
    "â\x80\xa6": "...",
}


def fix_string(s: str) -> str:
    """Aplica todos los reemplazos de mojibake conocidos."""
    if not isinstance(s, str):
        return s
    for bad, good in MOJIBAKE_REPLACEMENTS.items():
        if bad in s:
            s = s.replace(bad, good)
    return s


def fix_recursive(obj):
    if isinstance(obj, dict):
        return {k: fix_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_recursive(item) for item in obj]
    elif isinstance(obj, str):
        return fix_string(obj)
    return obj


def fix_file(path: Path) -> bool:
    """Devuelve True si se hicieron cambios."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"SKIP {path}: {e}")
        return False

    original = json.dumps(data, sort_keys=True, ensure_ascii=False)
    fixed = fix_recursive(data)
    fixed_str = json.dumps(fixed, sort_keys=True, ensure_ascii=False)

    if original == fixed_str:
        return False

    with open(path, "w", encoding="utf-8") as f:
        json.dump(fixed, f, indent=2, ensure_ascii=False)
    return True


def main() -> None:
    base = Path("data/patch_notes")
    if not base.exists():
        print(f"ERROR: {base} no existe")
        sys.exit(1)

    fixed_count = 0
    total = 0
    for json_file in base.rglob("*.json"):
        total += 1
        if fix_file(json_file):
            print(f"FIXED {json_file}")
            fixed_count += 1

    print(f"\nResumen: {fixed_count}/{total} archivos modificados")


if __name__ == "__main__":
    main()
