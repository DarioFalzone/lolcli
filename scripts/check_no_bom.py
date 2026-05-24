"""Pre-commit hook: rechaza archivos JSON con BOM UTF-8.

Uso (manual):
    python scripts/check_no_bom.py path/to/file.json [more.json ...]

El hook de pre-commit lo invoca automáticamente con los archivos JSON
modificados en el commit.
"""

from __future__ import annotations

import sys
from pathlib import Path

BOM = b"\xef\xbb\xbf"


def main() -> int:
    if len(sys.argv) < 2:
        return 0

    offenders = []
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.is_file():
            continue
        try:
            with open(path, "rb") as f:
                if f.read(3) == BOM:
                    offenders.append(str(path))
        except OSError:
            continue

    if offenders:
        print("BOM UTF-8 detectado en JSON (rompe parsers + frontend):")
        for o in offenders:
            print(f"  - {o}")
        print()
        print("FIX:")
        print(
            "  python -c \"import json,sys; "
            "p=sys.argv[1]; "
            "json.dump(json.load(open(p,'r',encoding='utf-8-sig')), "
            "open(p,'w',encoding='utf-8'), indent=2, ensure_ascii=False)\" "
            "FILE.json"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
