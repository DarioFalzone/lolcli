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
DEFAULT_ITEMS_BROWSER_HOST = "0.0.0.0"
DEFAULT_ITEMS_BROWSER_PORT = 8004
DEFAULT_PATCH_NOTES_HOST = "0.0.0.0"
DEFAULT_PATCH_NOTES_PORT = 8005
DEFAULT_HOME_HOST = "0.0.0.0"
DEFAULT_HOME_PORT = 8080


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


def get_items_browser_host() -> str:
    return os.getenv("LOLCLI_ITEMS_BROWSER_HOST", DEFAULT_ITEMS_BROWSER_HOST)


def get_items_browser_port() -> int:
    return _get_env_int("LOLCLI_ITEMS_BROWSER_PORT", DEFAULT_ITEMS_BROWSER_PORT)


def get_patch_notes_host() -> str:
    return os.getenv("LOLCLI_PATCH_NOTES_HOST", DEFAULT_PATCH_NOTES_HOST)


def get_patch_notes_port() -> int:
    return _get_env_int("LOLCLI_PATCH_NOTES_PORT", DEFAULT_PATCH_NOTES_PORT)


def get_patch_notes_cron_enabled() -> bool:
    """True si LOLCLI_PATCH_NOTES_CRON_ENABLED=1 (default: off)."""
    return os.getenv("LOLCLI_PATCH_NOTES_CRON_ENABLED", "0").strip() in {"1", "true", "True", "yes"}


def get_patch_notes_default_locale() -> str:
    return os.getenv("LOLCLI_PATCH_NOTES_DEFAULT_LOCALE", "es-es")


def get_patch_notes_max_patches() -> int:
    return _get_env_int("LOLCLI_PATCH_NOTES_MAX_PATCHES", 10)


def get_home_host() -> str:
    return os.getenv("LOLCLI_HOME_HOST", DEFAULT_HOME_HOST)


def get_home_port() -> int:
    return _get_env_int("LOLCLI_HOME_PORT", DEFAULT_HOME_PORT)
