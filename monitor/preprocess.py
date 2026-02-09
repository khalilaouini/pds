# monitor/preprocess.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Optional


@dataclass(frozen=True)
class LogEvent:
    container: str
    timestamp: datetime
    level: str
    message: str
    raw: str


# Example expected formats:
# 2026-02-01T12:34:56.123Z [INFO] service: message
# 2026-02-01T12:34:56Z [ERROR] bug_service: something
_TS_RE = r"(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)"
_LVL_RE = r"\[(?P<lvl>INFO|WARN|ERROR|DEBUG|TRACE)\]"
_LINE_RE = re.compile(rf"^\s*{_TS_RE}\s+{_LVL_RE}\s+(?P<rest>.*)\s*$")


def _parse_iso_z(ts: str) -> datetime:
    # Convert "....Z" to timezone-aware datetime in UTC
    # datetime.fromisoformat doesn't accept trailing Z directly in older versions.
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


def parse_log_line(container: str, line: str) -> LogEvent:
    raw = line.rstrip("\n")

    m = _LINE_RE.match(raw)
    if m:
        ts = _parse_iso_z(m.group("ts"))
        lvl = m.group("lvl")
        msg = m.group("rest").strip()
        return LogEvent(container=container, timestamp=ts, level=lvl, message=msg, raw=raw)

    # Fallback parsing (best-effort):
    # If no timestamp/level, mark timestamp as now, level as INFO
    now = datetime.now(timezone.utc)
    return LogEvent(container=container, timestamp=now, level="INFO", message=raw.strip(), raw=raw)

