"""Pydantic V2 models for the Patch Notes subsystem.

Schema inspirado en el deep research (`projects/active/patch-notes/deep-research-report.md`),
sección "Modelo de datos". Separa nota, secciones (recursivas), assets y manifest para que
V2 pueda agregar search/diff/multi-locale UI sin migrar datos.

V2 agrega: PatchEnrichment (datos por fuente no-canónica), SearchHit (resultado de búsqueda)
y PatchDiff (comparación entre versiones).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PatchSection(BaseModel):
    """Una sección del patch note. Recursiva para H2 → H3 → H4."""

    model_config = ConfigDict(extra="ignore")

    title: str
    heading_level: int = Field(ge=1, le=6, description="Nivel HTML (2, 3, 4)")
    blocks: list[str] = Field(default_factory=list, description="Párrafos y listas de la sección")
    subsections: list[PatchSection] = Field(default_factory=list)


class PatchAsset(BaseModel):
    """Imagen o link encontrado en la nota."""

    model_config = ConfigDict(extra="ignore")

    asset_type: Literal["image", "link"]
    src: str
    alt: str | None = None
    text: str | None = None


class PatchEnrichment(BaseModel):
    """Payload de una fuente no-canónica para un parche específico.

    Cada fuente adicional (LoL /dev, calendario Riot, DDragon, U.GG, OP.GG, etc.)
    se adjunta como un enrichment al `PatchNote` canónico. Si el scraping falla,
    queda con `error` y `payload={}` pero la entrada persiste para auditar.
    """

    model_config = ConfigDict(extra="ignore")

    source: str = Field(description="lol_dev | riot_calendar | ddragon | ugg_patch | opgg_patch | lolalytics_patch | mobalytics_patch")
    source_url: str | None = None
    fetched_at: datetime
    content_hash: str = Field(min_length=64, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class PatchNote(BaseModel):
    """Patch note completo con secciones, assets y enrichments por fuente."""

    model_config = ConfigDict(extra="ignore")

    publisher: Literal["riot"] = "riot"
    game: Literal["lol"] = "lol"
    channel: Literal["site", "dev", "support"] = "site"
    source_locale: str = Field(description="es-es, es-mx, en-us")
    patch_version: str = Field(description="Ej: 25.17, 26.10b")
    title: str
    canonical_url: str
    published_at: datetime | None = None
    fetched_at: datetime
    content_hash: str = Field(min_length=64, max_length=64, description="sha256 hex de sections")
    summary: str | None = None
    sections: list[PatchSection] = Field(default_factory=list)
    assets: list[PatchAsset] = Field(default_factory=list)
    scraper_version: str
    raw_html_ref: str | None = Field(default=None, description="Path relativo al HTML snapshot")
    enrichments: list[PatchEnrichment] = Field(default_factory=list, description="V2: datos de fuentes no-canónicas")


class PatchNoteIndex(BaseModel):
    """Versión compacta para la lista de parches en la UI."""

    model_config = ConfigDict(extra="ignore")

    patch_version: str
    title: str
    published_at: datetime | None = None
    canonical_url: str
    source_locale: str
    summary: str | None = None
    content_hash: str
    section_count: int = 0


class ManifestEntry(BaseModel):
    """Una entrada del manifest indexada por (patch_version, locale)."""

    model_config = ConfigDict(extra="ignore")

    patch_version: str
    source_locale: str
    file: str = Field(description="Path relativo a data/patch_notes/ (ej: normalized/by_patch/...)")
    content_hash: str
    fetched_at: datetime
    published_at: datetime | None = None
    title: str
    canonical_url: str


class PatchManifest(BaseModel):
    """Estado global de patch notes scrapeados."""

    model_config = ConfigDict(extra="ignore")

    schema_version: str = "1.0"
    last_scrape: datetime | None = None
    scraper_version: str
    locales: list[str] = Field(default_factory=list)
    available_patches: list[str] = Field(default_factory=list, description="Versiones únicas conocidas, desc")
    entries: list[ManifestEntry] = Field(default_factory=list)


class SourceStatus(BaseModel):
    """Estado de cada fuente en el manifest."""

    model_config = ConfigDict(extra="ignore")

    last_scrape: datetime | None = None
    last_success: datetime | None = None
    last_error: str | None = None
    available_patches: list[str] = Field(default_factory=list)


class SearchHit(BaseModel):
    """Resultado individual de búsqueda full-text."""

    model_config = ConfigDict(extra="ignore")

    patch_version: str
    source_locale: str
    section_path: list[str] = Field(description="Jerarquía: ['Campeones', 'Aatrox']")
    snippet: str
    score: float
    section_anchor: str | None = Field(default=None, description="Anchor slug para deep-link")


class DiffSection(BaseModel):
    """Diferencia detectada en una sección entre dos parches."""

    model_config = ConfigDict(extra="ignore")

    title: str
    change_type: Literal["added", "removed", "modified", "unchanged"]
    heading_level: int = 2
    a_blocks: list[str] = Field(default_factory=list)
    b_blocks: list[str] = Field(default_factory=list)
    sub_diffs: list[DiffSection] = Field(default_factory=list)


class PatchDiff(BaseModel):
    """Diff completo entre dos versiones del mismo locale."""

    model_config = ConfigDict(extra="ignore")

    a_version: str
    b_version: str
    source_locale: str
    a_title: str
    b_title: str
    sections: list[DiffSection]
    summary: dict[str, int] = Field(default_factory=dict, description="{added, removed, modified, unchanged}")


PatchSection.model_rebuild()
DiffSection.model_rebuild()
