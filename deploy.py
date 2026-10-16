"""Run `python deploy.py`. No Node.js is required to use the bundled dashboard."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import venv
import webbrowser

ROOT = Path(__file__).resolve().parent


def read_env():
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            var_name = name.strip()
            var_val = value.strip().strip('"').strip("'")
            if var_name:
                os.environ.setdefault(var_name, var_val)


def ensure_environment():
    directory = ROOT / ".venv"
    python = directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        print("Creating this project's Python environment...", flush=True)
        venv.EnvBuilder(with_pip=True).create(directory)
    requirements = ROOT / "requirements.txt"
    digest = hashlib.sha256(requirements.read_bytes()).hexdigest()
    stamp = directory / ".requirements-hash"
    if not stamp.exists() or stamp.read_text().strip() != digest:
        print("Installing application dependencies. The first run needs internet access...", flush=True)
        subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(requirements)], check=True, cwd=ROOT)
        stamp.write_text(digest)
    return python


def port_is_free(port):
    with socket.socket() as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def open_when_ready(url, process):
    for _ in range(100):
        if process.poll() is not None:
            return
        try:
            with urllib.request.urlopen(url+"/api/health", timeout=1) as response:
                data = json.load(response)
            if data.get("application") == "marketing-manager":
                webbrowser.open(url)
                return
        except Exception:
            time.sleep(0.3)
    print("The browser did not open automatically. Use the local address shown above.", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Install and start AI Marketing Manager locally.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--setup-only", action="store_true")
    parser.add_argument("--no-install", action="store_true", help="Use the current Python; dependencies must already be installed.")
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error("Python 3.11 or newer is required. Install Python and enable Add Python to PATH.")
    if not 1024 <= args.port <= 65535:
        parser.error("Choose a port between 1024 and 65535.")
    if not (ROOT / "frontend" / "dist" / "index.html").exists():
        parser.error("The bundled dashboard is missing. Extract the full project ZIP, not just deploy.py.")
    read_env()
    try:
        python = Path(sys.executable) if args.no_install else ensure_environment()
    except (OSError, subprocess.CalledProcessError) as exc:
        print("Setup could not finish. Check internet access and Python installation, then run python deploy.py again.")
        return 1
    if args.setup_only:
        print("Setup complete. Start the app with: python deploy.py")
        return 0
    if not port_is_free(args.port):
        print(f"Port {args.port} is already in use. Close the other app, or run: python deploy.py --port {args.port+1}")
        return 1
    os.environ["MARKETING_PORT"] = str(args.port)
    url = f"http://127.0.0.1:{args.port}"
    print(f"\nAI Marketing Manager: {url}\nPublishing simulator enabled. Keep this terminal open; press Ctrl+C to stop.\n", flush=True)
    process = subprocess.Popen([str(python), "-m", "uvicorn", "app.main:create_app", "--factory", "--host", "127.0.0.1", "--port", str(args.port)], cwd=ROOT)
    if not args.no_browser:
        threading.Thread(target=open_when_ready, args=(url, process), daemon=True).start()
    try:
        return process.wait()
    except KeyboardInterrupt:
        print("\nStopping the local application. Campaign progress is saved.")
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
