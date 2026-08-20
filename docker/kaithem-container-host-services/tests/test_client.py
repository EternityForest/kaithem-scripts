"""End-to-end client tests against a real UDS server.

These intentionally do *not* test the correct-password case — that's covered
by any actual integration use. We focus on:

* Wrong password -> ``ok=False`` (and never a leaked reason in the response).
* Malformed input -> HTTP 422 from FastAPI, surfaced as AuthServerUnavailable.
* Every client safety check (wrong owner, bad mode, hardlink, peer uid
  mismatch, peer pid=0, missing socket, not-a-socket).
"""

from __future__ import annotations

import json
import os
import socket
from pathlib import Path

import pytest

from kaithem_host_services import client as client_mod


# ---- Server round-trip ----------------------------------------------------


def test_health_endpoint(server: Path) -> None:
    """A trivial HTTP/1.1 round trip against the live UDS proves the wiring."""
    body = _http_get(server, "/health")
    payload = json.loads(body)
    assert payload == {"ok": True, "uid": os.getuid()}


def test_wrong_password_returns_false_and_no_reason(server: Path, require_pam) -> None:
    """A clearly-bogus password must come back as ok=False with no leak."""
    body = _http_post(server, "/check_password", {"user": "root", "password": ""})
    payload = json.loads(body)
    assert payload == {"ok": False}
    # Server must never echo PAM failure reasons (avoids user enumeration).
    assert "reason" not in payload
    assert "error" not in payload


def test_empty_user_field_is_rejected(server: Path) -> None:
    """FastAPI/Pydantic validation -> HTTP 422, surfaced as AuthServerUnavailable."""
    from kaithem_host_services.client import AuthServerUnavailable

    with pytest.raises(AuthServerUnavailable) as ei:
        client_mod.check_password(socket_path=server, username="", password="x")
    # Pydantic rejects empty 'user' (min_length=1); we get HTTP 422 -> surfaced.
    assert "422" in str(ei.value)


# ---- Client safety checks -------------------------------------------------


def test_missing_socket(tmp_path: Path) -> None:
    from kaithem_host_services.client import AuthServerUnavailable, check_password

    with pytest.raises(AuthServerUnavailable):
        check_password(socket_path=tmp_path / "nope.sock", username="root", password="x")


def test_not_a_socket(tmp_path: Path) -> None:
    from kaithem_host_services.client import InsecureConnectionError, check_password

    p = tmp_path / "regular-file.sock"
    p.write_text("not a socket")
    with pytest.raises(InsecureConnectionError):
        check_password(socket_path=p, username="root", password="x")


def test_wrong_owner(tmp_path: Path) -> None:
    from kaithem_host_services.client import InsecureConnectionError, check_password

    p = tmp_path / "wrong-owner.sock"
    p.write_text("")
    st = os.stat(p)
    # Pick a UID that isn't ours. Skip if we can't chown (non-root).
    other_uid = 0 if os.getuid() != 0 else 65534
    if other_uid == os.getuid():
        pytest.skip("no other uid available to test with")
    try:
        os.chown(p, other_uid, -1)
    except PermissionError:
        pytest.skip("cannot chown to other uid (not root)")
    try:
        with pytest.raises(InsecureConnectionError):
            check_password(socket_path=p, username="root", password="x")
    finally:
        # Restore so cleanup can remove it.
        try:
            os.chown(p, st.st_uid, st.st_gid)
        except (PermissionError, OSError):
            pass


def test_group_or_other_bits(tmp_path: Path) -> None:
    from kaithem_host_services.client import InsecureConnectionError, check_password

    p = tmp_path / "loose-mode.sock"
    p.write_text("")
    os.chmod(p, 0o644)
    with pytest.raises(InsecureConnectionError):
        check_password(socket_path=p, username="root", password="x")


