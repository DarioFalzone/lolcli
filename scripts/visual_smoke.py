"""
Visual smoke test: captura una URL con Chrome headless y guarda PNG.

Uso:
    python scripts/visual_smoke.py URL [--out PATH] [--width 1600] [--height 1000]

Ejemplo:
    python scripts/visual_smoke.py http://localhost:8000/dashboard-enhanced
    -> outputs/visual-smoke/dashboard-enhanced.png

Pensado como ultimo paso obligatorio despues de cambios en cualquier surface
visual (Draft Advisor, Meta Analyzer dashboard, Home Hub, Items/Jungle/Meta
Scraper). Verificar JS+CSS+HTML en codigo no atrapa cascadas rotas, modales
fantasma ni mojibake renderizado.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

CHROME_PATHS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)


def find_chrome() -> str:
    for p in CHROME_PATHS:
        if Path(p).exists():
            return p
    found = shutil.which("chrome") or shutil.which("google-chrome") or shutil.which("chromium")
    if found:
        return found
    raise SystemExit("Chrome no encontrado. Instalar Chrome o pasar PATH explicito.")


def default_out(url: str) -> Path:
    parsed = urlparse(url)
    name = (parsed.path.strip("/") or parsed.netloc).replace("/", "-") or "page"
    return Path("outputs/visual-smoke") / f"{name}.png"


def capture(url: str, out: Path, width: int, height: int, wait_ms: int) -> None:
    out = out.resolve()  # Chrome necesita path absoluto
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    chrome = find_chrome()
    # user-data-dir aislado evita conflicto con instancias abiertas del usuario.
    import tempfile
    with tempfile.TemporaryDirectory(prefix="visual-smoke-") as tmpdir:
        args = [
            chrome,
            "--headless=new",
            f"--screenshot={out}",
            f"--window-size={width},{height}",
            "--hide-scrollbars",
            "--disable-gpu",
            f"--virtual-time-budget={wait_ms}",
            f"--user-data-dir={tmpdir}",
            "--no-first-run",
            "--no-default-browser-check",
            url,
        ]
        result = subprocess.run(args, check=False, capture_output=True, timeout=30)
    if not out.exists():
        stderr = result.stderr.decode("utf-8", errors="replace")[:500]
        raise SystemExit(f"Screenshot no generado: {out}\nstderr: {stderr}")
    print(f"OK {out} ({out.stat().st_size} bytes)")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("url")
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--width", type=int, default=1600)
    p.add_argument("--height", type=int, default=1000)
    p.add_argument("--wait", type=int, default=4000, help="virtual time budget en ms")
    args = p.parse_args()
    out = args.out or default_out(args.url)
    capture(args.url, out, args.width, args.height, args.wait)


if __name__ == "__main__":
    sys.exit(main())
