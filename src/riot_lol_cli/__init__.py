from riot_lol_cli.versioning import bump_version, get_version


__version__ = get_version()

__all__ = ["__version__", "get_version", "bump_version"]
