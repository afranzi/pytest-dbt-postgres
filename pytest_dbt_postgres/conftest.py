from typing import Any

from pytest_postgresql import factories


def get_open_port() -> int:
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()

    return port


def factory_postgresql_proc(port: int | None = None) -> tuple[Any, int]:
    port = port or get_open_port()
    postgresql_proc = factories.postgresql_proc(port=port)

    return postgresql_proc, port


postgresql_proc, postgres_port = factory_postgresql_proc()
postgresql = factories.postgresql("postgresql_proc", dbname="test")
