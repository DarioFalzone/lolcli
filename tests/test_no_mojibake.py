"""
Guardrail anti-mojibake.

Falla si algun archivo relevante del repo contiene secuencias tipicas de
doble-encoding UTF-8 -> Latin-1/cp1252 o caracteres de reemplazo.

Regla: todo archivo de texto en este repo se lee y escribe SIEMPRE como UTF-8
sin BOM. PowerShell `Set-Content -Encoding UTF8` agrega BOM y debe evitarse;
usar `[System.IO.File]::WriteAllText($p, $c, [System.Text.UTF8Encoding]::new($false))`
o tooling que respete UTF-8 sin BOM.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

SCAN_DIRS = (
    "src",
    "templates",
    "scripts",
    "docs",
    "outputs",
    "projects/active",
    ".agent/rules",
)
SCAN_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "bitacora_de_cambios.md",
)
SCAN_EXTS = (".py", ".html", ".css", ".js", ".md", ".json", ".bat", ".sh", ".ps1")
QUESTION_RUN_RE = re.compile(r"[?]{4,}")


def _double_utf8_latin1(text: str) -> str:
    return text.encode("utf-8").decode("latin-1")


_SINGLE_PASS_MARKERS = (
    "\u00c3\u00a1",
    "\u00c3\u00a9",
    "\u00c3\u00ad",
    "\u00c3\u00b3",
    "\u00c3\u00ba",
    "\u00c3\u00b1",
    "\u00c3\u0081",
    "\u00c3\u0089",
    "\u00c3\u008d",
    "\u00c3\u0093",
    "\u00c3\u009a",
    "\u00c3\u0091",
    "\u00c2\u00a1",
    "\u00c2\u00bf",
    "\u00c2\u00b7",
    "\u00e2\u20ac",
    "\u00e2\u201e",
    "\u00e2\u0161",
    "\u00e2\u0153",
    "\u00f0\u0178",
    "\ufffd",
)
_DOUBLE_PASS_MARKERS = tuple(_double_utf8_latin1(marker) for marker in _SINGLE_PASS_MARKERS if marker != "\ufffd")
MOJIBAKE_MARKERS = _SINGLE_PASS_MARKERS + _DOUBLE_PASS_MARKERS

ALLOW_MOJIBAKE = (
    "projects/legacy",
    "claude-design-handoff",
    "claude-design-handoff_revolution",
    # scripts/fix_double_encoding.py contiene los patterns mojibake como
    # strings literales porque ES el script que los reemplaza. Necesario.
    "scripts/fix_double_encoding.py",
)


def _iter_text_files() -> list[Path]:
    files: list[Path] = []

    for relative_dir in SCAN_DIRS:
        base = REPO_ROOT / relative_dir
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in SCAN_EXTS:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if any(allow in rel for allow in ALLOW_MOJIBAKE):
                continue
            files.append(path)

    for relative_file in SCAN_FILES:
        path = REPO_ROOT / relative_file
        if not path.exists():
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if any(allow in rel for allow in ALLOW_MOJIBAKE):
            continue
        files.append(path)

    return files


def test_no_mojibake_in_repo_text_surfaces() -> None:
    offenders: dict[str, list[str]] = {}
    for path in _iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            offenders.setdefault(str(path.relative_to(REPO_ROOT)), []).append("no es UTF-8 valido")
            continue

        hits = [marker.encode("unicode_escape").decode("ascii") for marker in MOJIBAKE_MARKERS if marker in text]
        if QUESTION_RUN_RE.search(text):
            hits.append("question-run")
        if hits:
            offenders[str(path.relative_to(REPO_ROOT))] = hits

    if offenders:
        msg = "Mojibake detectado:\n"
        for file_name, markers in sorted(offenders.items()):
            msg += f"  {file_name}: {markers!r}\n"
        msg += (
            "\nReencode el archivo: leerlo con cp1252, escribirlo con UTF-8 sin BOM. "
            "Ver tests/test_no_mojibake.py para la regla canonica."
        )
        pytest.fail(msg)


def test_no_utf8_bom_in_python_sources() -> None:
    bom_offenders: list[str] = []
    for relative_dir in SCAN_DIRS:
        base = REPO_ROOT / relative_dir
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            with path.open("rb") as handle:
                head = handle.read(3)
            if head == b"\xef\xbb\xbf":
                bom_offenders.append(str(path.relative_to(REPO_ROOT)))
    if bom_offenders:
        pytest.fail(
            "Archivos Python con BOM UTF-8 detectados:\n  "
            + "\n  ".join(bom_offenders)
            + "\n\nGuardar como UTF-8 sin BOM. PowerShell `Set-Content -Encoding UTF8` "
            "agrega BOM; usar UTF8Encoding(false) en su lugar."
        )
