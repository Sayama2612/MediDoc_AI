"""Launcher for the Flask app that reads PORT/HOST/DEBUG from environment.

Usage (PowerShell):
  $env:PORT = 5000; python run_server.py
  # or
  python run_server.py         # uses default PORT=8080, HOST=127.0.0.1

This file imports `src.web.app` and runs the `app` object. Importing this
module does NOT start the server (the server is started only when run as
__main__). That means other scripts can safely import it.
"""
import os
import sys
from importlib import import_module


def main():
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 8080)))
    debug = os.getenv('DEBUG', 'False').lower() in ('1', 'true', 'yes')

    # Import the Flask `app` from src.web.app
    try:
        mod = import_module('src.web.app')
    except Exception as e:
        print('Failed to import src.web.app:', e, file=sys.stderr)
        return 2

    app = getattr(mod, 'app', None)
    if app is None:
        print("No Flask 'app' object found in src.web.app", file=sys.stderr)
        return 3

    print(f"Starting Flask app from src.web.app on {host}:{port} (debug={debug})")
    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print('Error while running app:', e, file=sys.stderr)
        return 4

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
