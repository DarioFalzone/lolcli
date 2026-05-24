"""Read-only source registry for Esports Research."""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import ValidationError

from riot_lol_cli.esports_research import json_storage
from riot_lol_cli.esports_research.schemas import Source, SourceStatus, SourceType


class SourceRegistry:
    """Wrapper over `data/esports_research/sources.json` with filters."""

    def __init__(self, sources: list[Source]):
        self._by_id: dict[str, Source] = {source.id: source for source in sources}

    @classmethod
    def load(cls) -> SourceRegistry:
        raw = json_storage.read_sources()
        validated: list[Source] = []
        errors: list[str] = []
        for entry in raw:
            try:
                validated.append(Source.model_validate(entry))
            except ValidationError as exc:
                errors.append(f"{entry.get('id', '?')}: {exc.error_count()} errors")
        if errors:
            raise ValueError(f"Invalid esports sources: {'; '.join(errors)}")
        return cls(validated)

    def all(self) -> list[Source]:
        return list(self._by_id.values())

    def get(self, source_id: str) -> Source | None:
        return self._by_id.get(source_id)

    def by_type(self, source_type: SourceType) -> list[Source]:
        return [source for source in self._by_id.values() if source.source_type == source_type]

    def by_status(self, status: SourceStatus) -> list[Source]:
        return [source for source in self._by_id.values() if source.status == status]

    def active(self) -> list[Source]:
        return self.by_status(SourceStatus.ACTIVE)

    def stubs(self) -> list[Source]:
        return self.by_status(SourceStatus.STUB)

    def planned(self) -> list[Source]:
        return self.by_status(SourceStatus.PLANNED)

    def restricted(self) -> list[Source]:
        return self.by_status(SourceStatus.RESTRICTED)

    def filter_active(self, source_ids: Iterable[str]) -> list[Source]:
        wanted = set(source_ids)
        return [
            source
            for source in self._by_id.values()
            if source.id in wanted and source.status == SourceStatus.ACTIVE
        ]

    def summary(self) -> dict[str, int]:
        out = {status.value: 0 for status in SourceStatus}
        for source in self._by_id.values():
            out[source.status.value] += 1
        out["total"] = len(self._by_id)
        return out
