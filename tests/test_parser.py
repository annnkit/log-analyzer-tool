from app.parser import parse_line


def test_parses_valid_line():
    line = "2026-10-12 14:03:25 ERROR Database connection failed"
    result = parse_line(line)
    assert result == {
        "timestamp": "2026-10-12 14:03:25",
        "level": "ERROR",
        "message": "Database connection failed",
    }

def test_parses_access_log_server_error():
    line = '192.168.1.11 - - [12/Oct/2026:14:03:27 +0000] "GET /api/orders HTTP/1.1" 500 87'
    assert parse_line(line) == {
        "timestamp": "2026-10-12 14:03:27",
        "level": "ERROR",
        "message": "GET /api/orders -> 500",
    }


def test_access_log_status_to_level():
    def level_for(status):
        line = f'1.1.1.1 - - [12/Oct/2026:14:03:27 +0000] "GET /x HTTP/1.1" {status} 1'
        return parse_line(line)["level"]

    assert level_for(200) == "INFO"
    assert level_for(404) == "WARN"
    assert level_for(503) == "ERROR"


def test_access_log_with_bad_date_returns_none():
    line = '1.1.1.1 - - [99/Foo/2026:14:03:27 +0000] "GET /x HTTP/1.1" 200 1'
    assert parse_line(line) is None


def test_garbage_line_returns_none():
    assert parse_line("this is not a log line") is None