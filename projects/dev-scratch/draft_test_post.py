import requests
import json

payload = {
    "allies": [{"id": "Volibear"}],
    "enemies": [{"id": "Nautilus"}],
    "bans": [],
    "context": {
        "pick_position": "late",
        "information_level": "none",
        "queue_type": "ranked_solo"
    },
    "user_pool": {
        "mode": "unrestricted",
        "champions": [],
        "comfort": {}
    },
    "target_role": "support"
}

try:
    response = requests.post("http://localhost:8001/api/v1/draft/recommend", json=payload)
    print(response.status_code)
    try:
        print(json.dumps(response.json(), indent=2))
    except BaseException:
        print(response.text[:500])
except Exception as e:
    print(f"Error: {e}")
