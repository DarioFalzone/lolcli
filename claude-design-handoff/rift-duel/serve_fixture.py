"""Levanta el fixture de Rift Duel en localhost.

Uso, desde la raiz del repo:
    python claude-design-handoff/rift-duel/serve_fixture.py [--port 8007]

Sirve esta carpeta en la raiz del sitio (/ abre fixture.html) y /assets/ desde la
carpeta assets/ del repo, donde estan los splash arts de Data Dragon que usan los
retratos. Solo escucha en 127.0.0.1. Solo libreria estandar.
"""

from __future__ import annotations

import argparse
import os
import posixpath
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_PORT = int(os.environ.get("LOLCLI_RIFT_DUEL_PORT", "8007"))


class FixtureHandler(SimpleHTTPRequestHandler):
    """/ -> fixture.html; /assets/... -> assets/ del repo; el resto, esta carpeta."""

    def translate_path(self, path: str) -> str:
        # Normalizar antes de decidir: /assets/../.git no tiene que escaparse de assets/.
        route = posixpath.normpath(unquote(urlsplit(path).path))
        if route == "/":
            return str(HERE / "fixture.html")
        if route == "/assets" or route.startswith("/assets/"):
            saved, self.directory = self.directory, str(REPO)
            try:
                return super().translate_path(route)
            finally:
                self.directory = saved
        return super().translate_path(route)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sirve el fixture de Rift Duel en localhost.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="puerto (default: 8007 o LOLCLI_RIFT_DUEL_PORT)")
    args = parser.parse_args()

    handler = partial(FixtureHandler, directory=str(HERE))
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    except OSError as exc:
        print(f"ERROR: no se pudo usar el puerto {args.port}: {exc}", file=sys.stderr)
        return 1
    print(f"Rift Duel en http://localhost:{args.port}/  (Ctrl+C para cortar)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
