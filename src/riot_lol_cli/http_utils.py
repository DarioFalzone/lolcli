"""Utilities HTTP transversales para servidores FastAPI del paquete.

Centraliza el `UTF8JSONResponse` para garantizar charset=utf-8 en todas las
respuestas JSON. Ver `tests/test_encoding_global.py` para el guardrail que
fuerza su uso en cada servidor.
"""

from __future__ import annotations

from fastapi.responses import JSONResponse


class UTF8JSONResponse(JSONResponse):
    """JSONResponse que fuerza charset=utf-8 en Content-Type.

    Starlette por defecto sirve application/json sin charset, lo que provoca
    que algunos navegadores interpreten la respuesta como Latin-1 y rompan
    caracteres no-ASCII. Ver tests/patch_notes/test_encoding.py para regresion
    guard.

    Uso:
        from riot_lol_cli.http_utils import UTF8JSONResponse
        app = FastAPI(default_response_class=UTF8JSONResponse)
    """

    media_type = "application/json; charset=utf-8"
