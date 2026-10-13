import pytest
from app import database, analyzer


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_db()


def sample_entries():
    return [
        {"timestamp": "2026-10-12 14:00:00", "level": "ERROR", "message": "boom"},
        {"timestamp": "2026-10-12 14:30:00", "level": "ERROR", "message": "boom"},
        {"timestamp": "2026-10-12 15:00:00", "level": "ERROR", "message": "crash"},
        {"timestamp": "2026-10-12 15:10:00", "level": "INFO", "message": "ok"},
        {"timestamp": "2026-10-12 15:20:00", "level": "WARN", "message": "slow"},
    ]


def test_count_by_level():
    database.insert_logs(sample_entries(), "a.log")
    assert analyzer.count_by_level() == {"ERROR": 3, "INFO": 1, "WARN": 1}


def test_top_errors_ranks_most_common_first():
    database.insert_logs(sample_entries(), "a.log")
    top = analyzer.top_errors()
    assert top[0] == {"message": "boom", "count": 2}
    assert top[1] == {"message": "crash", "count": 1}


def test_errors_per_hour():
    database.insert_logs(sample_entries(), "a.log")
    assert analyzer.errors_per_hour() == [
        {"hour": "2026-10-12 14", "count": 2},
        {"hour": "2026-10-12 15", "count": 1},
    ]


def test_search_by_level_ignores_case():
    database.insert_logs(sample_entries(), "a.log")
    results = analyzer.search_logs(level="info")
    assert len(results) == 1
    assert results[0]["message"] == "ok"


def test_search_by_keyword():
    database.insert_logs(sample_entries(), "a.log")
    results = analyzer.search_logs(keyword="cra")
    assert len(results) == 1
    assert results[0]["message"] == "crash"


def test_filter_by_source_file():
    database.insert_logs(sample_entries(), "a.log")
    database.insert_logs(
        [{"timestamp": "2026-10-13 09:00:00", "level": "ERROR", "message": "other"}],
        "b.log",
    )
    assert analyzer.count_by_level("a.log")["ERROR"] == 3
    assert analyzer.count_by_level("b.log") == {"ERROR": 1}


def test_uploading_same_file_twice_does_not_duplicate():
    database.insert_logs(sample_entries(), "a.log")
    database.insert_logs(sample_entries(), "a.log")
    assert sum(analyzer.count_by_level().values()) == 5


def test_empty_database_gives_empty_results():
    assert analyzer.count_by_level() == {}
    assert analyzer.top_errors() == []