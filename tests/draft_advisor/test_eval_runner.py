import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from riot_lol_cli.draft_advisor.champion_data import ChampionDataService
from riot_lol_cli.draft_advisor.eval_runner import _build_draft_state, _check_assertions
from riot_lol_cli.draft_advisor.scoring import ScoringEngine

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_KB_ROOT = _PROJECT_ROOT / "data" / "draft_advisor" / "kb"


def load_golden_cases():
    golden_file = _KB_ROOT / "evals" / "golden_drafts.json"
    if not golden_file.exists():
        return []
    with open(golden_file, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("cases", [])


@pytest.fixture(scope="module")
def scoring_engine():
    data_service = ChampionDataService(_PROJECT_ROOT / "data" / "draft_advisor")
    data_service._adc_meta_snapshot["scraped_at"] = datetime.now(timezone.utc).isoformat()
    return ScoringEngine(data_service)


cases = load_golden_cases()


@pytest.mark.parametrize("case", cases, ids=[c.get("case_id", "unknown") for c in cases])
def test_golden_draft(case, scoring_engine):
    """Test a golden draft case using pytest."""
    draft_state = _build_draft_state(case["draft_state"])
    recommendation = scoring_engine.recommend(draft_state)

    failures = _check_assertions(case["case_id"], case["assertions"], recommendation)

    assert not failures, f"Failed assertions: {', '.join(failures)}"
