"""
Knowledge Base Retriever — Stage 1: Filesystem + Metadata Filtering.

Scans the research/ directory, parses YAML frontmatter from markdown notes,
and returns relevant notes based on champion/topic/patch/confidence filtering.

No vector DB, no embeddings — just fast metadata-based retrieval
suitable for a corpus of <200 notes.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .kb_schemas import ConfidenceLevel, ResearchNoteMeta, ReviewStatus

logger = logging.getLogger(__name__)

# Confidence ranking for comparison
_CONFIDENCE_RANK = {
    ConfidenceLevel.HIGH: 4,
    ConfidenceLevel.MEDIUM: 3,
    ConfidenceLevel.LOW: 2,
    ConfidenceLevel.SPECULATIVE: 1,
}


@dataclass
class RetrievedNote:
    """A research note retrieved by the KB retriever."""

    meta: ResearchNoteMeta
    file_path: Path
    body: str
    relevance_score: float = 0.0


@dataclass
class RetrievalQuery:
    """Query parameters for knowledge retrieval."""

    champions: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    patch: str = "*"
    max_results: int = 5
    min_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    only_reviewed: bool = True
    note_types: list[str] | None = None  # Filter by specific note types


class KnowledgeRetriever:
    """
    Stage 1 retriever: scans markdown files, parses frontmatter,
    filters and ranks by metadata relevance.
    """

    def __init__(self, kb_root: Path):
        """
        Args:
            kb_root: Path to the kb/ directory (e.g., data/draft_advisor/kb/).
        """
        self._kb_root = kb_root
        self._research_dir = kb_root / "research"
        self._cache: list[tuple[ResearchNoteMeta, Path]] | None = None

    def retrieve(self, query: RetrievalQuery) -> list[RetrievedNote]:
        """
        Retrieve relevant research notes based on query parameters.

        Ranking formula:
            relevance = champion_overlap * 3 + topic_overlap * 2 + confidence_bonus

        Args:
            query: Retrieval parameters.

        Returns:
            List of RetrievedNote sorted by relevance_score descending.
        """
        all_notes = self._scan_notes()
        results: list[RetrievedNote] = []

        query_champions = set(c.lower() for c in query.champions)
        query_topics = set(t.lower() for t in query.topics)
        min_conf_rank = _CONFIDENCE_RANK.get(query.min_confidence, 0)

        for meta, filepath in all_notes:
            # --- Filters ---

            # Review status filter
            if query.only_reviewed and meta.review_status != ReviewStatus.REVIEWED:
                continue

            # Superseded filter — skip superseded notes
            if meta.review_status == ReviewStatus.SUPERSEDED:
                continue

            # Confidence filter
            conf_rank = _CONFIDENCE_RANK.get(meta.confidence, 0)
            if conf_rank < min_conf_rank:
                continue

            # Patch filter
            if query.patch != "*" and meta.patch != "*" and meta.patch != query.patch:
                continue

            # Note type filter
            if query.note_types and meta.type.value not in query.note_types:
                continue

            # --- Relevance scoring ---
            note_champions = set(c.lower() for c in meta.champions)
            note_topics = set(t.lower() for t in meta.topics)

            champion_overlap = len(query_champions & note_champions)
            topic_overlap = len(query_topics & note_topics)

            # Must have at least one overlap to be considered
            if champion_overlap == 0 and topic_overlap == 0:
                continue

            confidence_bonus = conf_rank * 0.5
            relevance = champion_overlap * 3.0 + topic_overlap * 2.0 + confidence_bonus

            # Read the note body
            try:
                body = self._read_body(filepath)
            except Exception as e:
                logger.warning(f"Failed to read body of {filepath}: {e}")
                body = ""

            results.append(RetrievedNote(
                meta=meta,
                file_path=filepath,
                body=body,
                relevance_score=relevance,
            ))

        # Sort by relevance descending
        results.sort(key=lambda r: r.relevance_score, reverse=True)

        return results[:query.max_results]

    def get_note_by_id(self, note_id: str) -> RetrievedNote | None:
        """Retrieve a specific note by its ID."""
        all_notes = self._scan_notes()
        for meta, filepath in all_notes:
            if meta.id == note_id:
                body = self._read_body(filepath)
                return RetrievedNote(meta=meta, file_path=filepath, body=body)
        return None

    def list_all_notes(self) -> list[ResearchNoteMeta]:
        """List metadata for all parseable research notes."""
        return [meta for meta, _ in self._scan_notes()]

    def invalidate_cache(self) -> None:
        """Force re-scan of the research directory."""
        self._cache = None

    # ========================================================================
    # Internal
    # ========================================================================

    def _scan_notes(self) -> list[tuple[ResearchNoteMeta, Path]]:
        """Scan all .md files in research/ and parse their frontmatter."""
        if self._cache is not None:
            return self._cache

        notes: list[tuple[ResearchNoteMeta, Path]] = []

        if not self._research_dir.exists():
            logger.warning(f"Research directory not found: {self._research_dir}")
            return notes

        for md_file in self._research_dir.rglob("*.md"):
            try:
                meta = self._parse_frontmatter(md_file)
                if meta is not None:
                    notes.append((meta, md_file))
            except Exception as e:
                logger.warning(f"Failed to parse frontmatter in {md_file}: {e}")

        self._cache = notes
        logger.info(f"KB retriever: scanned {len(notes)} research notes")
        return notes

    def _parse_frontmatter(self, filepath: Path) -> ResearchNoteMeta | None:
        """Parse YAML frontmatter from a markdown file."""
        text = filepath.read_text(encoding="utf-8")

        if not text.startswith("---"):
            return None

        # Find closing ---
        end_idx = text.find("---", 3)
        if end_idx == -1:
            return None

        yaml_text = text[3:end_idx].strip()
        data = yaml.safe_load(yaml_text)

        if not isinstance(data, dict):
            return None

        return ResearchNoteMeta(**data)

    def _read_body(self, filepath: Path) -> str:
        """Read the markdown body (after frontmatter) from a file."""
        text = filepath.read_text(encoding="utf-8")

        if text.startswith("---"):
            end_idx = text.find("---", 3)
            if end_idx != -1:
                return text[end_idx + 3:].strip()

        return text.strip()
