"""Uvicorn server: FastAPI app exposing PAM-backed auth over a Unix-domain socket."""

from __future__ import annotations

import logging
import os
import socket
import stat
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .auth import check_password
from .socket_path import default_socket_path

log = logging.getLogger("kaithem-host-services")


class CheckPasswordRequest(BaseModel):
    user: str = Field(..., min_length=1, max_length=256)
    password: str = Field(..., max_length=1024)


class CheckPasswordResponse(BaseModel):
    ok: bool


def create_app() -> FastAPI:
    app = FastAPI(title="kaithem-host-services", docs_url=None, redoc_url=None)

    @app.get("/health")
    def health() -> dict:
        return {"ok": True, "uid": os.getuid()}

    @app.post("/check_password", response_model=CheckPasswordResponse)
    def check(req: CheckPasswordRequest) -> CheckPasswordResponse:
        ok, reason = check_password(req.user, req.password)
        # Never tell the client *why* auth failed (avoid user enumeration).
        if not ok:
            log.info("auth rejected for user=%r: %s", req.user, reason)
        return CheckPasswordResponse(ok=ok)

    @app.exception_handler(Exception)
    async def _unhandled(_request, exc: Exception):  # pragma: no cover - defensive
        log.exception("unhandled error")
        raise HTTPException(status_code=500, detail="internal error")

    return app


def _bind_listening_socket(path: Path) -> socket.socket:
    """Bind a UDS with 0o600 perms owned by us, and start listening.

    We bind the socket ourselves because newer uvicorn dropped the
    ``uds_permissions`` / ``uds_owner`` ``Config`` knobs. Binding first also
    means the socket exists with the right mode before any client tries to
    connect.
    """
    if path.exists():
        try:
            st = path.stat()
        except FileNotFoundError:
            st = None
        if st is not None:
            if not stat.S_ISSOCK(st.st_mode):
                raise RuntimeError(f"{path} exists and is not a socket; refusing to remove")
            if st.st_uid != os.getuid():
                raise RuntimeError(
                    f"{path} exists and is owned by uid {st.st_uid}; refusing to remove"
                )
            path.unlink()

    path.parent.mkdir(parents=True, exist_ok=True)

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.bind(str(path))
    except OSError:
        s.close()
        raise

    try:
        os.chmod(path, 0o600)
    except OSError:
        s.close()
        raise

    try:
        os.chown(path, os.getuid(), os.getgid())
    except (PermissionError, OSError):
        # Non-root or filesystem without chown; chmod is enough because the
        # socket already lives in a directory only we can write to.
        pass

    s.listen(128)
    return s


def serve(socket_path: Path | None = None) -> None:
    sock = socket_path or default_socket_path()

    listener = _bind_listening_socket(sock)

    config = uvicorn.Config(
        app=create_app(),
        uds=str(sock),
        log_level="info",
        access_log=False,
    )
    server = uvicorn.Server(config)
    log.info("listening on %s (uid=%d)", sock, os.getuid())
    # Pass our already-bound listener so uvicorn doesn't recreate the socket.
    server.run(sockets=[listener])
