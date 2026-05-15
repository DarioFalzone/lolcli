"""Búsqueda full-text simple sobre los patch notes persistidos.

Sin dependencias adicionales (no Whoosh, no SQLite). Construye un índice
in-memory al startup y permite reconstruir tras cada scrape. Suficiente
para ~100 parches × ~20 secciones por parche.

Algoritmo:
- Tokenización: lowercase + sin acentos + sin puntuación, split por whitespace.
- Indexación: dict[token] → list[Posting]. Posting referencia patch+locale+section+block.
- Query: AND de tokens (cada token debe aparecer), ranking por suma de TF normalizado.
- Snippet: ±60 chars alrededor de la primera ocurrencia del primer token.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from .loader import _read_patch_file
from .normalizer import _version_sort_key, get_data_dir
from .schema import PatchSection, SearchHit

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_MIN_TOKEN_LEN = 2
_SNIPPET_RADIUS = 80
# Stop words mínimas en español/inglés — útiles para evitar matches inútiles.
_STOPWORDS = frozenset(
    {
        "de",
        "la",
        "el",
        "los",
        "las",
        "un",
        "una",
        "y",
        "o",
        "a",
        "en",
        "que",
        "con",
        "por",
        "para",
        "the",
        "of",
        "and",
        "to",
        "in",
        "is",
        "for",
        "on",
        "with",
    }
)


@dataclass
class _Posting:
    patch_version: str
    source_locale: str
    section_path: list[str]
    block_text: str
    section_anchor: str
    token_count: int  # tokens del bloque, para TF normalizado


@dataclass
class SearchIndex:
    """Índice in-memory con dos diccionarios.

    `postings[token]` mapea a la lista de bloques donde aparece.
    `doc_count` registra cuántos bloques hay en total (para IDF aproximado).
    """

    postings: dict[str, list[_Posting]] = field(default_factory=dict)
    doc_count: int = 0
    last_built_at: float = 0.0


_INDEX = SearchIndex()


def _tokenize(text: str) -> list[str]:
    # Reemplazar separadores Unicode (em-dash, en-dash, etc.) por espacio antes de NFD
    # para no fusionar palabras al stripear los caracteres no-ASCII.
    raw = (text or "")
    for sep in ("—", "–", "‒", "‐", "/", "—", "–"):
        raw = raw.replace(sep, " ")
    normalized = unicodedata.normalize("NFD", raw).encode("ascii", "ignore").decode("ascii")
    return [
        tok
        for tok in _TOKEN_RE.findall(normalized.lower())
        if len(tok) >= _MIN_TOKEN_LEN and tok not in _STOPWORDS
    ]


def _slugify_section(title: str, idx: int) -> str:
    base = unicodedata.normalize("NFD", title or "").encode("ascii", "ignore").decode("ascii").lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")[:50]
    return f"{base}-{idx}" if base else f"section-{idx}"


def _walk_sections(
    sections: list[PatchSection],
    path: list[str],
    visit_block,  # callable(text, section_path, section_anchor)
    parent_idx: int = 0,
) -> None:
    for idx, section in enumerate(sections):
        section_path = [*path, section.title] if section.title else path
        anchor = _slugify_section(section.title or f"section-{parent_idx}-{idx}", idx)
        for block in section.blocks:
            visit_block(block, section_path, anchor)
        _walk_sections(section.subsections, section_path, visit_block, idx)


def build_index() -> SearchIndex:
    """Reconstruye el índice desde cero leyendo `by_patch/*.json`."""
    import time as _time

    data_dir = get_data_dir() / "normalized" / "by_patch"
    new_index = SearchIndex()

    if not data_dir.exists():
        _INDEX.postings.clear()
        _INDEX.doc_count = 0
        _INDEX.last_built_at = _time.time()
        return _INDEX

    files = list(data_dir.glob("*.json"))
    files.sort(key=lambda p: _version_sort_key(p.stem.split("_")[0]), reverse=True)

    for path in files:
        stem = path.stem
        if "_" not in stem:
            continue
        patch_version, locale = stem.rsplit("_", 1)
        note = _read_patch_file(patch_version, locale)
        if note is None:
            continue

        # Bind via default args para evitar B023 (closure sobre loop variable)
        def visit(
            text: str,
            section_path: list[str],
            anchor: str,
            *,
            _pv: str = patch_version,
            _loc: str = locale,
            _note_title: str = note.title,
        ) -> None:
            tokens = _tokenize(text)
            if not tokens:
                return
            new_index.doc_count += 1
            unique_tokens: dict[str, int] = {}
            for tok in tokens:
                unique_tokens[tok] = unique_tokens.get(tok, 0) + 1
            for tok in unique_tokens:
                posting = _Posting(
                    patch_version=_pv,
                    source_locale=_loc,
                    section_path=section_path or [_note_title],
                    block_text=text,
                    section_anchor=anchor,
                    token_count=len(tokens),
                )
                new_index.postings.setdefault(tok, []).append(posting)

        _walk_sections(note.sections, [], visit)

    new_index.last_built_at = _time.time()
    _INDEX.postings = new_index.postings
    _INDEX.doc_count = new_index.doc_count
    _INDEX.last_built_at = new_index.last_built_at
    logger.info(
        "[patch_notes/search] Índice reconstruido: %d tokens, %d bloques",
        len(_INDEX.postings),
        _INDEX.doc_count,
    )
    return _INDEX


def search(query: str, locale: str | None = None, limit: int = 20) -> list[SearchHit]:
    """Devuelve los hits ranqueados para la query. AND lógico entre tokens."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []
    if not _INDEX.postings:
        build_index()

    # AND: intersección de postings. Mantenemos lookup por (patch, locale, anchor)
    # para dedupe (un bloque con varios tokens cuenta una vez).
    candidate_by_key: dict[tuple[str, str, str], dict] = {}

    for tok in query_tokens:
        postings = _INDEX.postings.get(tok)
        if not postings:
            return []

    # Construir candidatos: bloques donde TODOS los tokens aparezcan.
    first_tok = query_tokens[0]
    initial = _INDEX.postings.get(first_tok, [])
    for posting in initial:
        if locale and posting.source_locale != locale:
            continue
        key = (posting.patch_version, posting.source_locale, posting.section_anchor)
        if key not in candidate_by_key:
            candidate_by_key[key] = {
                "posting": posting,
                "matched_tokens": {first_tok},
            }

    for tok in query_tokens[1:]:
        next_postings = {
            (p.patch_version, p.source_locale, p.section_anchor)
            for p in _INDEX.postings.get(tok, [])
            if not locale or p.source_locale == locale
        }
        to_remove = []
        for key, entry in candidate_by_key.items():
            if key not in next_postings:
                to_remove.append(key)
            else:
                entry["matched_tokens"].add(tok)
        for key in to_remove:
            del candidate_by_key[key]

    # Ranking simple: score = sum(1 / token_count) por token matcheado.
    hits: list[SearchHit] = []
    for entry in candidate_by_key.values():
        posting: _Posting = entry["posting"]
        matched = entry["matched_tokens"]
        score = sum(1.0 / max(posting.token_count, 1) for _ in matched) * len(matched)
        snippet = _make_snippet(posting.block_text, query_tokens)
        hits.append(
            SearchHit(
                patch_version=posting.patch_version,
                source_locale=posting.source_locale,
                section_path=posting.section_path,
                snippet=snippet,
                score=round(score, 4),
                section_anchor=posting.section_anchor,
            )
        )

    hits.sort(key=lambda h: (-h.score, _version_sort_key(h.patch_version)), reverse=False)
    # version sort reversed = desc → sort key returns tuples; we want score desc and version desc.
    hits.sort(key=lambda h: (-h.score, [-x if isinstance(x, int) else 0 for x in _version_sort_key(h.patch_version)]))
    return hits[:limit]


def _make_snippet(text: str, tokens: list[str]) -> str:
    """Extrae ±_SNIPPET_RADIUS chars alrededor del primer match en el texto original."""
    lower = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("ascii").lower()
    first_pos = -1
    for tok in tokens:
        pos = lower.find(tok)
        if pos != -1:
            first_pos = pos if first_pos == -1 else min(first_pos, pos)
    if first_pos == -1:
        return text[:200] + ("…" if len(text) > 200 else "")

    start = max(0, first_pos - _SNIPPET_RADIUS)
    end = min(len(text), first_pos + _SNIPPET_RADIUS)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"


def index_status() -> dict:
    """Estado del índice para diagnóstico."""
    return {
        "tokens": len(_INDEX.postings),
        "blocks_indexed": _INDEX.doc_count,
        "last_built_at": _INDEX.last_built_at,
    }


_ = Path  # silenciar import warning si no se usa
