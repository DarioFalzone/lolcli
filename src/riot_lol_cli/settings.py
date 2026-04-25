import os

DEFAULT_DDRAGON_VERSION = "15.20.1"
DEFAULT_META_API_HOST = "0.0.0.0"
DEFAULT_META_API_PORT = 8000
DEFAULT_DRAFT_ADVISOR_HOST = "0.0.0.0"
DEFAULT_DRAFT_ADVISOR_PORT = 8001


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
