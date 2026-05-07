from riot_lol_cli.draft_advisor.eval_runner import run_evaluation


def test_golden_drafts_regression_suite_passes():
    passed, total, _ = run_evaluation(save_results=False, force_fresh_adc_meta=True)

    assert total > 0
    assert passed == total
