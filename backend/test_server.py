import subprocess
import time
import sys

print("Starting Flask server...")
proc = subprocess.Popen(
    [sys.executable, "app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

try:
    for i in range(30):
        line = proc.stdout.readline()
        if line:
            print(line.rstrip())
            if "[OK]" in line or "Running" in line or "ERROR" in line:
                pass
            if "Running on" in line:
                print("\n=== SERVER STARTED SUCCESSFULLY ===")
                break
        time.sleep(0.5)
finally:
    proc.terminate()
    proc.wait(timeout=5)
