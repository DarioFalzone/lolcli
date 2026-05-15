"""Tests de encoding UTF-8 para patch notes.

Previene regresiones que sucedieron en 2026-05-15:
1. PowerShell Out-File -Encoding utf8 agrega BOM y rompe parsers
2. PowerShell escritura genera doble-encoding (mojibake en disco)
3. FastAPI por defecto no envia charset=utf-8 en application/json
   lo que provoca que el navegador interprete como Latin-1

Estos tests rompen CI si:
- Algun JSON en data/patch_notes/ tiene BOM UTF-8
- Algun JSON en data/patch_notes/ tiene marcadores de doble-encoding
- El servidor responde JSON sin charset=utf-8
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from riot_lol_cli.patch_notes.server import create_app

REPO_ROOT = Path(__file__).resolve().parents[2]
PATCH_NOTES_DATA = REPO_ROOT / "data" / "patch_notes"

# Markers de doble-encoding UTF-8 expresados como bytes para evitar problemas
# de codificacion del source file. Cada marker son los bytes UTF-8 de un
# caracter mal codificado (ej: 'a-con-tilde' codificado como UTF-8 y luego
# reinterpretado como Latin-1 y re-codificado).
DOUBLE_ENCODING_MARKERS_BYTES = (
    b"\xc3\x83\xc2\xa1",  # a-con-tilde mal codificada
    b"\xc3\x83\xc2\xa9",  # e-con-tilde mal codificada
    b"\xc3\x83\xc2\xad",  # i-con-tilde mal codificada
    b"\xc3\x83\xc2\xb3",  # o-con-tilde mal codificada
    b"\xc3\x83\xc2\xba",  # u-con-tilde mal codificada
    b"\xc3\x83\xc2\xb1",  # n-con-virgulilla mal codificada
    b"\xc3\x82\xc2\xa1",  # signo de exclamacion apertura mal codificado
    b"\xc3\x82\xc2\xbf",  # signo de pregunta apertura mal codificado
)


def _iter_json_files(base: Path):
    if not base.exists():
        return
    yield from base.rglob("*.json")


def test_json_files_no_utf8_bom():
    """Ningun JSON en data/patch_notes/ debe tener BOM UTF-8."""
    bom = b"\xef\xbb\xbf"
    offenders = []
    for path in _iter_json_files(PATCH_NOTES_DATA):
        with open(path, "rb") as f:
            head = f.read(3)
        if head == bom:
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert not offenders, (
        "Archivos JSON con BOM UTF-8 (rompen parsers y causan mojibake):\n"
        + "\n".join(f"  - {p}" for p in offenders)
        + "\n\nFIX: Re-guardar con Python, no PowerShell Set-Content/Out-File -Encoding UTF8."
    )


def test_json_files_no_double_encoding():
    """Ningun JSON debe tener mojibake doble-codificado."""
    offenders = []
    for path in _iter_json_files(PATCH_NOTES_DATA):
        with open(path, "rb") as f:
            raw = f.read()
        found = [m.hex() for m in DOUBLE_ENCODING_MARKERS_BYTES if m in raw]
        if found:
            offenders.append((str(path.relative_to(REPO_ROOT)), found))

    assert not offenders, (
        "Archivos JSON con doble-encoding UTF-8 (mojibake en disco):\n"
        + "\n".join(f"  - {p}: bytes={m}" for p, m in offenders)
        + "\n\nFIX: Correr `python scripts/fix_double_encoding.py`"
    )


def test_api_response_has_utf8_charset():
    """Las respuestas JSON DEBEN incluir charset=utf-8.

    Sin esto, navegadores interpretan application/json como Latin-1 y
    rompen caracteres no-ASCII en el frontend.
    """
    app = create_app()
    client = TestClient(app)

    endpoints = [
        "/health",
        "/api/v1/patch-notes/list?locale=es-es",
        "/api/v1/patch-notes/manifest",
        "/api/v1/patch-notes/sources/registry",
    ]
    for endpoint in endpoints:
        resp = client.get(endpoint)
        assert resp.status_code == 200, f"{endpoint} no retorno 200"
        content_type = resp.headers.get("content-type", "")
        assert "charset=utf-8" in content_type.lower(), (
            f"{endpoint}: Content-Type sin charset=utf-8: '{content_type}'\n"
            f"FIX: Usar default_response_class=UTF8JSONResponse en server.py"
        )


def test_api_serves_no_double_encoded_bytes():
    """End-to-end: las respuestas no contienen mojibake."""
    app = create_app()
    client = TestClient(app)

    resp = client.get("/api/v1/patch-notes/list?locale=es-es")
    assert resp.status_code == 200

    raw = resp.content
    for marker in DOUBLE_ENCODING_MARKERS_BYTES:
        assert marker not in raw, (
            f"Respuesta API contiene doble-encoding (bytes {marker.hex()})\n"
            f"FIX: Revisar archivos en data/patch_notes/normalized/by_patch/"
        )


def test_mobalytics_breakdown_payload_intact():
    """Mobalytics Breakdown debe tener content_markdown sin mojibake."""
    breakdown_path = (
        PATCH_NOTES_DATA / "sources" / "mobalytics_breakdown" / "26.10.json"
    )
    if not breakdown_path.exists():
        pytest.skip("Mobalytics breakdown 26.10 no presente")

    with open(breakdown_path, "rb") as f:
        raw = f.read()

    # Sin BOM
    assert not raw.startswith(b"\xef\xbb\xbf"), "Mobalytics breakdown tiene BOM"

    # Sin doble-encoding
    for marker in DOUBLE_ENCODING_MARKERS_BYTES:
        assert marker not in raw, f"Mobalytics breakdown tiene doble-encoding {marker.hex()}"

    # Es UTF-8 valido y tiene contenido esperado
    data = json.loads(raw.decode("utf-8"))
    assert "payload" in data
    assert "content_markdown" in data["payload"]
    markdown = data["payload"]["content_markdown"]
    assert "Ambessa" in markdown
    assert "Patch Notes" in markdown
