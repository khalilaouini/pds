# monitor/run_monitor.py
from __future__ import annotations

import signal
import sys
import time
from collections import defaultdict
from datetime import timezone

from monitor.config import DEFAULT_CONFIG
from monitor.docker_logs import DockerLogStreamer
from monitor.preprocess import parse_log_line, LogEvent
from monitor.features import compute_features
from monitor.rules import apply_rules


WINDOW_SECONDS = 10


def format_event(evt: LogEvent) -> str:
    ts = evt.timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return f"{ts} {evt.container} {evt.level}: {evt.message}"


def main() -> int:
    cfg = DEFAULT_CONFIG

    buffers: dict[str, list[LogEvent]] = defaultdict(list)
    last_flush = time.time()

    def on_line(container: str, raw_line: str) -> None:
        evt = parse_log_line(container, raw_line)
        buffers[container].append(evt)
        # Optional debug line:
        # print(format_event(evt), flush=True)

    streamer = DockerLogStreamer(
        containers=cfg.containers,
        callback=on_line,
        follow=cfg.follow,
        tail=cfg.tail,
        docker_base_url=cfg.docker_base_url,
    )

    def shutdown(*_args) -> None:
        print("\n[monitor] shutting down...", flush=True)
        streamer.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("[monitor] starting log streams...", flush=True)
    streamer.start()

    while True:
        time.sleep(0.25)
        now = time.time()
        if now - last_flush >= WINDOW_SECONDS:
            last_flush = now

            print(f"\n[monitor] window flush ({WINDOW_SECONDS}s)", flush=True)
            for container, evts in list(buffers.items()):
                if not evts:
                    continue

                feat = compute_features(container, evts)
                hits = apply_rules(feat)

                print(f"  - {container}: total={feat.total} err={feat.error} warn={feat.warn} repeat={feat.repeat_ratio}", flush=True)

                # Print top evidence (only non-zero hits)
                nonzero_kw = {k: v for k, v in feat.keyword_hits.items() if v > 0}
                nonzero_pat = {k: v for k, v in feat.pattern_hits.items() if v > 0}
                if nonzero_kw:
                    print(f"      keyword_hits={nonzero_kw}", flush=True)
                if nonzero_pat:
                    print(f"      pattern_hits={nonzero_pat}", flush=True)

                if hits:
                    for h in hits:
                        print(f"      RULE {h.severity} {h.issue_type}: {h.reason}", flush=True)
                else:
                    print("      RULE none", flush=True)

                # Clear window buffer for that container
                buffers[container].clear()

    # unreachable
    # return 0


if __name__ == "__main__":
    raise SystemExit(main())

