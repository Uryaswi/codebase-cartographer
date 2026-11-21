import json

from cartographer.models import HotspotResult
from cartographer.report import format_hotspots_json, format_hotspots_table

RESULTS = [
    HotspotResult(path="src/app.py", revisions=12, churn=340, size=200, score=2400),
    HotspotResult(path="a.py", revisions=3, churn=9, size=5, score=15),
]


def test_table_has_header_and_rows_in_given_order() -> None:
    lines = format_hotspots_table(RESULTS).splitlines()
    assert lines[0].split() == ["PATH", "REVISIONS", "CHURN", "SIZE", "SCORE"]
    assert lines[1].split() == ["src/app.py", "12", "340", "200", "2400"]
    assert lines[2].split() == ["a.py", "3", "9", "5", "15"]


def test_table_columns_are_aligned() -> None:
    lines = format_hotspots_table(RESULTS).splitlines()
    assert len({len(line) for line in lines}) == 1


def test_empty_table_says_no_hotspots() -> None:
    assert format_hotspots_table([]) == "No hotspots found."


def test_json_round_trips_all_fields() -> None:
    data = json.loads(format_hotspots_json(RESULTS))
    assert data[0] == {
        "path": "src/app.py",
        "revisions": 12,
        "churn": 340,
        "size": 200,
        "score": 2400,
    }
    assert [item["path"] for item in data] == ["src/app.py", "a.py"]


def test_empty_json_is_empty_array() -> None:
    assert json.loads(format_hotspots_json([])) == []
