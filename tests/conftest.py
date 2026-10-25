"""Model/data opt-in and network isolation for small-fixture test runs."""

import os
import socket
import shutil
import uuid
from pathlib import Path

import pytest


@pytest.fixture
def workspace_tmp_path():
    directory = Path(__file__).resolve().parents[1] / "reports/runs" / f"fixture-{uuid.uuid4().hex}"
    directory.mkdir(parents=True)
    try:
        yield directory
    finally:
        shutil.rmtree(directory)


def pytest_collection_modifyitems(items):
    if os.getenv("CI", "").lower() != "true":
        return
    for item in items:
        if any(
            item.get_closest_marker(marker)
            for marker in ("requires_weights", "requires_datasets", "live_api")
        ):
            item.add_marker(
                pytest.mark.skip(reason="CI runs small fixtures without models or datasets")
            )


@pytest.fixture(autouse=True)
def no_external_network(monkeypatch, request):
    if request.node.get_closest_marker("live_api"):
        return
    original_connect = socket.socket.connect

    def blocked(sock, address):
        # Windows' asyncio socketpair uses loopback even for in-process TestClient calls.
        if isinstance(address, tuple) and address[0] in ("127.0.0.1", "::1"):
            return original_connect(sock, address)
        raise AssertionError("Network access is disabled in fixture tests")

    monkeypatch.setattr(socket.socket, "connect", blocked)
