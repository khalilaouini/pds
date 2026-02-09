import time
from datetime import datetime
import random

noisy = [
    ("WARN", "sshd: Failed password for invalid user admin from 203.0.113.10 port 51234 ssh2"),
    ("WARN", "sshd: Failed password for root from 198.51.100.23 port 42011 ssh2"),
    ("WARN", "kernel: IN=eth0 OUT= MAC=... SRC=192.0.2.55 DST=172.17.0.2 LEN=60 TOS=0x00 SYN"),
    ("ERROR", "nginx: connect() failed (111: Connection refused) while connecting to upstream"),
    ("ERROR", "app: dependency timeout: redis:6379 unreachable"),
    ("WARN", "portscan: multiple connection attempts detected to ports 22, 80, 443, 3306"),
]

while True:
    ts = datetime.utcnow().isoformat() + "Z"
    level, msg = random.choice(noisy)
    print(f"{ts} [{level}] noisy_service: {msg}", flush=True)
    time.sleep(random.uniform(0.2, 0.6))

