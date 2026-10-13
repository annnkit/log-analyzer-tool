import re
from collections import Counter
from datetime import datetime

# Format 1: 2026-10-12 14:03:25 ERROR Database connection failed
LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>INFO|WARN|WARNING|ERROR|DEBUG|CRITICAL)\s+"
    r"(?P<message>.*)"
)

# Format 2: 192.168.1.11 - - [12/Oct/2026:14:03:27 +0000] "GET /api/orders HTTP/1.1" 500 87
ACCESS_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) [^"]*" '
    r'(?P<status>\d{3}) (?P<size>\S+)'
)


def parse_app_line(line):
    match = LOG_PATTERN.match(line.strip())
    return match.groupdict() if match else None


def parse_access_line(line):
    m = ACCESS_PATTERN.match(line.strip())
    if not m:
        return None

    status = int(m["status"])
    if status >= 500:
        level = "ERROR"
    elif status >= 400:
        level = "WARN"
    else:
        level = "INFO"

    try:
        when = datetime.strptime(m["time"].split()[0], "%d/%b/%Y:%H:%M:%S")
    except ValueError:
        return None

    return {
        "timestamp": when.strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "message": f'{m["method"]} {m["path"]} -> {status}',
    }


def parse_line(line):
    return parse_app_line(line) or parse_access_line(line)


def parse_lines(lines):
    entries = []
    for line in lines:
        entry = parse_line(line)
        if entry:
            entries.append(entry)
    return entries


def parse_file(path):
    with open(path, encoding="utf-8") as f:
        return parse_lines(f)


if __name__ == "__main__":
    entries = parse_file("sample_logs/app.log")
    levels = Counter(e["level"] for e in entries)
    errors = Counter(e["message"] for e in entries if e["level"] == "ERROR")

    print("Level counts:", dict(levels))
    print("Top errors:")
    for msg, count in errors.most_common(5):
        print(f"  {count}x {msg}")