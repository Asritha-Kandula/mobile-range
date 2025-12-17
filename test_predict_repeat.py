import requests
import time

features = [0.90, 2.05, 3.03, 4.03, 5.00, 6.06, 7.00, 8.00, 9.00, 9.99, 11.00, 12.00, 13.00, 14.00, 15.00, 16.00, 17.02, 10.19, 19.01, 20.01]
url = "http://127.0.0.1:5000/predict"

results = []
for i in range(10):
    try:
        r = requests.post(url, json={"features": features}, timeout=5)
        r.raise_for_status()
        data = r.json()
        print(i+1, '->', r.status_code, data)
        results.append(data)
    except Exception as e:
        print(i+1, 'ERROR', e)
    time.sleep(0.2)

# Summary
from collections import Counter
cnt = Counter([r.get('price_range') for r in results if isinstance(r, dict)])
print('\nSummary:', dict(cnt))
