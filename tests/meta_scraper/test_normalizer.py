"""Tests para el normalizador del Meta Scraper."""

import json

from riot_lol_cli.meta_scraper import normalizer
from riot_lol_cli.meta_scraper.normalizer import (
    MAX_GAMES_ANALYZED,
    _compute_climb_score,
    _compute_tier,
    merge_platform_data,
    normalize_champion_id,
    save_normalized,
)


class TestComputeTier:
    """Tests para el cálculo de tier."""

    def test_s_tier_high_wr_and_pr(self):
        assert _compute_tier(52.5, 10.0) == "S"

    def test_s_tier_very_high_wr(self):
        assert _compute_tier(54.0, 2.0) == "S"

    def test_a_tier(self):
        assert _compute_tier(51.5, 5.0) == "A"

    def test_b_tier(self):
        assert _compute_tier(49.5, 3.0) == "B"

    def test_c_tier(self):
        assert _compute_tier(47.0, 2.0) == "C"


class TestComputeClimbScore:
    """Tests para score de climb."""

    def test_high_wr_available_pick_scores_higher_than_banned_pick(self):
        strong_available = _compute_climb_score(52.5, 10.0, 4.0)
        strong_banned = _compute_climb_score(52.5, 10.0, 30.0)

        assert strong_available > strong_banned
        assert strong_available > 70


class TestNormalizeChampionId:
    """Tests para la normalización de nombres de campeones."""

    def test_exact_match(self):
        # Depende de champion_base.json existente
        result = normalize_champion_id("Thresh")
        # Debería devolver "Thresh" o el nombre raw
        assert result in ("Thresh", "thresh")

    def test_case_insensitive(self):
        result = normalize_champion_id("thresh")
        assert result.lower() == "thresh"

    def test_unknown_champion_returns_raw(self):
        result = normalize_champion_id("CampeónInventado")
        assert result == "CampeónInventado"


