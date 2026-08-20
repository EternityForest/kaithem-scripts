"""Console-script entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .server import serve
from .socket_path import default_socket_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kaithem-host-services")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_serve = sub.add_parser("serve", help="Run the host-services server")
    p_serve.add_argument(
        "--socket",
        type=Path,
        default=None,
        help="Override the UDS path (default: $XDG_RUNTIME_DIR/kaithem-host-services.sock)",
    )

    p_print = sub.add_parser("print-socket-path", help="Print the default UDS path and exit")

    args = parser.parse_args(argv)

    if args.cmd == "serve":
        serve(args.socket)
        return 0
    if args.cmd == "print-socket-path":
        print(default_socket_path())
        return 0

    parser.error("unknown command")
    return 2  # unreachable


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
