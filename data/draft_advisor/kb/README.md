# Draft Advisor Knowledge Base

## Purpose

This knowledge base supports the ADC Pick Recommendation Assistant with curated research, patch analysis, matchup intelligence, and draft heuristics. It is designed to make the system smarter over time through **controlled, reviewable knowledge acquisition** — not through vague file accumulation.

## Architecture

```
kb/
├── taxonomy.json       # Controlled vocabulary (note types, confidence, topics, etc.)
├── manifest.json       # Source provenance registry
├── sources/            # Raw, unmodified source materials
│   ├── patch_notes/    # Scraped patch note JSONs
│   ├── pdf/            # Original PDFs
│   ├── web/            # Saved web exports
│   └── notes/          # Personal raw notes
├── research/           # Normalized markdown knowledge notes
│   ├── adcs/           # Per-ADC strategic research
│   ├── supports/       # Support synergy analysis
│   ├── threats/        # Enemy threat analysis
│   ├── archetypes/     # Comp archetype research
│   ├── matchups/       # Lane/game matchup notes
│   ├── patches/        # Patch impact analysis
│   ├── heuristics/     # Draft decision rules
│   └── meta/           # Meta snapshot summaries
├── structured/         # Derived structured data
│   ├── patch_overrides.json
│   ├── comp_archetypes.json
│   └── matchup_rules.json
├── evals/              # Golden draft cases + results
│   ├── golden_drafts.json
│   └── eval_results/
└── scripts/            # KB tooling
    ├── validate_kb.py
    └── ingest_scaffold.py
```

## Core Principles

1. **Raw sources are never edited.** Store originals in `sources/`.
2. **Research notes are human-reviewed markdown.** They live in `research/`.
3. **Structured data is the scoring source of truth.** Research informs it, never replaces it silently.
4. **Every source has provenance** tracked in `manifest.json`.
5. **Changes must pass golden draft evaluation** before merging into structured data.

## How to Add Knowledge

### Adding a research note

1. Create a `.md` file in the appropriate `research/` subfolder
2. Use the frontmatter schema (see any existing note as template)
3. Set `review_status: "draft"` initially
4. Run `python -m data.draft_advisor.kb.scripts.validate_kb` to check
5. Update `review_status: "reviewed"` after review

### Adding a raw source

1. Place the file in the appropriate `sources/` subfolder
2. Add an entry to `manifest.json` with source metadata
3. Normalize into one or more research notes
4. Link the notes in the manifest entry's `linked_research_notes`

### Proposing a structured update

1. Write the research note that justifies the change
2. Add the override/rule to the appropriate `structured/` file
3. Run `python -m riot_lol_cli.draft_advisor.eval_runner` to verify golden cases still pass
4. If any case fails, revise or reject the update

## Patch Format

All patch references must match the pattern `^\d+\.\d+$` (e.g., `16.7`).
Use `*` for patch-agnostic notes.