def test_hardlinked_socket(tmp_path: Path) -> None:
    from kaithem_host_services.client import InsecureConnectionError, check_password

    src = tmp_path / "src.sock"
    src.write_text("")
    os.chmod(src, 0o600)
    other = tmp_path / "link.sock"
    os.link(src, other)
    assert os.stat(other).st_nlink == 2
    with pytest.raises(InsecureConnectionError):
        check_password(socket_path=other, username="root", password="x")


def test_peer_uid_mismatch(server: Path, monkeypatch) -> None:
    """The client must refuse if SO_PEERCRED reports a uid other than ours.

    The kernel reports the peer's *real* uid, so we can't make a child process
    lie about it. Instead we patch the post-connect getsockopt to return
    crafted credentials, which exercises the exact safety code path that
    protects against a MITM handing our connection off to a server running
    as another user.
    """
    from kaithem_host_services.client import InsecureConnectionError, check_password

    other_uid = 0 if os.getuid() != 0 else 65534
    if other_uid == os.getuid():
        pytest.skip("no other uid available to test with")

    class FakeSocket:
        def __init__(self):
            self._buf = bytearray()
            self.closed = False

        def settimeout(self, _t):
            pass

        def connect(self, _path):
            pass

        def getsockopt(self, level, optname, length):
            assert level == socket.SOL_SOCKET
            assert optname == socket.SO_PEERCRED
            # (pid=42, uid=other_uid, gid=other_uid) — wrong on purpose.
            return (42, other_uid, other_uid)

        def sendall(self, data):
            if self.closed:
                raise OSError("closed")
            # Pretend we accepted the data; respond with a tiny HTTP 200.
            self._buf.extend(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: 12\r\n"
                b"Connection: close\r\n\r\n"
                b'{"ok": false}'
            )

        def recv(self, _n):
            if self._buf:
                return bytes(self._buf[:_n]) if _n < len(self._buf) else bytes(self._buf)
            return b""

        def close(self):
            self.closed = True

    fake = FakeSocket()
    monkeypatch.setattr(socket, "socket", lambda *a, **kw: fake)

    with pytest.raises(InsecureConnectionError) as ei:
        check_password(socket_path=server, username="root", password="x")
    assert f"uid={other_uid}" in str(ei.value)


def test_peer_pid_zero_is_rejected(server: Path, monkeypatch) -> None:
    """A peer that reports pid=0 is bogus and must be refused."""
    from kaithem_host_services.client import InsecureConnectionError, check_password

    class FakeSocket:
        def settimeout(self, _t): pass
        def connect(self, _p): pass
        def getsockopt(self, *a, **kw):
            # pid=0, uid=ours, gid=ours — should still fail on pid check.
            return (0, os.getuid(), os.getgid())
        def sendall(self, _d): pass
        def recv(self, _n): return b""
        def close(self): pass

    monkeypatch.setattr(socket, "socket", lambda *a, **kw: FakeSocket())
    with pytest.raises(InsecureConnectionError) as ei:
        check_password(socket_path=server, username="root", password="x")
    assert "pid=0" in str(ei.value)


# ---- helpers --------------------------------------------------------------


def _http_get(sock_path: Path, path: str) -> str:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(5.0)
        s.connect(str(sock_path))
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: localhost\r\n"
            f"Connection: close\r\n\r\n"
        ).encode("ascii")
        s.sendall(req)
        return _read_http_body(s)


def _http_post(sock_path: Path, path: str, payload: dict) -> str:
    body = json.dumps(payload).encode("utf-8")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(5.0)
        s.connect(str(sock_path))
        req = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: localhost\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Connection: close\r\n\r\n"
        ).encode("ascii") + body
        s.sendall(req)
        return _read_http_body(s)


def _read_http_body(s: socket.socket) -> str:
    buf = bytearray()
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        buf.extend(chunk)
    text = bytes(buf).decode("iso-8859-1", errors="replace")
    return text.partition("\r\n\r\n")[2]



