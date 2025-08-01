import requests
import json

url = "http://127.0.0.1:8000/api/v1/hackrx/run"
headers = {
    "Authorization": "Bearer 87436cd7e9ec09c6ae1c66eb55aa5da937d1ec6c22a032731eb773c9a9727777",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
data = {
    "documents": "https://hackrx.blob.core.windows.net/assets/hackrx_6/policies/EDLHLGA23009V012223.pdf?sv=2023-01-03&st=2025-07-30T06%3A46%3A49Z&se=2025-09-01T06%3A46%3A00Z&sr=c&sp=rl&sig=9szykRKdGYj0BVm1skP%2BX8N9%2FRENEn2k7MQPUp33jyQ%3D",
    "questions": [
        "What is the grace period for premium payment?",
        "Does this policy cover organ donor expenses?"
    ]
}

try:
    res = requests.post(url, headers=headers, json=data, timeout=30)  # Hackathon rule
    res.raise_for_status()
    print(json.dumps(res.json(), indent=2))
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")