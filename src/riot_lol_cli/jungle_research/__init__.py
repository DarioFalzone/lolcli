"""
Jungle Research — base de conocimiento del meta de jungla.

Capa que vive dentro de Meta Analyzer (`:8000`) y consolida múltiples fuentes
en un score de consenso por campeón. Reusa Meta Scraper (:8002) y Jungle Meta
(:8003) como fuentes activas; el resto del registry queda como `planned` con
gaps visibles.

Convenciones canónicas:

- Todo dato lleva `source_url`, `extracted_at`, `patch`, `region`, `elo`,
  `queue` y `role` cuando aplica.
- Snapshots son inmutables: `latest.json` se rota a `backups/` antes de pisar.
- Riot API se usa solo si `RIOT_API_KEY` está presente; de lo contrario, el
  pipeline registra un gap controlado en lugar de inventar datos.

Storage v1 = JSON versionado bajo `data/meta_analyzer/jungle_research/`.
Migración futura a SQLite/PostgreSQL queda preparada por nombres de campos
compatibles en `schemas`.
"""

from __future__ import annotations
