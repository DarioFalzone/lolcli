from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMPLATES_DIR = BASE_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"
VERSION_FILE = CONFIG_DIR / "version.json"


def ensure_runtime_directories() -> None:
    """Crea los directorios mínimos de runtime si todavía no existen."""
    for directory in (CONFIG_DIR, DATA_DIR, CACHE_DIR, OUTPUT_DIR, TEMPLATES_DIR):
        directory.mkdir(parents=True, exist_ok=True)
