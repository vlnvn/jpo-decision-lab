from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from server import database
from server.app import app

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(database,'DB_PATH',tmp_path/'test.sqlite3')
    with TestClient(app) as c:
        yield c