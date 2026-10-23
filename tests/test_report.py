"""Summary construction and output preserve baseline behavior."""

import json

from tvsummary import build_summary, write_summary


def test_summary_sections(shows):
    summary = build_summary(shows, "https://example.invalid", seed=42, sample_size=2)
    assert summary["source_url"] == "https://example.invalid"
    assert summary["records_processed"] == 3
    assert summary["shows_per_genre"]["counts"] == {"Comedy": 1, "Drama": 2}
    assert summary["average_rating_by_language"]["shows_included"] == 2


def test_write_summary_creates_directory(tmp_path, shows):
    summary = build_summary(shows, seed=42, sample_size=2)
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
        write_summary(
            build_summary(shows, seed=42, sample_size=2), parent / "summary.json"
        )
    assert isinstance(caught.value.__cause__, OSError)


def test_same_seed_produces_same_featured_shows(shows):
    first = build_summary(shows, seed=42, sample_size=2)
    second = build_summary(shows, seed=42, sample_size=2)
    assert first["featured_shows"] == second["featured_shows"]
    assert len(first["featured_shows"]) == 2


def test_sampling_preserves_global_random_state(shows):
    import random

    before = random.getstate()
    build_summary(shows, seed=42, sample_size=2)
    assert random.getstate() == before


def test_every_legacy_summary_value_is_preserved(shows):
    summary = build_summary(shows, "https://example.invalid", seed=42, sample_size=2)
    featured = summary.pop("featured_shows")
    assert len(featured) == 2
    assert summary == {
        "source_url": "https://example.invalid",
        "records_processed": 3,
        "shows_per_genre": {
            "counts": {"Comedy": 1, "Drama": 2},
            "shows_without_valid_genres": 1,
        },
        "average_rating_by_language": {
            "languages": {"English": {"average_rating": 7.0, "rated_shows": 2}},
            "shows_without_valid_language": 1,
            "shows_without_valid_rating": 1,
            "shows_included": 2,
        },
    }


def test_sample_size_larger_than_input_raises(shows):
    import pytest

    from tvsummary.errors import SettingsError

    with pytest.raises(SettingsError, match="sample_size"):
        build_summary(shows, seed=42, sample_size=4)


def test_zero_sample_on_empty_input():
    assert build_summary([], seed=42, sample_size=0)["featured_shows"] == []
