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


def test_output_failure_is_chained(tmp_path, shows):
    import pytest

    from tvsummary.errors import OutputError

    parent = tmp_path / "file-not-directory"
    parent.write_text("occupied", encoding="utf-8")
    with pytest.raises(OutputError, match="Could not write summary") as caught:
        write_summary(build_summary(shows), parent / "summary.json")
    assert isinstance(caught.value.__cause__, OSError)
