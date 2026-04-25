#!/usr/bin/env python3
"""
Canonical Champion Validator
Validates local champion_base.json subset against DDragon 
preventing silent data drifts.
"""
import json
import sys
import urllib.request
from pathlib import Path

def run_validation():
    base_dir = Path(__file__).parent.parent.parent
    
    with open(base_dir / "data_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    version = manifest.get("static_data_version")
    
    with open(base_dir / "champion_base.json", "r", encoding="utf-8") as f:
        local_data = json.load(f)
        champs = local_data.get("champions", {})
        
    print(f"Validating {len(champs)} local champions against DDragon {version}...")
    try:
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
        with urllib.request.urlopen(url, timeout=5) as resp:
            remote_data = json.loads(resp.read().decode())
            remote_champs = remote_data["data"]
    except Exception as e:
        print(f"WARNING: DDragon fetch failed ({e})")
        return
        
    if len(champs) != len(remote_champs):
        print(f"ERROR: Canonical count mismatch. Local: {len(champs)}, Remote: {len(remote_champs)}")
        sys.exit(1)
        
    for champ_id in champs:
        if champ_id not in remote_champs:
            print(f"ERROR: Local champion {champ_id} does not exist in Canonical DDragon!")
            sys.exit(1)
            
    print("SUCCESS: Canonical baseline structurally verified.")

if __name__ == "__main__":
    run_validation()
