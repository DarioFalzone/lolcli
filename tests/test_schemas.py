"""Tests para los modelos Pydantic de Riot Match-V5."""

from riot_lol_cli.schemas.riot_api import (
    MatchDto,
    ProcessedMatch,
)


def _make_raw_match(match_id: str = "LA2_1234") -> dict:
    """Genera un dict crudo mínimo que simula una respuesta de Match-V5."""
    return {
        "metadata": {
            "dataVersion": "2",
            "matchId": match_id,
            "participants": ["puuid1"],
        },
        "info": {
            "gameCreation": 1700000000000,
            "gameCreationTime": 1700000000000,
            "gameDuration": 1800,
            "gameType": "MATCHED_GAME",
            "queueId": 420,
            "platformId": "LA2",
            "participants": [
                {
                    "puuid": "puuid1",
                    "summonerName": "TestPlayer",
                    "championId": 51,
                    "championName": "Caitlyn",
                    "champLevel": 15,
                    "teamId": 100,
                    "win": True,
                    "kills": 8,
                    "deaths": 2,
                    "assists": 5,
                    "totalMinionsKilled": 200,
                    "neutralMinionsKilled": 20,
                    "goldEarned": 14000,
                    "totalDamageDealtToChampions": 25000,
                    "totalDamageTaken": 12000,
                    "visionScore": 30,
                    "item0": 3031,
                    "item1": 3094,
                    "item2": 3006,
                    "item3": 3036,
                    "item4": 0,
                    "item5": 0,
                    "item6": 3340,
                    "perks": {
                        "statPerks": {"defense": 5002},
                        "styles": [
                            {
                                "description": "primaryStyle",
                                "selections": [{"perk": 8005, "var1": 1, "var2": 0, "var3": 0}],
                                "style": 8000,
                            },
                            {
                                "description": "subStyle",
                                "selections": [],
                                "style": 8200,
                            },
                        ],
                    },
                    "role": "CARRY",
                    "lane": "BOTTOM",
                    "individualPosition": "BOTTOM",
                    "teamPosition": "BOTTOM",
                }
            ],
        },
    }


class TestMatchDto:
    def test_parse_minimal(self):
        raw = _make_raw_match()
        match = MatchDto.model_validate(raw)
        assert match.metadata.match_id == "LA2_1234"
        assert match.info.game_duration == 1800
        assert len(match.info.participants) == 1

    def test_participant_properties(self):
        raw = _make_raw_match()
        match = MatchDto.model_validate(raw)
        p = match.info.participants[0]

        assert p.champion_name == "Caitlyn"
        assert p.cs == 220  # 200 + 20
        assert p.primary_rune == 8005
        assert p.secondary_style == 8200
        assert len(p.items_list) == 7
        assert p.items_list[6] == 3340  # trinket

    def test_extra_fields_allowed(self):
        """Riot puede agregar fields nuevos; no deben romper el parser."""
        raw = _make_raw_match()
        raw["info"]["newRiotField"] = "surprise"
        raw["info"]["participants"][0]["experimentalMetric"] = 42

        match = MatchDto.model_validate(raw)
        assert match.info.game_duration == 1800

    def test_missing_perks_falls_back(self):
        raw = _make_raw_match()
        raw["info"]["participants"][0]["perks"] = {}

        match = MatchDto.model_validate(raw)
        p = match.info.participants[0]
        assert p.primary_rune == 0
        assert p.secondary_style == 0


class TestProcessedMatch:
    def test_from_match_dto(self):
        raw = _make_raw_match("LA2_5678")
        match_dto = MatchDto.model_validate(raw)

        processed = ProcessedMatch.from_match_dto(match_dto, "LA2_5678")
        assert processed.match_id == "LA2_5678"
        assert processed.duration == 1800
        assert len(processed.champions) == 1

        champ = processed.champions[0]
        assert champ.champion_name == "Caitlyn"
        assert champ.result is True
        assert champ.stats.kills == 8
        assert champ.stats.cs == 220
        assert champ.runes.primary == 8005
        assert champ.runes.secondary == 8200

    def test_serialization_roundtrip(self):
        raw = _make_raw_match()
        match_dto = MatchDto.model_validate(raw)
        processed = ProcessedMatch.from_match_dto(match_dto, "LA2_1234")

        # model_dump() must produce a clean, JSON-serializable dict
        data = processed.model_dump()
        assert isinstance(data, dict)
        assert data["match_id"] == "LA2_1234"
        assert data["champions"][0]["stats"]["kills"] == 8
