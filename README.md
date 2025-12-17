# Mobile Price Prediction API

Simple Flask app exposing a `/predict` endpoint that expects JSON input and returns a `price_range` prediction.

Quick start (development):

```bash
# create a venv (recommended)
python -m venv .venv
# activate venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# install dependencies
pip install -r requirements.txt
# run locally (debug mode off by default)
python app.py
# to enable debug mode
set FLASK_DEBUG=1
python app.py
```

Run with Waitress (production-friendly on Windows):

```bash
pip install waitress
# Option A: use the CLI
waitress-serve --host=0.0.0.0 --port=5000 app:app

# Option B: use the included wrapper (preferred for convenience)
python serve.py
```

API usage example:

```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H 'Content-Type: application/json' \
  -d '{"features": [12,3,1,0, ...]}'
```

Notes:
- Place your trained model at `mobile_price_model.pkl` in the project root.
- Endpoint accepts either `{"features": [...]}` or a bare JSON list `[...]`.
