import os

DEFAULT_DDRAGON_VERSION = "16.9.1"
DEFAULT_META_API_HOST = "0.0.0.0"
DEFAULT_META_API_PORT = 8000
DEFAULT_DRAFT_ADVISOR_HOST = "0.0.0.0"
DEFAULT_DRAFT_ADVISOR_PORT = 8001
DEFAULT_META_SCRAPER_HOST = "0.0.0.0"
DEFAULT_META_SCRAPER_PORT = 8002
DEFAULT_JUNGLE_META_HOST = "0.0.0.0"
DEFAULT_JUNGLE_META_PORT = 8003


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default

    try:
        return int(raw)
    except ValueError:
        return default


def get_ddragon_version() -> str:
    return os.getenv("LOLCLI_DDRAGON_VERSION", DEFAULT_DDRAGON_VERSION)


def get_meta_api_host() -> str:
    return os.getenv("LOLCLI_META_API_HOST", DEFAULT_META_API_HOST)


def get_meta_api_port() -> int:
    return _get_env_int("LOLCLI_META_API_PORT", DEFAULT_META_API_PORT)


def get_draft_advisor_host() -> str:
    return os.getenv("LOLCLI_DRAFT_ADVISOR_HOST", DEFAULT_DRAFT_ADVISOR_HOST)


def get_draft_advisor_port() -> int:
    return _get_env_int("LOLCLI_DRAFT_ADVISOR_PORT", DEFAULT_DRAFT_ADVISOR_PORT)


def get_meta_scraper_host() -> str:
    return os.getenv("LOLCLI_META_SCRAPER_HOST", DEFAULT_META_SCRAPER_HOST)


def get_meta_scraper_port() -> int:
    return _get_env_int("LOLCLI_META_SCRAPER_PORT", DEFAULT_META_SCRAPER_PORT)


def get_jungle_meta_host() -> str:
    return os.getenv("LOLCLI_JUNGLE_META_HOST", DEFAULT_JUNGLE_META_HOST)


def get_jungle_meta_port() -> int:
    return _get_env_int("LOLCLI_JUNGLE_META_PORT", DEFAULT_JUNGLE_META_PORT)
