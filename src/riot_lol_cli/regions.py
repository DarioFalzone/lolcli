PLATFORM_TO_REGIONAL = {
    # AMERICAS
    "na1": "americas",
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    "oc1": "americas",
    # EUROPE
    "euw1": "europe",
    "eun1": "europe",
    "tr1": "europe",
    "ru": "europe",
    # ASIA
    "kr": "asia",
    "jp1": "asia",
}


def get_regional_route(platform: str) -> str:
    """
    Dada la plataforma (p.ej. la2), retorna la ruta regional para Match-V5.
    Lanza ValueError si la plataforma no está soportada.
    """
    key = (platform or "").lower()
    if key not in PLATFORM_TO_REGIONAL:
        raise ValueError(
            f"Plataforma no soportada: {platform}. Usa una de: {', '.join(sorted(PLATFORM_TO_REGIONAL.keys()))}"
        )
    return PLATFORM_TO_REGIONAL[key]
