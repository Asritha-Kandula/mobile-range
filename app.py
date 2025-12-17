from flask import Flask, request, jsonify
import joblib
import numpy as np
import os
import argparse
import json
from datetime import datetime

# File to append prediction logs (JSON-lines)
LOG_PATH = os.path.join(os.path.dirname(__file__), 'predictions.log')

app = Flask(__name__)

# Load trained model safely
MODEL_PATH = os.path.join(os.path.dirname(__file__), "mobile_price_model.pkl")
model = None
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    # Keep application running but return errors on predict until model is available
    app.logger.error(f"Failed to load model from {MODEL_PATH}: {e}")
    # Also print to console so running the script shows the problem immediately
    print(f"ERROR: Failed to load model from {MODEL_PATH}: {e}")


@app.route('/')
def home():
    return "Mobile Price Prediction API is running"


@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    payload = request.get_json()

    # Accept either {"features": [...]} or a bare list
    if isinstance(payload, dict) and 'features' in payload:
        features = payload['features']
    elif isinstance(payload, list):
        features = payload
    else:
        return jsonify({"error": "Invalid payload. Expected {'features': [...]} or a list."}), 400

    try:
        data = np.array(features, dtype=float).reshape(1, -1)
    except Exception:
        return jsonify({"error": "Features must be a list of numeric values."}), 400

    # Optional: validate feature length if model exposes it
    expected = getattr(model, 'n_features_in_', None)
    if expected is not None and data.shape[1] != expected:
        return (
            jsonify({"error": f"Invalid number of features: expected {expected}, got {data.shape[1]}"}),
            400,
        )

    try:
        prediction = model.predict(data)
    except Exception as e:
        app.logger.error(f"Prediction error: {e}")
        return jsonify({"error": "Prediction failed"}), 500

    # Log the prediction (timestamp, features, prediction, client)
    try:
        client = request.headers.get('X-Forwarded-For', request.remote_addr)
        log_entry = {
            "ts": datetime.utcnow().isoformat() + 'Z',
            "client": client,
            "features": features,
            "prediction": int(prediction[0])
        }
        with open(LOG_PATH, 'a', encoding='utf-8') as fh:
            fh.write(json.dumps(log_entry) + '\n')
    except Exception:
        app.logger.exception('Failed to write prediction log')

    return jsonify({"price_range": int(prediction[0])})


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint. Returns 200 if model is loaded, 503 otherwise."""
    loaded = model is not None
    payload = {"model_loaded": loaded}
    if loaded:
        payload["n_features_in"] = getattr(model, 'n_features_in_', None)
        return jsonify(payload), 200
    return jsonify(payload), 503


if __name__ == '__main__':
    # Read runtime configuration from environment for safer defaults in CI/IDE
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    port = int(os.getenv('PORT', '5000'))

    # Add CLI parser for quick diagnostics
    parser = argparse.ArgumentParser(description='Mobile Price API helpers')
    parser.add_argument('--check-model', action='store_true', help='Check if model loads and exit (print details)')
    args = parser.parse_args()

    if args.check_model:
        if model is None:
            print(f"MODEL CHECK: FAILED - model not loaded from {MODEL_PATH}")
            exit(1)
        else:
            print(f"MODEL CHECK: OK - model loaded from {MODEL_PATH}")
            info = getattr(model, 'n_features_in_', None)
            if info is not None:
                print(f"MODEL INFO: n_features_in_ = {info}")
            exit(0)

    # Prefer running with Waitress to avoid the Flask development-server warning
    # (and to avoid signal/reloader issues in some IDEs). If Waitress is not
    # available, fall back to Flask's development server.
    use_waitress = os.getenv('USE_WAITRESS', '1') in ('1', 'true', 'True')
    if use_waitress:
        try:
            from waitress import serve

            print(f"Starting Waitress on http://0.0.0.0:{port} (Press CTRL+C to quit)")
            app.logger.info(f"Starting Waitress on 0.0.0.0:{port}")
            serve(app, host='0.0.0.0', port=port)
            # `serve` blocks; when it returns the process is shutting down
        except Exception as e:
            print(f"Waitress not available ({e}); falling back to Flask server")
            app.logger.warning(f"Waitress unavailable ({e}); falling back to Flask server")

    # Final fallback to Flask development server (debug off by default)
    print(f"Starting Flask development server on http://0.0.0.0:{port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
