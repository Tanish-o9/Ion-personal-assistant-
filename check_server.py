import urllib.request

try:
    data = urllib.request.urlopen('http://127.0.0.1:8001/api/analytics', timeout=5).read().decode('utf-8')
    print('OK')
    print(data)
except Exception as exc:
    print('ERROR')
    print(exc)
