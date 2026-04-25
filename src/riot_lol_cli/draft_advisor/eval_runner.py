"""
Evaluation Runner — Golden Draft Case Regression Testing.

Loads golden_drafts.json, runs each draft through the scoring engine,
and checks assertion constraints. Outputs pass/fail per case.

Usage:
    python -m riot_lol_cli.draft_advisor.eval_runner
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .schemas import DraftState, RecommendationOutput

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Setup paths
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_KB_ROOT = _PROJECT_ROOT / "data" / "draft_advisor" / "kb"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _build_draft_state(case_draft: dict) -> DraftState:
    """Convert a golden case draft_state dict into a DraftState model."""
    from .schemas import (
        DraftChampion,
        DraftContext,
        DraftState,
        InformationLevel,
        PickPosition,
        PoolMode,
        QueueType,
        UserPool,
    )

    allies = [DraftChampion(**a) for a in case_draft.get("allies", [])]
    enemies = [DraftChampion(**e) for e in case_draft.get("enemies", [])]
    bans = case_draft.get("bans", [])

    ctx_data = case_draft.get("context", {})
    context = DraftContext(
        pick_position=PickPosition(ctx_data.get("pick_position", "blind")),
        information_level=InformationLevel(ctx_data.get("information_level", "none")),
        queue_type=QueueType(ctx_data.get("queue_type", "ranked_solo")),
    )

    pool_data = case_draft.get("user_pool") or {}
    user_pool = UserPool(
        mode=PoolMode(pool_data.get("mode", "unrestricted")),
        champions=pool_data.get("champions", []),
        comfort={k: int(v) for k, v in pool_data.get("comfort", {}).items()},
    )

    return DraftState(
        allies=allies,
        enemies=enemies,
        bans=bans,
        context=context,
        user_pool=user_pool,
    )


def _check_assertions(
    case_id: str,
    assertions: dict,
    result: RecommendationOutput,
) -> list[str]:
    """
    Check assertion constraints against a recommendation result.
    Returns a list of failure messages (empty = all passed).
    """
    failures: list[str] = []
    top_id = result.top_pick.id
    top_score = result.top_pick.total_score

    # top_pick_must_be_one_of
    allowed = assertions.get("top_pick_must_be_one_of", [])
    if allowed and top_id not in allowed:
        failures.append(
            f"Top pick '{top_id}' not in allowed set {allowed}"
        )

    # top_3_must_include_any_of
    must_include = assertions.get("top_3_must_include_any_of", [])
    if must_include:
        top_3_ids = [top_id] + [a.id for a in result.alternatives[:2]]
        if not any(c in top_3_ids for c in must_include):
            failures.append(
                f"Top 3 {top_3_ids} must include at least one of {must_include}"
            )

    # must_not_recommend_as_top
    must_not = assertions.get("must_not_recommend_as_top", [])
    if top_id in must_not:
        failures.append(
            f"Top pick '{top_id}' is in must_not_recommend set {must_not}"
        )

    # top_pick_score_min
    score_min = assertions.get("top_pick_score_min")
    if score_min is not None and top_score < score_min:
        failures.append(
            f"Top pick score {top_score:.1f} < minimum {score_min}"
        )

    # total_candidates_max
    cand_max = assertions.get("total_candidates_max")
    if cand_max is not None:
        total = 1 + len(result.alternatives)
        if total > cand_max:
            failures.append(
                f"Total candidates {total} exceeds max {cand_max}"
            )

    return failures


def run_evaluation(
    golden_file: Path = _KB_ROOT / "evals" / "golden_drafts.json",
    save_results: bool = True,
) -> tuple[int, int, list[dict]]:
    """
    Run all golden draft cases.

    Returns:
        (passed_count, total_count, detailed_results)
    """
    from .champion_data import ChampionDataService
    from .scoring import ScoringEngine

    # Load golden cases
    with open(golden_file, encoding="utf-8") as f:
        golden_data = json.load(f)

    cases = golden_data["cases"]
    logger.info(f"Loaded {len(cases)} golden draft cases")

    # Init engine
    data_service = ChampionDataService(_PROJECT_ROOT / "data" / "draft_advisor")
    engine = ScoringEngine(data_service)

    results: list[dict] = []
    passed = 0

    for case in cases:
        case_id = case["case_id"]
        description = case["description"]

        logger.info(f"--- Running: {case_id} ---")
        logger.info(f"    {description}")

        try:
            draft_state = _build_draft_state(case["draft_state"])
            recommendation = engine.recommend(draft_state)

            failures = _check_assertions(
                case_id, case["assertions"], recommendation
            )

            if failures:
                status = "FAIL"
                for f in failures:
                    logger.error(f"  FAIL: {f}")
            else:
                status = "PASS"
                passed += 1
                logger.info(f"  PASS (top: {recommendation.top_pick.id}, "
                           f"score: {recommendation.top_pick.total_score:.1f})")

            results.append({
                "case_id": case_id,
                "description": description,
                "status": status,
                "top_pick": recommendation.top_pick.id,
                "top_score": recommendation.top_pick.total_score,
                "alternatives": [a.id for a in recommendation.alternatives],
                "failures": failures,
            })

        except Exception as e:
            logger.error(f"  ERROR: {e}")
            results.append({
                "case_id": case_id,
                "description": description,
                "status": "ERROR",
                "error": str(e),
                "failures": [str(e)],
            })

    total = len(cases)
    logger.info(f"\n{'='*50}")
    logger.info(f"RESULTS: {passed}/{total} passed")
    logger.info(f"{'='*50}")

    # Save results
    if save_results:
        results_dir = _KB_ROOT / "evals" / "eval_results"
        results_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        result_file = results_dir / f"eval_{ts}.json"

        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "golden_file": str(golden_file),
            "total_cases": total,
            "passed": passed,
            "failed": total - passed,
            "results": results,
        }

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {result_file}")

    return passed, total, results


def main():
    """CLI entry point."""
    passed, total, _ = run_evaluation()
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
