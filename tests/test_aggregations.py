"""Handmade examples protect the original aggregation values."""

from tvsummary import AverageRatingByLanguage, ShowsPerGenre


def test_genre_counts(shows):
    assert ShowsPerGenre().compute(shows) == {
        "counts": {"Comedy": 1, "Drama": 2},
        "shows_without_valid_genres": 1,
    }


def test_language_averages(shows):
    assert AverageRatingByLanguage().compute(shows) == {
        "languages": {"English": {"average_rating": 7.0, "rated_shows": 2}},
        "shows_without_valid_language": 1,
        "shows_without_valid_rating": 1,
        "shows_included": 2,
    }


def test_empty_genre_input():
    assert ShowsPerGenre().compute([]) == {
        "counts": {},
        "shows_without_valid_genres": 0,
    }


def test_empty_rating_input():
    assert AverageRatingByLanguage().compute([])["shows_included"] == 0
