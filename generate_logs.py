import random
from datetime import datetime, timedelta

LEVELS = ["INFO", "WARN", "ERROR"]
WEIGHTS = [70, 20, 10]

MESSAGES = {
    "INFO": ["Server started", "User logged in", "Request completed", "Cache refreshed"],
    "WARN": ["Slow response: 2.4s", "Disk usage at 85%", "Retrying request"],
    "ERROR": ["Database connection failed", "Payment gateway timeout", "File not found", "Out of memory"],
}

START = datetime(2026, 10, 14, 8, 0, 0)
FILENAME = "sample_logs/incident.log"
ADD_INCIDENT = True

lines = []
current = START
for _ in range(500):
    current += timedelta(seconds=random.randint(1, 60))
    level = random.choices(LEVELS, weights=WEIGHTS)[0]
    message = random.choice(MESSAGES[level])
    lines.append((current, level, message))

if ADD_INCIDENT:
    # 15 database errors, 3 seconds apart, starting at 10:13
    burst_start = START + timedelta(hours=2, minutes=13)
    for i in range(15):
        lines.append((burst_start + timedelta(seconds=i * 3), "ERROR", "Database connection failed"))

lines.sort()   # keep everything in time order

with open(FILENAME, "w") as f:
    for ts, level, message in lines:
        f.write(f"{ts.strftime('%Y-%m-%d %H:%M:%S')} {level} {message}\n")

print(f"Generated {FILENAME}")