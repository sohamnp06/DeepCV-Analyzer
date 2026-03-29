import os
import subprocess
import sys
import importlib.util
import socket


ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT, "frontend")
RUNTIME_CONFIG_PATH = os.path.join(FRONTEND_DIR, "runtime-config.js")
REQUIRED_MODULES = ["fastapi", "uvicorn", "psycopg2", "sklearn", "fitz"]
PACKAGE_BY_MODULE = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "psycopg2": "psycopg2-binary",
    "sklearn": "scikit-learn",
    "fitz": "PyMuPDF",
}


def ensure_dependencies():
    missing = [mod for mod in REQUIRED_MODULES if importlib.util.find_spec(mod) is None]
    if not missing:
        return
    missing_packages = [PACKAGE_BY_MODULE[m] for m in missing]
    print(f"Installing missing dependencies: {', '.join(missing_packages)}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages], cwd=ROOT)


def _is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def pick_backend_port(start=8000, end=8100):
    for port in range(start, end + 1):
        if _is_port_available(port):
            return port
    raise RuntimeError("No free backend port found between 8000 and 8100.")


def write_runtime_config(backend_port):
    api_base = f"http://127.0.0.1:{backend_port}"
    content = f"window.RUNTIME_CONFIG = {{ API_BASE: '{api_base}' }};\n"
    with open(RUNTIME_CONFIG_PATH, "w", encoding="utf-8") as config_file:
        config_file.write(content)


def main():
    ensure_dependencies()
    backend_port = pick_backend_port()
    write_runtime_config(backend_port)
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api_server:app", "--reload", "--host", "0.0.0.0", "--port", str(backend_port)],
        cwd=ROOT,
    )
    frontend = subprocess.Popen(
        [sys.executable, "-m", "http.server", "5500", "--bind", "0.0.0.0"],
        cwd=FRONTEND_DIR,
    )
    print(f"Backend running at http://127.0.0.1:{backend_port}")
    print("Frontend running at http://127.0.0.1:5500/landing.html")
    print("Press Ctrl+C to stop both.")

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        backend.terminate()
        frontend.terminate()


if __name__ == "__main__":
    main()
