"""Guardrails globales de encoding UTF-8 para TODO el repo.

Estos tests son complementarios a `tests/test_no_mojibake.py` (que escanea
markdown/python por mojibake) y `tests/patch_notes/test_encoding.py` (que
valida el subsistema patch_notes especificamente).

Cubren:
1. Todos los JSONs del repo: sin BOM y sin doble-encoding.
2. Scripts PowerShell (.ps1) y batch (.bat): no usan `-Encoding UTF8` salvo
   explicitamente permitido (causa BOM).
3. Todos los servidores FastAPI: usan `UTF8JSONResponse` o equivalente con
   `charset=utf-8` en `default_response_class`.

Rompe CI si:
- Algun JSON tiene BOM o doble-encoding.
- Algun script PS1/BAT escribe con `-Encoding UTF8`.
- Algun `FastAPI()` se construye sin `default_response_class` con charset.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Mismos markers que test_encoding.py de patch_notes pero como bytes
DOUBLE_ENCODING_MARKERS = (
    b"\xc3\x83\xc2\xa1",
    b"\xc3\x83\xc2\xa9",
    b"\xc3\x83\xc2\xad",
    b"\xc3\x83\xc2\xb3",
    b"\xc3\x83\xc2\xba",
    b"\xc3\x83\xc2\xb1",
    b"\xc3\x82\xc2\xa1",
    b"\xc3\x82\xc2\xbf",
)

# Directorios que se excluyen del escaneo (legacy, terceros, etc.)
EXCLUDED_DIRS = (
    ".venv",
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "outputs",
    "projects/legacy",
    "claude-design-handoff",
    "claude-design-handoff_revolution",
    "assets",
    "data/cache",
    "data/meta_scraper/raw",
    "data/meta_scraper/normalized/backups",
    "data/meta_scraper/normalized/history",
    "data/patch_notes/raw",
    "data/patch_notes/normalized/history",
    "data/draft_advisor/kb",
    "data/items",
    "data/jungle_meta",
    "data/jungle_research",
    "data/meta_analyzer",
    "data/patch_notes/sources/ddragon",
    "data/patch_notes/sources/riot_calendar",
    "data/patch_notes/sources/lol_dev",
    "data/patch_notes/sources/lol_official",
)

# Excepciones especificas a las reglas de PowerShell encoding
POWERSHELL_ENCODING_ALLOWLIST = (
    # Scripts que documentan el problema o lo testean, pueden contener el patron
    "tests/test_no_mojibake.py",
    "tests/test_encoding_global.py",
    "tests/patch_notes/test_encoding.py",
    "scripts/fix_double_encoding.py",
)


def _is_excluded(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT).as_posix()
    return any(rel.startswith(d) or f"/{d}/" in f"/{rel}/" for d in EXCLUDED_DIRS)


def _iter_files_by_ext(*exts: str):
    """Itera archivos con las extensiones dadas, excluyendo paths irrelevantes."""
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in exts:
            continue
        if _is_excluded(path):
            continue
        yield path


def test_all_repo_json_files_no_bom():
    """Ningun JSON del repo debe tener BOM UTF-8."""
    bom = b"\xef\xbb\xbf"
    offenders = []
    for path in _iter_files_by_ext(".json"):
        with open(path, "rb") as f:
            head = f.read(3)
        if head == bom:
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert not offenders, (
        "JSON con BOM UTF-8 (rompe parsers y causa mojibake en frontend):\n"
        + "\n".join(f"  - {p}" for p in offenders)
        + "\n\nFIX: Re-guardar con Python:\n"
        + "  python -c \"import json; json.dump(json.load(open('FILE','r',encoding='utf-8-sig')), open('FILE','w',encoding='utf-8'), indent=2, ensure_ascii=False)\""
    )


def test_all_repo_json_files_no_double_encoding():
    """Ningun JSON del repo debe contener mojibake doble-codificado."""
    offenders = []
    for path in _iter_files_by_ext(".json"):
        try:
            with open(path, "rb") as f:
                raw = f.read()
        except OSError:
            continue
        found = [m.hex() for m in DOUBLE_ENCODING_MARKERS if m in raw]
        if found:
            offenders.append((str(path.relative_to(REPO_ROOT)), found))

    assert not offenders, (
        "JSON con doble-encoding UTF-8 (mojibake en disco):\n"
        + "\n".join(f"  - {p}: bytes={m}" for p, m in offenders)
        + "\n\nFIX: `python scripts/fix_double_encoding.py`"
    )


def test_powershell_scripts_no_unsafe_encoding():
    """Scripts PowerShell/Batch no deben usar `-Encoding UTF8` (agrega BOM).

    `Set-Content -Encoding UTF8` y `Out-File -Encoding UTF8` agregan BOM
    automaticamente. Si necesitas escribir UTF-8 desde PowerShell, usar
    `[System.IO.File]::WriteAllText($p, $c, [System.Text.UTF8Encoding]::new($false))`
    o delegar a Python.
    """
    # Patron: -Encoding UTF8 (case-insensitive) PERO no -Encoding UTF8NoBOM ni utf8BOM
    pattern = re.compile(r"-Encoding\s+UTF8(?!NoBOM|BOM)\b", re.IGNORECASE)
    offenders = []

    for path in _iter_files_by_ext(".ps1", ".bat", ".cmd"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in POWERSHELL_ENCODING_ALLOWLIST:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in pattern.finditer(text):
            line_num = text[: match.start()].count("\n") + 1
            offenders.append(f"{rel}:{line_num}: '{match.group(0)}'")

    assert not offenders, (
        "Scripts PowerShell/Batch usando `-Encoding UTF8` (agrega BOM):\n"
        + "\n".join(f"  - {o}" for o in offenders)
        + "\n\nFIX: Usar `-Encoding UTF8NoBOM` (PS 6+), o delegar a Python."
    )


def test_fastapi_apps_use_utf8_response_class():
    """Servidores FastAPI deben usar default_response_class con charset=utf-8.

    Sin esto, las respuestas JSON se sirven como application/json sin charset,
    lo que hace que el navegador asuma Latin-1 y rompa tildes.

    Excepcion permitida: subsistemas con tests propios que ya validan charset.
    """
    server_files = list(REPO_ROOT.glob("src/riot_lol_cli/*/server.py"))
    server_files.extend(REPO_ROOT.glob("src/riot_lol_cli/*server*.py"))

    # Pattern: si crea una FastAPI instance, debe usar default_response_class
    fastapi_create = re.compile(r"FastAPI\s*\(", re.MULTILINE)
    charset_class = re.compile(r"default_response_class\s*=", re.MULTILINE)
    charset_string = re.compile(r"charset\s*=\s*[\"']?utf-?8", re.IGNORECASE)

    offenders = []
    for path in server_files:
        if _is_excluded(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if not fastapi_create.search(text):
            continue
        # Si construye FastAPI, debe tener default_response_class O usar charset
        # en algun otro lado (ej: media_type custom)
        if charset_class.search(text) or charset_string.search(text):
            continue
        offenders.append(str(path.relative_to(REPO_ROOT)))

    assert not offenders, (
        "Servidores FastAPI sin `default_response_class` con charset=utf-8:\n"
        + "\n".join(f"  - {p}" for p in offenders)
        + "\n\nFIX: definir UTF8JSONResponse y pasarlo a FastAPI(default_response_class=...).\n"
        + "Referencia: src/riot_lol_cli/patch_notes/server.py:UTF8JSONResponse"
    )


def test_fix_double_encoding_script_works():
    """El script fix_double_encoding.py debe ser funcional."""
    script = REPO_ROOT / "scripts" / "fix_double_encoding.py"
    assert script.exists(), "scripts/fix_double_encoding.py no existe"

    # Importar el modulo y probar la funcion fix_string
    import importlib.util

    spec = importlib.util.spec_from_file_location("fix_double_encoding", script)
    if spec is None or spec.loader is None:
        pytest.fail("No se pudo cargar scripts/fix_double_encoding.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Verificar que el reemplazo basico funciona
    assert hasattr(module, "fix_string"), "fix_string no encontrado"
    assert hasattr(module, "fix_recursive"), "fix_recursive no encontrado"

    # Test directo: tomar bytes de mojibake conocido y verificar fix
    mojibake_input = b"\xc3\x83\xc2\xb3".decode("utf-8")  # "Ã³" como string
    fixed = module.fix_string(mojibake_input)
    assert fixed == "ó", f"Expected 'o-tilde', got: {fixed!r}"  # 'ó'
