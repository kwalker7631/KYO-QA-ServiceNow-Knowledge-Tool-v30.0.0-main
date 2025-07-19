import subprocess
import sys
import threading
import time

import webview


def _run_server():
    """Run the Flask server."""
    # We don't use check=True so the app continues even if server exits unexpectedly.
    subprocess.run([sys.executable, "server.py"])  # pragma: no cover - external process


def main():
    """Start the Flask server then open a PyWebView window."""
    # Launch the server in a background thread so the UI remains responsive.
    threading.Thread(target=_run_server, daemon=True).start()

    # Give the server a moment to start up.
    time.sleep(1)

    # Open the local web app in a native window.
    webview.create_window(
        "KYO QA Tool",
        "http://127.0.0.1:5000",
        width=1200,
        height=900,
    )
    webview.start()


if __name__ == "__main__":
    main()
