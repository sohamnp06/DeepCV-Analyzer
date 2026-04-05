"""
Start script — launches BOTH backend (8000) and frontend (3000)
Consolidated into a clean launcher for local dev.
"""
import subprocess, sys, os, time, socket

ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND = os.path.join(ROOT, "frontend")

def wait_for_port(port, host='localhost', timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (socket.timeout, ConnectionRefusedError):
            time.sleep(1)
    return False

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print("🚀 DeepCV Analyzer — Multi-Port Dev Environment")
    print("=" * 60)

    # 1. Start Backend
    print("[1/2] Launching Backend on port 8080... (Preloading models)")
    log_file = open("backend.log", "w", encoding="utf-8")
    backend = subprocess.Popen(
        [sys.executable, "api_server.py"],
        cwd=ROOT,
        env={**os.environ, "PORT": "8080"},
        stdout=log_file,
        stderr=subprocess.STDOUT
    )

    # 2. Start Frontend
    print("[2/2] Launching Frontend on port 3000...")
    frontend = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000"],
        cwd=FRONTEND,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )

    # Wait for things to be ready
    if wait_for_port(8080, host='127.0.0.1') and wait_for_port(3000, host='127.0.0.1'):
        print("\n" + " ✅ READY! Servers are running. " .center(60, "-"))
        print(f" 🌐 Frontend : http://127.0.0.1:3000/landing.html")
        print(f" ⚡ Backend  : http://127.0.0.1:8080")
        print("-" * 60)
        print("\n ⚠️  IMPORTANT: KEEP THIS TERMINAL OPEN while using the app.")
        print("    If you close this window, the backend will stop working.")
    else:
        print("\n ⚠️  Warning: Backend or Frontend took too long to start.")
        print(" Check if another process is using port 8080 or 3000.")

    print("\n [Press Ctrl+C to shutdown both servers]")

    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down servers...")
        backend.terminate()
        frontend.terminate()
        print("Cleaning up... Done.")
