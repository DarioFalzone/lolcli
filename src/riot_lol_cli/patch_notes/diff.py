"""Diff entre dos PatchNote del mismo locale.

Algoritmo:
1. Match de secciones top-level por título normalizado (lowercase, sin acentos).
2. Si la sección está en ambos: comparar `blocks` y aplicar recursión a `subsections`.
   - `unchanged` si blocks y subsecciones son idénticos.
   - `modified` si hay cualquier diferencia.
3. Si la sección está solo en `a` → `removed`.
4. Si la sección está solo en `b` → `added`.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Literal

from .schema import DiffSection, PatchDiff, PatchNote, PatchSection

ChangeType = Literal["added", "removed", "modified", "unchanged"]


def _normalize_title(title: str) -> str:
    base = unicodedata.normalize("NFD", title or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", base.lower()).strip()


def _blocks_equal(a: list[str], b: list[str]) -> bool:
    return [s.strip() for s in a] == [s.strip() for s in b]


def _diff_sections(
    a_sections: list[PatchSection],
    b_sections: list[PatchSection],
) -> list[DiffSection]:
    a_by_key: dict[str, tuple[int, PatchSection]] = {}
    for idx, sec in enumerate(a_sections):
        key = _normalize_title(sec.title)
        if key in a_by_key:
            # Sección con título duplicado → desambiguar con idx
            key = f"{key}#{idx}"
        a_by_key[key] = (idx, sec)

    b_by_key: dict[str, tuple[int, PatchSection]] = {}
    for idx, sec in enumerate(b_sections):
        key = _normalize_title(sec.title)
        if key in b_by_key:
            key = f"{key}#{idx}"
        b_by_key[key] = (idx, sec)

    seen_b_keys: set[str] = set()
    diffs: list[DiffSection] = []

    # Iterar en orden de A (mantiene narrativa del parche más viejo)
    for key, (_a_idx, a_sec) in a_by_key.items():
        if key in b_by_key:
            seen_b_keys.add(key)
            _b_idx, b_sec = b_by_key[key]
            sub_diffs = _diff_sections(a_sec.subsections, b_sec.subsections)
            sub_changed = any(s.change_type != "unchanged" for s in sub_diffs)
            blocks_same = _blocks_equal(a_sec.blocks, b_sec.blocks)
            if blocks_same and not sub_changed:
                change_type: ChangeType = "unchanged"
            else:
                change_type = "modified"
            diffs.append(
                DiffSection(
                    title=a_sec.title or b_sec.title or "(sin título)",
                    change_type=change_type,
                    heading_level=a_sec.heading_level,
                    a_blocks=a_sec.blocks,
                    b_blocks=b_sec.blocks,
                    sub_diffs=sub_diffs,
                )
            )
        else:
            diffs.append(
                DiffSection(
                    title=a_sec.title or "(sin título)",
                    change_type="removed",
                    heading_level=a_sec.heading_level,
                    a_blocks=a_sec.blocks,
                    b_blocks=[],
                    sub_diffs=[
                        DiffSection(
                            title=sub.title,
                            change_type="removed",
                            heading_level=sub.heading_level,
                            a_blocks=sub.blocks,
                            b_blocks=[],
                        )
                        for sub in a_sec.subsections
                    ],
                )
            )

    # Secciones que están solo en B → added (al final, en orden de B)
    for key, (_b_idx, b_sec) in b_by_key.items():
        if key in seen_b_keys:
            continue
        diffs.append(
            DiffSection(
                title=b_sec.title or "(sin título)",
                change_type="added",
                heading_level=b_sec.heading_level,
                a_blocks=[],
                b_blocks=b_sec.blocks,
                sub_diffs=[
                    DiffSection(
                        title=sub.title,
                        change_type="added",
                        heading_level=sub.heading_level,
                        a_blocks=[],
                        b_blocks=sub.blocks,
                    )
                    for sub in b_sec.subsections
                ],
            )
        )

    return diffs


def diff_patches(a: PatchNote, b: PatchNote) -> PatchDiff:
    """Compara dos PatchNote y devuelve un PatchDiff con secciones taggeadas."""
    if a.source_locale != b.source_locale:
        raise ValueError(
            f"Diff requiere mismo locale: a={a.source_locale}, b={b.source_locale}"
        )
    sections = _diff_sections(a.sections, b.sections)

    summary = {"added": 0, "removed": 0, "modified": 0, "unchanged": 0}

    def count(s: DiffSection) -> None:
        summary[s.change_type] = summary.get(s.change_type, 0) + 1
        for sub in s.sub_diffs:
            count(sub)

    for s in sections:
        count(s)

    return PatchDiff(
        a_version=a.patch_version,
        b_version=b.patch_version,
        source_locale=a.source_locale,
        a_title=a.title,
        b_title=b.title,
        sections=sections,
        summary=summary,
    )
