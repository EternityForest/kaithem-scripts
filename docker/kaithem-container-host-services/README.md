# kaithem-host-services

A small host-side helper that lets containers do PAM password checks against
the host without ever exposing PAM (or root) into the container.

- **Server**: a FastAPI app served by uvicorn on a **per-user** Unix-domain
  socket in `$XDG_RUNTIME_DIR/kaithem-host-services.sock` (mode `0o600`,
  owned by the running user).
- **Client**: importable as `kaithem_host_services.client.check_password`,
  with paranoid pre-flight + post-connect checks to make sure the socket
  isn't being hijacked by another local user.

## Install

```bash
cd docker/kaithem-container-host-services
./install.sh
```

This:

1. Runs `uv tool install .` from this directory.
2. Drops a `systemd --user` unit and enables it.
3. Prints the socket path.

To uninstall: `./uninstall.sh`.

## Running tests

```bash
uv venv
uv pip install -e '.[dev]'
python -m pytest
```

Tests spin up a real uvicorn instance on a per-user UDS in a temp directory
and exercise the client against it, including all the pre-flight + post-
connect safety checks. The "wrong password" test requires `python-pam`
(already installed by the package).

## API

```
POST /check_password   { "user": "...", "password": "..." }   →   { "ok": true|false }
GET  /health                                                     →   { "ok": true, "uid": 1000 }
```

The server never tells the client *why* authentication failed, to avoid
username enumeration.

## Client usage

```python
from kaithem_host_services.client import check_password

if check_password("alice", password_from_form):
    ...
```

The client will refuse to send a password if:

- The socket file is missing, not a socket, owned by another UID, has any
  group/other permission bits, or has more than one hardlink.
- The peer it actually connects to does not present `SO_PEERCRED`
  credentials whose `uid` matches the calling UID.
- The peer's reported PID is zero.

## Container setup

Mount the host socket into the container and point the client at it:

```yaml
volumes:
  - /run/user/${UID}/kaithem-host-services.sock:/run/user/${UID}/kaithem-host-services.sock:ro
environment:
  - XDG_RUNTIME_DIR=/run/user/${UID}
```

Then inside the container:

```python
from kaithem_host_services.client import check_password
```

## Security notes

- The socket is per-user. A different UID on the host cannot connect to
  yours, and yours cannot connect to theirs (the client refuses).
- PAM runs in the server process (host-side) using `python-pam`, which uses
  the host's default PAM stack. No special PAM service file is required.
- The server does no privileged work beyond PAM; it does not read
  `/etc/shadow` directly and does not need root.
