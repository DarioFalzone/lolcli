#!/usr/bin/env python3
"""
Data Freshness Validator
Flags KB artifacts that are deemed too old compared to the live_patch_label.
"""
import os
import sys
import yaml
from pathlib import Path
import json

def get_patch_major(patch_str):
    try:
        return float(patch_str)
    except:
        return 0.0

def run_validation():
    base_dir = Path(__file__).parent.parent.parent
    
    with open(base_dir / "data_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    live_label = manifest.get("live_patch_label", "0.0")
    live_major = get_patch_major(live_label)

    research_dir = base_dir / "kb" / "research"
    stale_count = 0
    tft_count = 0

    print(f"Checking data freshness against Live Patch: {live_label}")
    
    for root, _, files in os.walk(research_dir):
        for file in files:
            if file.endswith(".md"):
                path = Path(root) / file
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check TFT contamination
                if "tft" in content.lower():
                    print(f"ERROR: TFT string found in KB note: {file}")
                    tft_count += 1
                
                # Extract frontmatter bounded by ---
                if content.startswith("---"):
                    try:
                        fm_str = content.split("---")[1]
                        meta = yaml.safe_load(fm_str)
                        if "patch" in meta:
                            patch = meta["patch"]
                            # simple delta check
                            if get_patch_major(live_label) - get_patch_major(patch) > 2.0:
                                print(f"WARNING: Note {file} is Stale ({patch} vs {live_label})")
                                stale_count += 1
                        if "live_patch_label" in meta and meta["live_patch_label"]:
                            patch = meta["live_patch_label"]
                            if get_patch_major(live_label) - get_patch_major(patch) > 2.0:
                                print(f"WARNING: Note {file} is Stale ({patch} vs {live_label})")
                                stale_count += 1
                    except Exception as e:
                        pass
    
    if tft_count > 0:
        sys.exit(1)
        
    print(f"SUCCESS: Freshness check completed. {stale_count} stale notes optionally flagged.")

if __name__ == "__main__":
    run_validation()
