"""
Source registry — carga y valida `sources.json`.

Cada fuente del prompt se registra con metadata operativa:

- `id`: slug estable, único.
- `source_type`: categoría operativa (`SourceType`).
- `status`: `active` (V1 funcional) | `planned` (registry-only) | `gap`
  (intentamos pero falla persistente).
- `region_focus`: lista de regiones cubiertas (`["KR", "CN"]`, `["GLOBAL"]`).
- `requires_browser`: True si necesita Playwright (no XHR/JSON disponible).
- `scrape_priority`: 0-100, mayor = se intenta antes en pipeline.

El registry no decide nada por sí mismo; los pipelines lo consultan para
saber qué fuentes están operativas y cómo ranquearlas.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import ValidationError

from riot_lol_cli.jungle_research import json_storage
from riot_lol_cli.jungle_research.schemas import Source, SourceStatus, SourceType


class SourceRegistry:
    """Wrapper read-only sobre `sources.json` con accesores por filtro."""

    def __init__(self, sources: list[Source]):
        self._by_id: dict[str, Source] = {s.id: s for s in sources}

    @classmethod
    def load(cls) -> SourceRegistry:
        """Carga desde el archivo canónico. Lanza si hay schema inválido."""
        raw = json_storage.read_sources()
        validated: list[Source] = []
        errors: list[str] = []
        for entry in raw:
            try:
                validated.append(Source.model_validate(entry))
            except ValidationError as exc:
                errors.append(f"{entry.get('id', '?')}: {exc.error_count()} errors")
        if errors:
            raise ValueError(f"Sources inválidas: {'; '.join(errors)}")
        return cls(validated)

    def all(self) -> list[Source]:
        return list(self._by_id.values())

    def get(self, source_id: str) -> Source | None:
        return self._by_id.get(source_id)

    def by_type(self, source_type: SourceType) -> list[Source]:
        return [s for s in self._by_id.values() if s.source_type == source_type]

    def by_status(self, status: SourceStatus) -> list[Source]:
        return [s for s in self._by_id.values() if s.status == status]

    def active(self) -> list[Source]:
        return self.by_status(SourceStatus.ACTIVE)

    def planned(self) -> list[Source]:
        return self.by_status(SourceStatus.PLANNED)

    def gaps(self) -> list[Source]:
        return self.by_status(SourceStatus.GAP)

    def filter_active(self, source_ids: Iterable[str]) -> list[Source]:
        """Devuelve las fuentes solicitadas que están activas."""
        wanted = set(source_ids)
        return [
            s for s in self._by_id.values()
            if s.id in wanted and s.status == SourceStatus.ACTIVE
        ]

    def summary(self) -> dict[str, int]:
        """Conteo por estado para UI/overview."""
        out: dict[str, int] = {status.value: 0 for status in SourceStatus}
        for source in self._by_id.values():
            out[source.status.value] += 1
        out["total"] = len(self._by_id)
        return out
