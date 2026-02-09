# monitor/docker_logs.py
from __future__ import annotations

import threading
from typing import Callable, Optional

import docker
from docker.errors import NotFound, APIError


LogCallback = Callable[[str, str], None]
# callback(container_name, raw_line)


class DockerLogStreamer:
    """
    Streams logs from multiple containers concurrently.
    Calls callback(container, line) for each decoded log line.
    """

    def __init__(
        self,
        containers: list[str],
        callback: LogCallback,
        follow: bool = True,
        tail: int = 50,
        docker_base_url: Optional[str] = None,
    ) -> None:
        self.containers = containers
        self.callback = callback
        self.follow = follow
        self.tail = tail
        self.client = docker.DockerClient(base_url=docker_base_url) if docker_base_url else docker.from_env()
        self._threads: list[threading.Thread] = []
        self._stop_event = threading.Event()

    def start(self) -> None:
        self._stop_event.clear()
        for name in self.containers:
            t = threading.Thread(target=self._stream_one, args=(name,), daemon=True)
            t.start()
            self._threads.append(t)

    def stop(self) -> None:
        self._stop_event.set()
        # Threads are daemon; stop flag will end loops gracefully.

    def join(self, timeout: Optional[float] = None) -> None:
        for t in self._threads:
            t.join(timeout=timeout)

    def _stream_one(self, container_name: str) -> None:
        try:
            container = self.client.containers.get(container_name)
        except NotFound:
            self.callback(container_name, f"[ERROR] container not found: {container_name}")
            return
        except APIError as e:
            self.callback(container_name, f"[ERROR] Docker API error getting {container_name}: {e}")
            return

        try:
            stream = container.logs(stream=True, follow=self.follow, tail=self.tail)
            for chunk in stream:
                if self._stop_event.is_set():
                    break
                try:
                    line = chunk.decode("utf-8", errors="replace")
                except Exception:
                    line = str(chunk)
                # Split in case chunk contains multiple lines
                for one_line in line.splitlines():
                    if one_line.strip():
                        self.callback(container_name, one_line)
        except APIError as e:
            self.callback(container_name, f"[ERROR] Docker API error streaming {container_name}: {e}")

