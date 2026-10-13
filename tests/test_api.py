import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_db()


LOG_A = (
    "2026-10-12 14:00:00 ERROR boom\n"
    "2026-10-12 14:30:00 ERROR boom\n"
    "2026-10-12 15:00:00 INFO ok\n"
    "this line is garbage\n"
)
LOG_B = "2026-10-13 09:00:00 WARN slow\n"


def upload(name, text):
    return client.post("/upload", files={"file": (name, text.encode(), "text/plain")})


def test_upload_reports_saved_and_skipped():
    res = upload("a.log", LOG_A)
    assert res.status_code == 200
    assert res.json() == {"filename": "a.log", "saved": 3, "skipped": 1}


def test_upload_rejects_file_with_no_log_lines():
    res = upload("junk.txt", "hello\nworld\n")
    assert res.status_code == 400


def test_levels_endpoint():
    upload("a.log", LOG_A)
    res = client.get("/stats/levels")
    assert res.json() == {"ERROR": 2, "INFO": 1}


def test_levels_endpoint_filters_by_file():
    upload("a.log", LOG_A)
    upload("b.log", LOG_B)
    assert client.get("/stats/levels", params={"source_file": "b.log"}).json() == {"WARN": 1}
    assert client.get("/stats/levels").json() == {"ERROR": 2, "INFO": 1, "WARN": 1}


def test_top_errors_endpoint():
    upload("a.log", LOG_A)
    assert client.get("/stats/top-errors").json() == [{"message": "boom", "count": 2}]


def test_errors_per_hour_endpoint():
    upload("a.log", LOG_A)
    assert client.get("/stats/errors-per-hour").json() == [{"hour": "2026-10-12 14", "count": 2}]


def test_logs_endpoint_filters_by_level_and_limit():
    upload("a.log", LOG_A)
    assert len(client.get("/logs", params={"level": "error"}).json()) == 2
    assert len(client.get("/logs", params={"limit": 1}).json()) == 1


def test_logs_endpoint_rejects_bad_limit():
    res = client.get("/logs", params={"limit": "abc"})
    assert res.status_code == 422


def test_files_endpoint_lists_uploads():
    upload("a.log", LOG_A)
    assert client.get("/files").json() == [{"source_file": "a.log", "count": 3}]

def test_delete_file_removes_only_that_file():
    upload("a.log", LOG_A)
    upload("b.log", LOG_B)
    res = client.delete("/files/a.log")
    assert res.status_code == 200
    assert res.json()["deleted"] == 3
    assert client.get("/files").json() == [{"source_file": "b.log", "count": 1}]


def test_delete_missing_file_returns_404():
    assert client.delete("/files/nope.log").status_code == 404