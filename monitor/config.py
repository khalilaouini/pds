# monitor/config.py
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class MonitorConfig:
    containers: List[str]
    follow: bool = True
    tail: int = 50              # initial tail lines per container
    docker_base_url: str | None = None  # None = use env / default socket
    timezone: str = "UTC"


DEFAULT_CONFIG = MonitorConfig(
    containers=[
        "good_service",
        "bug_service",
        "suspicious_service",
        "noisy_service",
    ],
    follow=True,
    tail=50,
)

