"""Summary construction and output preserve baseline behavior."""

import json

from tvsummary import build_summary, write_summary


def test_summary_sections(shows):
    summary = build_summary(shows, "https://example.invalid")
    assert summary["source_url"] == "https://example.invalid"
    assert summary["records_processed"] == 3
    assert summary["shows_per_genre"]["counts"] == {"Comedy": 1, "Drama": 2}
    assert summary["average_rating_by_language"]["shows_included"] == 2


def test_write_summary_creates_directory(tmp_path, shows):
    summary = build_summary(shows)
    destination = tmp_path / "processed" / "summary.json"
    write_summary(summary, destination)
    assert json.loads(destination.read_text(encoding="utf-8")) == summary
    assert destination.read_text(encoding="utf-8").endswith("\n")
