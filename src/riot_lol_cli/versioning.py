import json
from typing import Any, Optional

from riot_lol_cli import paths

DEFAULT_VERSION = "1.0.0"


def read_version_metadata() -> dict[str, Any]:
    """Lee metadata de versión sin mutar el repo si el archivo no existe."""
    if not paths.VERSION_FILE.exists():
        return {"version": DEFAULT_VERSION}

    try:
        with open(paths.VERSION_FILE, encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return {"version": DEFAULT_VERSION}

    if not isinstance(data, dict):
        return {"version": DEFAULT_VERSION}

    data.setdefault("version", DEFAULT_VERSION)
    return data


def get_version() -> str:
    return str(read_version_metadata().get("version", DEFAULT_VERSION))


def write_version(version: str, extra_metadata: Optional[dict[str, Any]] = None) -> str:
    """Persiste la versión preservando otros metadatos."""
    paths.ensure_runtime_directories()
    metadata = read_version_metadata()
    metadata["version"] = version
    if extra_metadata:
        metadata.update(extra_metadata)

    with open(paths.VERSION_FILE, "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    return version


def bump_version() -> str:
    """Incrementa el patch version siguiendo semver simple."""
    current_version = get_version()
    parts = current_version.split(".")

    try:
        major, minor, patch = (int(part) for part in parts[:3])
    except (TypeError, ValueError):
        return write_version(current_version)

    return write_version(f"{major}.{minor}.{patch + 1}")
