import json
import urllib.request
import urllib.error

payload = {
    "question": "run the model on the server fast",
    "context": [],
    "model": "claude",
}

req = urllib.request.Request(
    "http://127.0.0.1:8001/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode("utf-8"))
except urllib.error.HTTPError as error:
    print("HTTP", error.code)
    print(error.read().decode("utf-8"))
except Exception as exc:
    print(type(exc).__name__, exc)
