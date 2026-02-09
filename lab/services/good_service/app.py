import time
from datetime import datetime
import random

levels = ["INFO", "INFO", "INFO", "WARN"]

messages = [
    "Healthcheck OK",
    "Worker heartbeat",
    "Processed batch successfully",
    "Cache warmed",
    "DB connection pool healthy",
    "Request handled: 200 OK",
]

while True:
    ts = datetime.utcnow().isoformat() + "Z"
    level = random.choice(levels)
    msg = random.choice(messages)
    print(f"{ts} [{level}] good_service: {msg}", flush=True)
    time.sleep(random.uniform(0.6, 1.4))

