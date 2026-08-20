"""PAM-backed credential check."""

from __future__ import annotations

from typing import Tuple

try:
    import pam  # type: ignore
except Exception:  # pragma: no cover - import guard
    pam = None  # type: ignore


def check_password(username: str, password: str) -> Tuple[bool, str]:
    """Return ``(ok, reason)`` for the given username/password pair.

    ``reason`` is suitable for server logs but should never be returned to
    the network client (it can reveal whether a username exists).
    """
    if pam is None:
        return False, "python-pam not available on host"

    if not username or password is None:
        return False, "missing username or password"

    try:
        p = pam.authenticate()  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - some builds expose `pam` directly
        p = pam  # type: ignore[assignment]

    try:
        ok = bool(p.authenticate(username, password))  # type: ignore[union-attr]
    except Exception as e:  # pragma: no cover - pam raises on internal errors
        return False, f"pam error: {e!r}"

    return ok, "ok" if ok else "pam rejected"
