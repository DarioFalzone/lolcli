from __future__ import annotations

from pydantic import BaseModel, Field


class DuoSynergyEntry(BaseModel):
    """Representa una fila de sinergia entre el campeón de enfoque y un jungla."""

    jungler_id: str = Field(..., description="ID canónico del campeón jungla en Data Dragon (ej. LeeSin).")
    jungler_name: str = Field(..., description="Nombre de visualización del jungla (ej. Lee Sin).")
    base_winrate: float = Field(..., description="Win Rate base individual del campeón seleccionado.")
    jungle_winrate: float = Field(..., description="Win Rate base individual del jungla.")
    duo_winrate: float = Field(..., description="Win Rate promedio combinado del dúo.")
    synergy_factor: float = Field(..., description="Factor de bonificación o sinergia en porcentaje.")
    duo_pickrate: float = Field(..., description="Popularidad o Pick Rate del dúo.")
    matches: int = Field(..., description="Número total de partidas analizadas en este dúo.")
    tier: str = Field(..., description="Tier de sinergia (S, A, B, C).")
    advantages: list[str] = Field(..., description="Ventajas estratégicas redactadas en español rioplatense.")


class ChampionDuoDetails(BaseModel):
    """Detalle completo del análisis de sinergias para un campeón seleccionado."""

    champion_id: str = Field(..., description="ID canónico del campeón seleccionado (ej. Lux).")
    display_name: str = Field(..., description="Nombre de visualización del campeón.")
    primary_role: str = Field(..., description="Rol primario del campeón.")
    title: str = Field(..., description="Título poético del campeón (ej. the Lady of Luminosity).")
    base_winrate: float = Field(..., description="Win Rate individual general del campeón.")
    synergies: list[DuoSynergyEntry] = Field(..., description="Lista ordenada de las mejores sinergias con junglas.")
