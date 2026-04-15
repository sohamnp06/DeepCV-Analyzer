import subprocess, sys

if __name__ == "__main__":
    try:
        subprocess.run([sys.executable, "start.py"])
    except KeyboardInterrupt:
        pass