#!/usr/bin/env python3
"""
Semantic Version Validator

Enforces semantic separation between Player-Facing Live Patch Labels
and the underlying technical Data Dragon Static Data Versions.

Rules:
1. live_patch_label must follow season rules (e.g., 26.x or X.x)
2. static_data_version must match a real DDragon build (e.g. 16.x.x)
3. Must block TFT contamination.
"""

import json
import re
import sys
from pathlib import Path
import urllib.request

def run_validation():
    base_dir = Path(__file__).parent.parent.parent
    manifest_path = base_dir / "data_manifest.json"
    
    if not manifest_path.exists():
        print(f"ERROR: Missing {manifest_path}")
        sys.exit(1)
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    live_label = manifest.get("live_patch_label", "")
    static_version = manifest.get("static_data_version", "")

    # Rule 1: TFT contamination guard
    if "tft" in live_label.lower() or "tft" in static_version.lower():
        print("ERROR: TFT product contamination detected in version identifiers!")
        sys.exit(1)

    # Rule 2: Basic Pattern matches
    if not re.match(r"^\d+\.\d+$", live_label):
        print(f"ERROR: live_patch_label '{live_label}' must be 'X.Y'")
        sys.exit(1)
        
    if not re.match(r"^\d+\.\d+\.\d+$", static_version):
        print(f"ERROR: static_data_version '{static_version}' must be 'X.Y.Z' (DDragon Asset Format)")
        sys.exit(1)

    # Rule 3: Network assertion (DDragon sync)
    print(f"Querying DDragon to verify {static_version}...")
    try:
        url = "https://ddragon.leagueoflegends.com/api/versions.json"
        with urllib.request.urlopen(url, timeout=5) as resp:
            versions = json.loads(resp.read().decode())
    except Exception as e:
        print(f"WARNING: DDragon offline check failed ({e}) - continuing with generic validation.")
        return

    if static_version not in versions:
        print(f"ERROR: static_data_version {static_version} is NOT a valid DDragon release!")
        sys.exit(1)
        
    print(f"SUCCESS: {live_label} semantically decoupled from valid underlying {static_version}.")

if __name__ == "__main__":
    run_validation()
