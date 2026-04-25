"""
KB Validation Script — Validates the entire Knowledge Base for consistency.

Checks:
1. All research notes have valid frontmatter matching the schema
2. All note IDs are unique
3. All note type prefixes match their folder location
4. All referenced champion IDs exist in champion_base.json
5. All patch references match the required format
6. All topics/roles match the controlled taxonomy
7. Manifest references valid files and notes
8. Supersedes/superseded_by are symmetric
9. Structured files parse correctly

Usage:
    python -m data.draft_advisor.kb.scripts.validate_kb
    OR
    python data/draft_advisor/kb/scripts/validate_kb.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set

import yaml

# Resolve project paths
_SCRIPT_DIR = Path(__file__).resolve().parent
_KB_ROOT = _SCRIPT_DIR.parent
_DATA_ROOT = _KB_ROOT.parent
_PROJECT_ROOT = _DATA_ROOT.parents[1]

# Add src to path for imports
sys.path.insert(0, str(_PROJECT_ROOT / "src"))


def _load_taxonomy() -> dict:
    """Load the controlled taxonomy."""
    path = _KB_ROOT / "taxonomy.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_champion_ids() -> Set[str]:
    """Load valid champion IDs from champion_base.json."""
    path = _DATA_ROOT / "champion_base.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("champions", {}).keys())


def _parse_frontmatter(filepath: Path) -> dict | None:
    """Parse YAML frontmatter from a markdown file."""
    text = filepath.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end_idx = text.find("---", 3)
    if end_idx == -1:
        return None
    yaml_text = text[3:end_idx].strip()
    return yaml.safe_load(yaml_text)


class KBValidator:
    """Validates the entire KB structure and content."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.taxonomy = _load_taxonomy()
        self.champion_ids = _load_champion_ids()
        self.note_ids: Dict[str, Path] = {}  # id -> filepath
        self.patch_pattern = re.compile(self.taxonomy["patch_format"]["pattern"])

    def validate_all(self) -> bool:
        """Run all validations. Returns True if no errors."""
        print("=" * 60)
        print("KB Validation")
        print("=" * 60)

        self._validate_directory_structure()
        self._validate_taxonomy()
        self._validate_research_notes()
        self._validate_manifest()
        self._validate_structured_files()
        self._validate_golden_drafts()
        self._validate_supersedes_symmetry()

        # Report
        print()
        if self.warnings:
            print(f"WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  [WARN] {w}")
            print()

        if self.errors:
            print(f"ERRORS ({len(self.errors)}):")
            for e in self.errors:
                print(f"  [ERROR] {e}")
            print()
            print(f"VALIDATION FAILED: {len(self.errors)} errors, {len(self.warnings)} warnings")
            return False
        else:
            print(f"VALIDATION PASSED: 0 errors, {len(self.warnings)} warnings")
            return True

    def _validate_directory_structure(self):
        """Check that expected directories exist."""
        print("\n--- Directory Structure ---")
        required_dirs = [
            "sources", "sources/patch_notes", "sources/pdf", "sources/web", "sources/notes",
            "research", "research/adcs", "research/supports", "research/threats",
            "research/archetypes", "research/matchups", "research/patches",
            "research/heuristics", "research/meta",
            "structured", "evals",
        ]
        for d in required_dirs:
            full_path = _KB_ROOT / d
            if full_path.exists():
                print(f"  [OK] {d}/")
            else:
                # Create missing directories (they may just be empty)
                full_path.mkdir(parents=True, exist_ok=True)
                self.warnings.append(f"Created missing directory: {d}/")
                print(f"  [CREATED] {d}/")

    def _validate_taxonomy(self):
        """Validate the taxonomy file itself."""
        print("\n--- Taxonomy ---")
        required_keys = ["note_types", "confidence_levels", "review_statuses",
                         "source_types", "trust_levels", "roles", "topics", "patch_format"]
        for key in required_keys:
            if key not in self.taxonomy:
                self.errors.append(f"Taxonomy missing key: {key}")
            else:
                print(f"  [OK] taxonomy.{key}")

    def _validate_research_notes(self):
        """Validate all research note frontmatter."""
        print("\n--- Research Notes ---")
        research_dir = _KB_ROOT / "research"
        if not research_dir.exists():
            self.errors.append("research/ directory does not exist")
            return

        md_files = list(research_dir.rglob("*.md"))
        print(f"  Found {len(md_files)} markdown files")

        valid_note_types = set(self.taxonomy["note_types"].keys())
        valid_confidences = set(self.taxonomy["confidence_levels"])
        valid_review_statuses = set(self.taxonomy["review_statuses"])
        valid_source_types = set(self.taxonomy["source_types"])
        valid_roles = set(self.taxonomy["roles"])
        valid_topics = set(self.taxonomy["topics"])
        type_prefix_map = {nt: info["prefix"] for nt, info in self.taxonomy["note_types"].items()}
        type_folder_map = {nt: info["folder"] for nt, info in self.taxonomy["note_types"].items()}

        for md_file in md_files:
            rel_path = md_file.relative_to(_KB_ROOT)
            fm = _parse_frontmatter(md_file)

            if fm is None:
                self.errors.append(f"{rel_path}: No valid YAML frontmatter")
                continue

            # Required fields
            for field in ["id", "title", "type", "source_type",
                          "review_status", "confidence", "created_at"]:
                if field not in fm:
                    self.errors.append(f"{rel_path}: Missing required field '{field}'")

            note_id = fm.get("id", "")
            note_type = fm.get("type", "")

            # Unique ID check
            if note_id in self.note_ids:
                self.errors.append(
                    f"{rel_path}: Duplicate ID '{note_id}' (also in {self.note_ids[note_id]})"
                )
            else:
                self.note_ids[note_id] = md_file

            # Note type validation
            if note_type not in valid_note_types:
                self.errors.append(f"{rel_path}: Invalid note type '{note_type}'")

            # ID prefix must match note type
            if note_type in type_prefix_map:
                expected_prefix = type_prefix_map[note_type]
                if not note_id.startswith(expected_prefix):
                    self.errors.append(
                        f"{rel_path}: ID '{note_id}' should start with '{expected_prefix}' for type '{note_type}'"
                    )

            # Folder must match note type
            if note_type in type_folder_map:
                expected_folder = type_folder_map[note_type]
                actual_folder = str(rel_path.parent).replace("\\", "/") + "/"
                if not actual_folder.endswith(expected_folder.rstrip("/") + "/") and \
                   expected_folder not in actual_folder:
                    self.warnings.append(
                        f"{rel_path}: Note type '{note_type}' expected in '{expected_folder}'"
                    )

            # Patch format
            patch = fm.get("patch_scope", "")
            if patch and patch != "*" and not self.patch_pattern.match(patch):
                self.errors.append(f"{rel_path}: Invalid patch_scope format '{patch}' (expected X.Y)")
            live_label = fm.get("live_patch_label", "")
            if live_label and not self.patch_pattern.match(live_label):
                self.errors.append(f"{rel_path}: Invalid live_patch_label format '{live_label}'")

            # Confidence
            confidence = fm.get("confidence", "")
            if confidence and confidence not in valid_confidences:
                self.errors.append(f"{rel_path}: Invalid confidence '{confidence}'")

            # Review status
            review = fm.get("review_status", "")
            if review and review not in valid_review_statuses:
                self.errors.append(f"{rel_path}: Invalid review_status '{review}'")

            # Source type
            source_type = fm.get("source_type", "")
            if source_type and source_type not in valid_source_types:
                self.errors.append(f"{rel_path}: Invalid source_type '{source_type}'")

            # Champions — validate against champion_base
            champions = fm.get("champions", [])
            for champ in champions:
                if champ not in self.champion_ids:
                    self.warnings.append(f"{rel_path}: Champion '{champ}' not in champion_base.json")

            # Roles
            roles = fm.get("roles", [])
            for role in roles:
                if role not in valid_roles:
                    self.errors.append(f"{rel_path}: Invalid role '{role}'")

            # Topics
            topics = fm.get("topics", [])
            for topic in topics:
                if topic not in valid_topics:
                    self.warnings.append(f"{rel_path}: Topic '{topic}' not in taxonomy")

            print(f"  [OK] {rel_path} (id={note_id})")

    def _validate_manifest(self):
        """Validate manifest.json."""
        print("\n--- Source Manifest ---")
        manifest_path = _KB_ROOT / "manifest.json"
        if not manifest_path.exists():
            self.errors.append("manifest.json does not exist")
            return

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        sources = manifest.get("sources", [])
        print(f"  Found {len(sources)} source entries")

        source_ids = set()
        for entry in sources:
            sid = entry.get("source_id", "")
            if sid in source_ids:
                self.errors.append(f"Manifest: Duplicate source_id '{sid}'")
            source_ids.add(sid)

            # Patch format
            patch = entry.get("patch_scope", "")
            if patch and patch != "*" and not self.patch_pattern.match(patch):
                self.errors.append(f"Manifest: Invalid patch_scope format '{patch}' in source '{sid}'")

            # Validate linked research notes exist
            for note_id in entry.get("linked_research_notes", []):
                if note_id not in self.note_ids:
                    self.warnings.append(
                        f"Manifest: Source '{sid}' links to unknown note '{note_id}'"
                    )

            print(f"  [OK] {sid}")

    def _validate_structured_files(self):
        """Validate structured JSON files parse correctly."""
        print("\n--- Structured Data ---")
        structured_dir = _KB_ROOT / "structured"
        if not structured_dir.exists():
            self.errors.append("structured/ directory does not exist")
            return

        for json_file in structured_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                sv = data.get("schema_version", "missing")
                print(f"  [OK] {json_file.name} (schema_version={sv})")

                # Validate champion IDs in patch_overrides
                if json_file.name == "patch_overrides.json":
                    for ovr in data.get("overrides", []):
                        champ = ovr.get("champion_id", "")
                        if champ and champ not in self.champion_ids:
                            self.errors.append(
                                f"patch_overrides.json: Unknown champion '{champ}'"
                            )

                # Validate champion IDs in comp_archetypes
                if json_file.name == "comp_archetypes.json":
                    for arch_id, arch in data.get("archetypes", {}).items():
                        prefs = arch.get("adc_preferences", {})
                        for champ in prefs.get("preferred_adcs", []) + prefs.get("avoid_adcs", []):
                            if champ not in self.champion_ids:
                                self.warnings.append(
                                    f"comp_archetypes.json: '{arch_id}' references unknown champion '{champ}'"
                                )

            except json.JSONDecodeError as e:
                self.errors.append(f"{json_file.name}: Invalid JSON - {e}")

    def _validate_golden_drafts(self):
        """Validate golden_drafts.json."""
        print("\n--- Golden Draft Cases ---")
        golden_path = _KB_ROOT / "evals" / "golden_drafts.json"
        if not golden_path.exists():
            self.errors.append("evals/golden_drafts.json does not exist")
            return

        with open(golden_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cases = data.get("cases", [])
        print(f"  Found {len(cases)} golden cases")

        case_ids = set()
        for case in cases:
            cid = case.get("case_id", "")
            if cid in case_ids:
                self.errors.append(f"Golden drafts: Duplicate case_id '{cid}'")
            case_ids.add(cid)

            # Validate champion IDs in draft states
            for champ_entry in case.get("draft_state", {}).get("allies", []):
                cname = champ_entry.get("id", "")
                if cname and cname not in self.champion_ids:
                    self.errors.append(f"Golden draft '{cid}': Unknown ally champion '{cname}'")
            for champ_entry in case.get("draft_state", {}).get("enemies", []):
                cname = champ_entry.get("id", "")
                if cname and cname not in self.champion_ids:
                    self.errors.append(f"Golden draft '{cid}': Unknown enemy champion '{cname}'")

            # Validate assertion champion IDs
            assertions = case.get("assertions", {})
            for key in ["top_pick_must_be_one_of", "top_3_must_include_any_of",
                        "must_not_recommend_as_top"]:
                for cname in assertions.get(key, []):
                    if cname not in self.champion_ids:
                        self.warnings.append(
                            f"Golden draft '{cid}': Assertion references unknown champion '{cname}'"
                        )

            print(f"  [OK] {cid}")

    def _validate_supersedes_symmetry(self):
        """Check that supersedes/superseded_by relationships are symmetric."""
        print("\n--- Supersedes Symmetry ---")
        research_dir = _KB_ROOT / "research"
        if not research_dir.exists():
            return

        for md_file in research_dir.rglob("*.md"):
            fm = _parse_frontmatter(md_file)
            if fm is None:
                continue

            note_id = fm.get("id", "")

            # Check supersedes
            for superseded_id in fm.get("supersedes", []):
                if superseded_id in self.note_ids:
                    target_fm = _parse_frontmatter(self.note_ids[superseded_id])
                    if target_fm and note_id not in target_fm.get("superseded_by", []):
                        self.warnings.append(
                            f"Note '{note_id}' supersedes '{superseded_id}' but "
                            f"'{superseded_id}' doesn't list '{note_id}' in superseded_by"
                        )

            # Check superseded_by
            for superseding_id in fm.get("superseded_by", []):
                if superseding_id in self.note_ids:
                    target_fm = _parse_frontmatter(self.note_ids[superseding_id])
                    if target_fm and note_id not in target_fm.get("supersedes", []):
                        self.warnings.append(
                            f"Note '{note_id}' superseded_by '{superseding_id}' but "
                            f"'{superseding_id}' doesn't list '{note_id}' in supersedes"
                        )

        print("  [OK] Supersedes checks complete")


def run_remote_validators():
    import subprocess
    print("\n--- Running Offline Remote Validators ---")
    scripts = [
        "semantic_version_validator.py",
        "canonical_champion_validator.py",
        "data_freshness_validator.py"
    ]
    for script in scripts:
        script_path = _SCRIPT_DIR / script
        if script_path.exists():
            print(f"> Executing {script}...")
            res = subprocess.run([sys.executable, str(script_path)])
            if res.returncode != 0:
                print(f"  [FAILED] {script} returned {res.returncode}")
                return False
            print()
    return True

def main():
    validator = KBValidator()
    success = validator.validate_all()
    
    # Run remote offline checks if explicitly requested
    if "--remote" in sys.argv:
        if not run_remote_validators():
            success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
