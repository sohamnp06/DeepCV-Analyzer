import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT, "frontend")


def main():
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api_server:app", "--reload", "--port", "8000"],
        cwd=ROOT,
    )
    frontend = subprocess.Popen(
        [sys.executable, "-m", "http.server", "5500"],
        cwd=FRONTEND_DIR,
    )
    print("Backend running at http://127.0.0.1:8000")
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
