"""Pytest fixtures for end-to-end tests against a real UDS."""

from __future__ import annotations

import os
import socket
import stat
import threading
import time
from pathlib import Path

import pytest

from kaithem_host_services.server import _bind_listening_socket, create_app


def _is_socket(path: Path) -> bool:
    try:
        return stat.S_ISSOCK(path.stat().st_mode)
    except FileNotFoundError:
        return False


def _wait_for_socket(path: Path, timeout: float = 5.0) -> None:
    """Poll until the UDS file exists and accepts connections."""
    deadline = time.monotonic() + timeout
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        if _is_socket(path):
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    s.connect(str(path))
                return
            except OSError as e:
                last_err = e
        time.sleep(0.02)
    raise RuntimeError(f"server never became reachable at {path}: {last_err!r}")


@pytest.fixture()
def server(tmp_path: Path) -> Path:
    """Start the FastAPI app via uvicorn on a fresh per-user UDS and tear it down.

    Returns the socket path. The socket is mode 0o600 owned by the test user,
    exactly like a real install.
    """
    import uvicorn

    sock = tmp_path / "host-services.sock"
    listener = _bind_listening_socket(sock)

    config = uvicorn.Config(
        app=create_app(),
        uds=str(sock),
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
    thread.start()

    try:
        _wait_for_socket(sock)
        yield sock
    finally:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.fixture()
def require_pam():
    """Skip if python-pam isn't installed on this host."""
    pytest.importorskip("pam")
