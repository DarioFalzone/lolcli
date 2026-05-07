"""
Modelos Pydantic V2 para las respuestas de Riot Match-V5.

Uso:
    from riot_lol_cli.schemas.riot_api import MatchDto
    match = MatchDto.model_validate(raw_dict)
    # acceso tipado y seguro:
    info = match.info
    for p in info.participants:
        print(p.champion_name, p.kills, p.deaths, p.assists)

Notas:
- Todos los campos que la API de Riot puede omitir llevan defaults seguros.
- extra="allow" evita que un field nuevo de la API rompa el parseo.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Participant → Perks
# ---------------------------------------------------------------------------


class PerkSelection(BaseModel, extra="allow"):
    perk: int = 0
    var1: int = 0
    var2: int = 0
    var3: int = 0


class PerkStyle(BaseModel, extra="allow"):
    description: str = ""
    selections: list[PerkSelection] = Field(default_factory=list)
    style: int = 0


class Perks(BaseModel, extra="allow"):
    stat_perks: dict[str, int] = Field(default_factory=dict, alias="statPerks")
    styles: list[PerkStyle] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Participant
# ---------------------------------------------------------------------------


class ParticipantDto(BaseModel, extra="allow"):
    """Datos de un jugador dentro de un match."""

    puuid: str = ""
    summoner_name: str = Field(default="", alias="summonerName")
    champion_id: int = Field(default=0, alias="championId")
    champion_name: str = Field(default="", alias="championName")
    champ_level: int = Field(default=0, alias="champLevel")
    team_id: int = Field(default=0, alias="teamId")
    win: bool = False

    # KDA
    kills: int = 0
    deaths: int = 0
    assists: int = 0

    # Farming / Gold
    total_minions_killed: int = Field(default=0, alias="totalMinionsKilled")
    neutral_minions_killed: int = Field(default=0, alias="neutralMinionsKilled")
    gold_earned: int = Field(default=0, alias="goldEarned")

    # Damage
    total_damage_dealt_to_champions: int = Field(default=0, alias="totalDamageDealtToChampions")
    total_damage_taken: int = Field(default=0, alias="totalDamageTaken")

    # Vision
    vision_score: int = Field(default=0, alias="visionScore")

    # Items (0 = empty)
    item0: int = 0
    item1: int = 0
    item2: int = 0
    item3: int = 0
    item4: int = 0
    item5: int = 0
    item6: int = 0  # trinket

    # Perks
    perks: Perks = Field(default_factory=Perks)

    # Role / Lane (Riot no siempre los manda)
    role: str = "UNKNOWN"
    lane: str = "UNKNOWN"
    individual_position: str = Field(default="", alias="individualPosition")
    team_position: str = Field(default="", alias="teamPosition")

    # Convenience
    @property
    def cs(self) -> int:
        return self.total_minions_killed + self.neutral_minions_killed

    @property
    def items_list(self) -> list[int]:
        return [self.item0, self.item1, self.item2, self.item3, self.item4, self.item5, self.item6]

    @property
    def primary_rune(self) -> int:
        """Keystone del estilo primario."""
        if self.perks.styles and self.perks.styles[0].selections:
            return self.perks.styles[0].selections[0].perk
        return 0

    @property
    def secondary_style(self) -> int:
        """ID del estilo secundario de runas."""
        if len(self.perks.styles) > 1:
            return self.perks.styles[1].style
        return 0


# ---------------------------------------------------------------------------
# Match Info
# ---------------------------------------------------------------------------


class MatchInfoDto(BaseModel, extra="allow"):
    game_creation: int = Field(default=0, alias="gameCreation")
    game_creation_time: int = Field(default=0, alias="gameCreationTime")
    game_duration: int = Field(default=0, alias="gameDuration")
    game_type: str = Field(default="", alias="gameType")
    queue_id: int = Field(default=0, alias="queueId")
    platform_id: str = Field(default="", alias="platformId")
    participants: list[ParticipantDto] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Top-level Match
# ---------------------------------------------------------------------------


class MatchMetadataDto(BaseModel, extra="allow"):
    data_version: str = Field(default="", alias="dataVersion")
    match_id: str = Field(default="", alias="matchId")
    participants: list[str] = Field(default_factory=list)


class MatchDto(BaseModel, extra="allow"):
    """Modelo completo de un match de Riot Match-V5."""

    metadata: MatchMetadataDto = Field(default_factory=MatchMetadataDto)
    info: MatchInfoDto = Field(default_factory=MatchInfoDto)


# ---------------------------------------------------------------------------
# Processed match (salida del data collector)
# ---------------------------------------------------------------------------


class ChampionStats(BaseModel):
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    damage_champions: int = 0
    damage_taken: int = 0
    gold: int = 0
    cs: int = 0
    vision: int = 0
    level: int = 0


class ChampionRunes(BaseModel):
    primary: int = 0
    secondary: int = 0


class ProcessedChampion(BaseModel):
    champion_id: int = 0
    champion_name: str = ""
    role: str = "UNKNOWN"
    lane: str = "UNKNOWN"
    team: int = 0
    result: bool = False
    items: list[int] = Field(default_factory=list)
    runes: ChampionRunes = Field(default_factory=ChampionRunes)
    stats: ChampionStats = Field(default_factory=ChampionStats)


class ProcessedMatch(BaseModel):
    match_id: str = ""
    timestamp: int = 0
    duration: int = 0
    game_type: str = ""
    queue_id: int = 0
    champions: list[ProcessedChampion] = Field(default_factory=list)

    @classmethod
    def from_match_dto(cls, match: MatchDto, match_id: str) -> ProcessedMatch:
        """Convierte un MatchDto crudo en la estructura procesada."""
        info = match.info
        champions = []
        for p in info.participants:
            champions.append(
                ProcessedChampion(
                    champion_id=p.champion_id,
                    champion_name=p.champion_name,
                    role=p.role,
                    lane=p.lane,
                    team=p.team_id,
                    result=p.win,
                    items=p.items_list,
                    runes=ChampionRunes(
                        primary=p.primary_rune,
                        secondary=p.secondary_style,
                    ),
                    stats=ChampionStats(
                        kills=p.kills,
                        deaths=p.deaths,
                        assists=p.assists,
                        damage_champions=p.total_damage_dealt_to_champions,
                        damage_taken=p.total_damage_taken,
                        gold=p.gold_earned,
                        cs=p.cs,
                        vision=p.vision_score,
                        level=p.champ_level,
                    ),
                )
            )

        return cls(
            match_id=match_id,
            timestamp=info.game_creation_time // 1000 if info.game_creation_time else 0,
            duration=info.game_duration,
            game_type=info.game_type,
            queue_id=info.queue_id,
            champions=champions,
        )
