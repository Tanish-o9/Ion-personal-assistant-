import json
import urllib.request
import urllib.error

payload = {
    "question": "Test Jarvis fast run",
    "context": [],
    "model": "claude",
}

request = urllib.request.Request(
    "http://127.0.0.1:8001/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

try:
    response = urllib.request.urlopen(request)
    print(response.read().decode("utf-8"))
except urllib.error.HTTPError as error:
    print("HTTP", error.code)
    print(error.read().decode("utf-8"))
except Exception as exc:
    print(type(exc).__name__, exc)
