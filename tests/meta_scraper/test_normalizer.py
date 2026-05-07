"""Tests para el normalizador del Meta Scraper."""

from riot_lol_cli.meta_scraper.normalizer import (
    _compute_climb_score,
    _compute_tier,
    merge_platform_data,
    normalize_champion_id,
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

        assert result["schema_version"] == "1.1"
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
        assert thresh["stats"]["win_rate"] == 51.5
        assert thresh["stats"]["pick_rate"] == 11.0
        assert thresh["stats"]["ban_rate"] == 7.0
        assert thresh["stats"]["games_analyzed"] == 180000

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
