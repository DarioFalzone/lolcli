"""
Scaffold de ingesta de fuentes: flujo mínimo para agregar fuentes a la KB.

Provee:
1. register_source() — agrega una entrada a manifest.json
2. create_research_template() — genera una plantilla de nota desde una fuente
3. Stub para extracción futura de texto desde PDF

Usage:
    python data/draft_advisor/kb/scripts/ingest_scaffold.py register \\
        --source-id "src-patch-16-8" \\
        --source-type "riot_patch_notes" \\
        --patch "16.8" \\
        --trust-level "authoritative" \\
        --notes "Notas del parche 16.8 extraídas del sitio de Riot"

    python data/draft_advisor/kb/scripts/ingest_scaffold.py template \\
        --note-id "patch-16-8-adc-summary" \\
        --title "Resumen de impacto ADC del parche 16.8" \\
        --note-type "patch_summary" \\
        --patch "16.8" \\
        --champions "Jinx,Ezreal,Caitlyn"
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from textwrap import dedent

_SCRIPT_DIR = Path(__file__).resolve().parent
_KB_ROOT = _SCRIPT_DIR.parent


def register_source(
    source_id: str,
    source_type: str,
    patch: str,
    trust_level: str = "community",
    file_path: str | None = None,
    origin_url: str | None = None,
    notes: str = "",
) -> None:
    """Register a new source in manifest.json."""
    manifest_path = _KB_ROOT / "manifest.json"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Check for duplicate source_id
    existing_ids = {s["source_id"] for s in manifest["sources"]}
    if source_id in existing_ids:
        print(f"ERROR: Source ID '{source_id}' already exists in manifest.")
        sys.exit(1)

    entry = {
        "source_id": source_id,
        "file_path": file_path,
        "source_type": source_type,
        "origin_url": origin_url,
        "capture_date": date.today().isoformat(),
        "patch_relevance": patch,
        "trust_level": trust_level,
        "review_status": "draft",
        "linked_research_notes": [],
        "linked_structured_updates": [],
        "notes": notes,
    }

    manifest["sources"].append(entry)
    manifest["last_updated"] = date.today().isoformat()

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Registered source '{source_id}' in manifest.json")


# Note type -> folder mapping
_TYPE_TO_FOLDER = {
    "adc_champion_note": "research/adcs",
    "support_synergy_note": "research/supports",
    "threat_note": "research/threats",
    "archetype_note": "research/archetypes",
    "matchup_note": "research/matchups",
    "patch_summary": "research/patches",
    "heuristic_note": "research/heuristics",
    "meta_snapshot": "research/meta",
}


def create_research_template(
    note_id: str,
    title: str,
    note_type: str,
    patch: str,
    source_type: str = "expert_analysis",
    champions: list[str] | None = None,
    topics: list[str] | None = None,
) -> Path:
    """Generate a research note template markdown file."""
    if note_type not in _TYPE_TO_FOLDER:
        print(f"ERROR: Unknown note type '{note_type}'. Valid types: {list(_TYPE_TO_FOLDER.keys())}")
        sys.exit(1)

    folder = _KB_ROOT / _TYPE_TO_FOLDER[note_type]
    folder.mkdir(parents=True, exist_ok=True)

    filepath = folder / f"{note_id}.md"
    if filepath.exists():
        print(f"ERROR: File already exists: {filepath}")
        sys.exit(1)

    today = date.today().isoformat()
    champions_yaml = json.dumps(champions or [])
    topics_yaml = json.dumps(topics or [])

    template = dedent(f"""\
    ---
    schema_version: "1.0"
    kb_version: "1"
    id: "{note_id}"
    title: "{title}"
    type: "{note_type}"
    domain: "draft_advisor"
    patch: "{patch}"
    source_type: "{source_type}"
    source_url: ""
    source_file: ""
    created_at: "{today}"
    last_reviewed_at: "{today}"
    review_status: "draft"
    confidence: "medium"
    champions: {champions_yaml}
    roles: ["Bot"]
    topics: {topics_yaml}
    tags: []
    derived_from: []
    supersedes: []
    superseded_by: []
    ---

    ## Resumen

    [Resumen ejecutivo de un parrafo]

    ## Hallazgos Clave

    - [Hallazgo 1]
    - [Hallazgo 2]

    ## Implicancias de Draft

    [Como afecta las decisiones de pick ADC]

    ## Cuando Importa

    - [Condicion 1]
    - [Condicion 2]

    ## Advertencias

    - [Limitacion 1]

    ## Claims Extraibles

    - [Claim condicional en formato pseudo-regla]

    ## Campeones / Composiciones Relacionadas

    - [Items relacionados]

    ## Notas de Fuente

    [Atribucion y notas de calidad de la fuente]
    """)

    filepath.write_text(template, encoding="utf-8")
    print(f"Plantilla de investigacion creada: {filepath}")
    return filepath


def extract_pdf_text_stub(pdf_path: Path) -> str:
    """
    Stub para extraccion de texto desde PDF.
    V1: Returns a placeholder message.
    V2: Will use pdfplumber or pymupdf for actual extraction.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    return (
        f"[PDF TEXT EXTRACTION STUB]\n"
        f"File: {pdf_path.name}\n"
        f"Size: {pdf_path.stat().st_size} bytes\n\n"
        f"To extract text, install pdfplumber:\n"
        f"  pip install pdfplumber\n\n"
        f"Then replace this stub with:\n"
        f"  import pdfplumber\n"
        f"  with pdfplumber.open(pdf_path) as pdf:\n"
        f"      text = '\\n'.join(page.extract_text() or '' for page in pdf.pages)\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Scaffold de ingesta de fuentes KB")
    subparsers = parser.add_subparsers(dest="command")

    # Register command
    reg = subparsers.add_parser("register", help="Register a new source in manifest.json")
    reg.add_argument("--source-id", required=True)
    reg.add_argument("--source-type", required=True)
    reg.add_argument("--patch", required=True)
    reg.add_argument("--trust-level", default="community")
    reg.add_argument("--file-path", default=None)
    reg.add_argument("--origin-url", default=None)
    reg.add_argument("--notes", default="")

    # Template command
    tmpl = subparsers.add_parser("template", help="Create a research note template")
    tmpl.add_argument("--note-id", required=True)
    tmpl.add_argument("--title", required=True)
    tmpl.add_argument("--note-type", required=True)
    tmpl.add_argument("--patch", required=True)
    tmpl.add_argument("--source-type", default="expert_analysis")
    tmpl.add_argument("--champions", default="", help="Comma-separated champion IDs")
    tmpl.add_argument("--topics", default="", help="Comma-separated topics")

    args = parser.parse_args()

    if args.command == "register":
        register_source(
            source_id=args.source_id,
            source_type=args.source_type,
            patch=args.patch,
            trust_level=args.trust_level,
            file_path=args.file_path,
            origin_url=args.origin_url,
            notes=args.notes,
        )
    elif args.command == "template":
        champs = [c.strip() for c in args.champions.split(",") if c.strip()] if args.champions else []
        topics = [t.strip() for t in args.topics.split(",") if t.strip()] if args.topics else []
        create_research_template(
            note_id=args.note_id,
            title=args.title,
            note_type=args.note_type,
            patch=args.patch,
            source_type=args.source_type,
            champions=champs,
            topics=topics,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
