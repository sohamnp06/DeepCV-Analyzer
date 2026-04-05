import subprocess, sys

if __name__ == "__main__":
    # Just run the consolidated start script
    try:
        subprocess.run([sys.executable, "start.py"])
    except KeyboardInterrupt:
        pass