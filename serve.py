import os

# Prefer production server on demand to avoid Flask development warning
USE_WAITRESS = os.getenv('USE_WAITRESS', '1') in ('1', 'true', 'True')
PORT = int(os.getenv('PORT', 5000))

if USE_WAITRESS:
    try:
        from waitress import serve
        import app as app_module

        print(f"Starting Waitress on 0.0.0.0:{PORT}")
        serve(app_module.app, host='0.0.0.0', port=PORT)
    except Exception as e:
        print("Failed to start Waitress:", e)
        raise
else:
    # Fallback to Flask development server (not recommended for production)
    from app import app

    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=PORT, debug=debug, use_reloader=False)
