# monitor/features.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import re
from collections import Counter

from monitor.preprocess import LogEvent

# Keywords used for simple hits (case-insensitive)
KEYWORDS = [
    "exception", "traceback", "failed", "refused", "timeout", "unauthorized", "forbidden",
    "curl", "base64", "chmod", "/tmp", "reverse shell", "failed password", "portscan",
]

# Regex patterns (case-insensitive) for stronger detections
PATTERNS = {
    "curl_pipe_bash": re.compile(r"curl\s+.+\|\s*bash", re.IGNORECASE),
    "base64_decode": re.compile(r"base64\s+-d|base64\s+--decode", re.IGNORECASE),
    "reverse_shell": re.compile(r"/dev/tcp/\d{1,3}(?:\.\d{1,3}){3}/\d+", re.IGNORECASE),
    "failed_password": re.compile(r"failed password", re.IGNORECASE),
    "port_scan": re.compile(r"portscan|multiple connection attempts|nmap", re.IGNORECASE),
}

LEVELS = ("DEBUG", "INFO", "WARN", "ERROR")


@dataclass(frozen=True)
class WindowFeatures:
    container: str
    total: int
    debug: int
    info: int
    warn: int
    error: int
    uniq_ratio: float          # unique messages / total
    repeat_ratio: float        # 1 - uniq_ratio
    keyword_hits: Dict[str, int]
    pattern_hits: Dict[str, int]

    def to_dict(self) -> dict:
        return {
            "container": self.container,
            "total": self.total,
            "debug": self.debug,
            "info": self.info,
            "warn": self.warn,
            "error": self.error,
            "uniq_ratio": self.uniq_ratio,
            "repeat_ratio": self.repeat_ratio,
            "keyword_hits": dict(self.keyword_hits),
            "pattern_hits": dict(self.pattern_hits),
        }


def _normalize_level(level: str) -> str:
    lvl = (level or "").strip().upper()
    return lvl if lvl in LEVELS else "INFO"


def compute_features(container: str, events: List[LogEvent]) -> WindowFeatures:
    total = len(events)
    lvl_counts = Counter(_normalize_level(e.level) for e in events)

    messages = [e.message.strip() for e in events if e.message]
    uniq = len(set(messages)) if total else 0
    uniq_ratio = (uniq / total) if total else 0.0
    repeat_ratio = (1.0 - uniq_ratio) if total else 0.0

    # keyword hits
    kw_counts: Dict[str, int] = {k: 0 for k in KEYWORDS}
    for e in events:
        msg_l = (e.message or "").lower()
        for k in KEYWORDS:
            if k in msg_l:
                kw_counts[k] += 1

    # pattern hits
    pat_counts: Dict[str, int] = {name: 0 for name in PATTERNS.keys()}
    for e in events:
        msg = e.message or ""
        for name, rx in PATTERNS.items():
            if rx.search(msg):
                pat_counts[name] += 1

    return WindowFeatures(
        container=container,
        total=total,
        debug=lvl_counts.get("DEBUG", 0),
        info=lvl_counts.get("INFO", 0),
        warn=lvl_counts.get("WARN", 0),
        error=lvl_counts.get("ERROR", 0),
        uniq_ratio=round(uniq_ratio, 4),
        repeat_ratio=round(repeat_ratio, 4),
        keyword_hits=kw_counts,
        pattern_hits=pat_counts,
    )

