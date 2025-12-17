import json
from urllib import request, error

payload = json.dumps({"features": list(range(1,21))}).encode()
req = request.Request('http://127.0.0.1:5000/predict', data=payload, headers={'Content-Type': 'application/json'})
try:
    resp = request.urlopen(req)
    print(resp.read().decode())
except error.HTTPError as e:
    print('STATUS', e.code)
    print(e.read().decode())
except Exception as e:
    print('ERROR', e)
