"""Levanta el fixture de Rift Duel en localhost.

Uso, desde la raiz del repo:
    python claude-design-handoff/rift-duel/serve_fixture.py [--port 8007] [--build] [--open]

Sirve esta carpeta en la raiz del sitio (/ abre fixture.html) y /assets/ desde la
carpeta assets/ del repo, donde estan los splash arts de Data Dragon que usan los
retratos. Solo escucha en 127.0.0.1. Solo libreria estandar.

--build regenera fixture.html antes de servir (si fixture.json tiene errores,
avisa y sirve la ultima version valida). --open abre el navegador recien cuando
el servidor ya esta escuchando. Si el puerto ya lo usa este mismo fixture, solo
abre el navegador.
"""

from __future__ import annotations

import argparse
import os
import posixpath
import subprocess
import sys
import urllib.request
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_PORT = int(os.environ.get("LOLCLI_RIFT_DUEL_PORT", "8007"))
MARKER = "Generado por build_fixture.py"  # comentario que lleva fixture.html


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


def is_fixture_server(url: str) -> bool:
    """True si en esa URL ya responde este fixture (sin pasar por proxies del sistema)."""
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(url, timeout=2) as resp:
            return MARKER in resp.read(4096).decode("utf-8", "replace")
    except OSError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Sirve el fixture de Rift Duel en localhost.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="puerto (default: 8007 o LOLCLI_RIFT_DUEL_PORT)")
    parser.add_argument("--build", action="store_true", help="regenerar fixture.html antes de servir")
    parser.add_argument("--open", action="store_true", help="abrir el navegador cuando el servidor esté listo")
    args = parser.parse_args()
    url = f"http://localhost:{args.port}/"

    if args.build:
        print("Regenerando fixture.html desde fixture.json...")
        if subprocess.run([sys.executable, str(HERE / "build_fixture.py")], check=False).returncode != 0:
            print("AVISO: fixture.json tiene errores (ver arriba). Se sirve la última versión válida.")

    handler = partial(FixtureHandler, directory=str(HERE))
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    except OSError as exc:
        if is_fixture_server(url):
            print(f"El fixture ya está levantado en {url}")
            if args.open:
                webbrowser.open(url)
            return 0
        print(f"ERROR: el puerto {args.port} lo está usando otro programa ({exc}).", file=sys.stderr)
        print("Probá con otro puerto: set LOLCLI_RIFT_DUEL_PORT=8017 y volvé a correr el .bat.", file=sys.stderr)
        return 1

    # El socket ya escucha desde acá: el navegador no puede llegar antes que el servidor.
    print(f"Rift Duel en {url}")
    print("Dejá esta ventana abierta; si la cerrás, se cae el servidor. Ctrl+C para cortar.")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
