import sys
import re
import subprocess
from collections import deque

# Start the ping process
ping_proc = subprocess.Popen(
    ["ping", "google.com"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True
)

avg_window = deque(maxlen=20)

try:
    for line in ping_proc.stdout:
        match = re.search(r"time=(\d+\.\d+)", line)
        if match:
            t = float(match.group(1))
            avg_window.append(t)
            avg = sum(avg_window) / len(avg_window)
            diff = t - avg
            if diff > 20:
                print(f"\033[97;41m{line.strip()}\033[0m")  # red text on white bg
            elif diff > 0:
                print(f"\033[91m{line.strip()}\033[0m")     # red text
            else:
                print(f"\033[92m{line.strip()}\033[0m")     # green text
        else:
            print(line.strip())
except KeyboardInterrupt:
    ping_proc.terminate()
    print("\nExiting.")

