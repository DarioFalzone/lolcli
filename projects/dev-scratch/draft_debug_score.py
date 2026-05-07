from riot_lol_cli.draft_advisor.champion_data import ChampionDataService
from riot_lol_cli.draft_advisor.schemas import DraftChampion, DraftContext, DraftState, UserPool
from riot_lol_cli.draft_advisor.scoring import ScoringEngine

engine = ScoringEngine(ChampionDataService())
draft = DraftState(
    allies=[DraftChampion(id="Jinx"), DraftChampion(id="Maokai"), DraftChampion(id="Syndra")],
    enemies=[DraftChampion(id="Rakan"), DraftChampion(id="LeeSin"), DraftChampion(id="Lucian")],
    target_role="support",
    context=DraftContext(pick_position="late", queue_type="ranked_solo"),
    user_pool=UserPool(mode="unrestricted"),
)
res = engine.recommend(draft)
for p in [res.top_pick] + res.alternatives[:4]:
    print(f"{p.id}: {p.total_score:.1f}")
    print("  RAW: " + str({k: round(v, 1) for k, v in p.score_breakdown.raw.items()}))
    print("  WGT: " + str({k: round(v, 1) for k, v in p.score_breakdown.weighted.items()}))
