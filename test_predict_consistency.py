import sys
import requests

def main():
    url = "http://127.0.0.1:5000/predict"
    features = [0.90, 2.05, 3.03, 4.03, 5.00, 6.06, 7.00, 8.00, 9.00, 9.99, 11.00, 12.00, 13.00, 14.00, 15.00, 16.00, 17.02, 10.19, 19.01, 20.01]
    results = []
    for i in range(5):
        try:
            r = requests.post(url, json={"features": features}, timeout=5)
            r.raise_for_status()
        except Exception as e:
            print(f"REQUEST {i+1} FAILED: {e}")
            return 2
        try:
            data = r.json()
        except Exception as e:
            print(f"REQUEST {i+1}: invalid JSON response: {e}")
            return 2
        if 'price_range' not in data:
            print(f"REQUEST {i+1}: missing 'price_range' in response: {data}")
            return 2
        results.append(data['price_range'])
        print(f"REQUEST {i+1}: {data}")

    first = results[0]
    if all(r == first for r in results):
        print(f"PASS: all predictions identical: {first}")
        return 0
    else:
        print(f"FAIL: inconsistent predictions: {results}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