class TestMergePlatformData:
    """Tests para el merge de datos multi-plataforma."""

    def test_merge_single_platform(self):
        """Merge con una sola plataforma debería pasar los datos directamente."""
        data = {
            "lolalytics": {
                "patch": "16.8",
                "champions": [
                    {
                        "id": "Thresh",
                        "display_name": "Thresh",
                        "win_rate": 51.5,
                        "pick_rate": 12.0,
                        "ban_rate": 8.0,
                        "games_analyzed": 100000,
                    },
                    {
                        "id": "Janna",
                        "display_name": "Janna",
                        "win_rate": 53.2,
                        "pick_rate": 7.0,
                        "ban_rate": 3.0,
                        "games_analyzed": 50000,
                    },
                ],
            }
        }

        result = merge_platform_data(data)

        assert result["schema_version"] == "1.2"
        assert result["patch"] == "16.8"
        assert result["role"] == "support"
        assert result["champion_count"] == 2
        assert len(result["champions"]) == 2

        # Verificar que Janna está primero (S tier, mayor WR)
        janna = next(c for c in result["champions"] if "Janna" in c["id"])
        assert janna["stats"]["win_rate"] == 53.2
        assert janna["stats"]["tier"] == "S"

    def test_merge_two_platforms_averages(self):
        """Merge con dos plataformas debe promediar WR/PR/BR."""
        data = {
            "lolalytics": {
                "patch": "16.8",
                "champions": [
                    {
                        "id": "Thresh",
                        "display_name": "Thresh",
                        "win_rate": 51.0,
                        "pick_rate": 12.0,
                        "ban_rate": 8.0,
                        "games_analyzed": 100000,
                    },
                ],
            },
            "opgg": {
                "patch": "16.8",
                "champions": [
                    {
                        "id": "Thresh",
                        "display_name": "Thresh",
                        "win_rate": 52.0,
                        "pick_rate": 10.0,
                        "ban_rate": 6.0,
                        "games_analyzed": 80000,
                    },
                ],
            },
        }

        result = merge_platform_data(data)

        thresh = result["champions"][0]
        assert thresh["stats"]["win_rate"] == 51.44
        assert thresh["stats"]["pick_rate"] == 11.11
        assert thresh["stats"]["ban_rate"] == 7.11
        assert thresh["stats"]["games_analyzed"] == 180000
        assert result["aggregation"]["method"] == "games_weighted_average_v1"

        # Source breakdown debe tener ambas
        assert "lolalytics" in thresh["source_breakdown"]
        assert "opgg" in thresh["source_breakdown"]

    def test_merge_empty(self):
        """Merge sin datos no debe fallar."""
        result = merge_platform_data({})
        assert result["champions"] == []
        assert result["champion_count"] == 0

    def test_merge_adc_role_sorts_by_climb_score(self):
        """ADC se ordena por climb_score para picks de climb."""
        data = {
            "opgg": {
                "patch": "16.8",
                "champions": [
                    {
                        "id": "Aphelios",
                        "display_name": "Aphelios",
                        "win_rate": 51.0,
                        "pick_rate": 5.0,
                        "ban_rate": 2.0,
                        "games_analyzed": 10000,
                    },
                    {
                        "id": "Jinx",
                        "display_name": "Jinx",
                        "win_rate": 52.5,
                        "pick_rate": 9.0,
                        "ban_rate": 3.0,
                        "games_analyzed": 20000,
                    },
                ],
            }
        }

        result = merge_platform_data(data, role="adc")

        assert result["role"] == "adc"
        assert result["champions"][0]["id"] == "Jinx"
        assert result["champions"][0]["stats"]["climb_score"] > result["champions"][1]["stats"]["climb_score"]

    def test_merge_jungle_role_with_source_gaps(self):
        data = {
            "ugg": {
                "patch": "26.9",
                "role": "jungle",
                "champions": [
                    {
                        "id": "XinZhao",
                        "display_name": "Xin Zhao",
                        "win_rate": 52.0,
                        "pick_rate": 9.0,
                        "ban_rate": 6.0,
                        "games_analyzed": 120000,
                    },
                ],
            }
        }
        gaps = [
            {
                "source": "opgg",
                "stage": "adapter_fetch",
                "reason": "403 bloqueado",
                "attempted_at": "2026-05-09T10:00:00+00:00",
            }
        ]

        result = merge_platform_data(data, role="jungle", source_gaps=gaps)

        assert result["role"] == "jungle"
        assert result["source_gaps"] == gaps
        assert result["source_status"][0]["source"] == "ugg"
        assert result["source_status"][0]["status"] == "ok"
        assert result["source_status"][1]["source"] == "opgg"
        assert result["source_status"][1]["status"] == "gap"

    def test_merge_uses_source_average_when_no_games(self):
        data = {
            "lolalytics": {
                "patch": "26.9",
                "champions": [{"id": "Nocturne", "win_rate": 52.0, "pick_rate": 8.0, "ban_rate": 5.0}],
            },
            "opgg": {
                "patch": "26.9",
                "champions": [{"id": "Nocturne", "win_rate": 54.0, "pick_rate": 6.0, "ban_rate": 7.0}],
            },
        }

        result = merge_platform_data(data, role="jungle")
        nocturne = result["champions"][0]

        assert nocturne["stats"]["win_rate"] == 53.0
        assert nocturne["stats"]["pick_rate"] == 7.0
        assert nocturne["stats"]["games_analyzed"] == 0
        assert result["aggregation"]["fallback"] == "source_average_no_games"

    def test_source_without_games_stays_in_breakdown_but_not_weighted_average(self):
        data = {
            "ugg": {
                "patch": "26.9",
                "champions": [
                    {"id": "LeeSin", "win_rate": 52.0, "pick_rate": 10.0, "ban_rate": 8.0, "games_analyzed": 100}
                ],
            },
            "opgg": {
                "patch": "26.9",
                "champions": [
                    {"id": "LeeSin", "win_rate": 60.0, "pick_rate": 20.0, "ban_rate": 1.0, "games_analyzed": 0}
                ],
            },
        }

        result = merge_platform_data(data, role="jungle")
        lee_sin = result["champions"][0]

        assert lee_sin["stats"]["win_rate"] == 52.0
        assert lee_sin["stats"]["pick_rate"] == 10.0
        assert lee_sin["stats"]["games_analyzed"] == 100
        assert "opgg" in lee_sin["source_breakdown"]
        assert "no en el promedio ponderado" in lee_sin["stats"]["aggregation_note"]

    def test_jungle_role_filters_cross_role_contamination(self):
        data = {
            "ugg": {
                "patch": "26.9",
                "role": "jungle",
                "champions": [
                    {"id": "Smolder", "win_rate": 53.5, "pick_rate": 17.0, "ban_rate": 10.0, "games_analyzed": 200000},
                    {"id": "XinZhao", "win_rate": 52.0, "pick_rate": 9.0, "ban_rate": 6.0, "games_analyzed": 120000},
                ],
            }
        }

        result = merge_platform_data(data, role="jungle")
        champion_ids = {champ["id"] for champ in result["champions"]}

        assert "XinZhao" in champion_ids
        assert "Smolder" not in champion_ids
        assert result["source_gaps"][0]["stage"] == "normalization_role_filter"
        assert "filtrados" in result["source_gaps"][0]["reason"]

    def test_games_above_sane_limit_stay_in_breakdown_but_not_weighted(self):
        data = {
            "lolalytics": {
                "patch": "26.9",
                "role": "jungle",
                "champions": [
                    {
                        "id": "Shyvana",
                        "win_rate": 53.0,
                        "pick_rate": 6.0,
                        "ban_rate": 8.0,
                        "games_analyzed": MAX_GAMES_ANALYZED + 1,
                    }
                ],
            },
            "ugg": {
                "patch": "26.9",
                "role": "jungle",
                "champions": [
                    {"id": "Shyvana", "win_rate": 52.0, "pick_rate": 5.0, "ban_rate": 7.0, "games_analyzed": 100000}
                ],
            },
        }

        result = merge_platform_data(data, role="jungle")
        shyvana = result["champions"][0]

        assert shyvana["stats"]["win_rate"] == 52.0
        assert shyvana["stats"]["games_analyzed"] == 100000
        assert shyvana["source_breakdown"]["lolalytics"]["games_analyzed"] == 0
        assert any(gap["stage"] == "normalization_games_filter" for gap in result["source_gaps"])

    def test_save_normalized_backs_up_previous_jungle_latest(self, tmp_path, monkeypatch):
        monkeypatch.setattr(normalizer, "_DATA_DIR", tmp_path)
        latest_dir = tmp_path / "normalized"
        latest_dir.mkdir(parents=True)
        latest_path = latest_dir / "latest_jungle_tier.json"
        latest_path.write_text('{"old": true}', encoding="utf-8")

        save_normalized({"role": "jungle", "champions": []}, role="jungle")

        backups = list((latest_dir / "backups" / "jungle").glob("latest_jungle_tier_*.json"))
        assert len(backups) == 1
        assert json.loads(backups[0].read_text(encoding="utf-8")) == {"old": True}
