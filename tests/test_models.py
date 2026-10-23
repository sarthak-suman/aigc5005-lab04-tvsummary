"""Cleaning behavior for individual shows."""

import pytest

from tvsummary import Show


def test_clean_values():
    show = Show(
        {
            "name": " Example ",
            "genres": [" Drama ", "Drama", "", None],
            "language": " English ",
            "rating": {"average": 8},
        }
    )
    assert show.genres == {"Drama"}
    assert show.language == "English"
    assert show.rating == 8
    assert str(show) == "Example"


def test_missing_genres():
    assert Show({}).genres == set()


def test_missing_rating():
    assert Show({}).rating is None


@pytest.mark.parametrize(
    "rating", [None, True, "8", -1, 11, float("nan"), float("inf")]
)
def test_invalid_rating(rating):
    assert Show({"rating": {"average": rating}}).rating is None


@pytest.mark.parametrize("rating", [0, 10, 7.5])
def test_valid_rating_boundaries(rating):
    assert Show({"rating": {"average": rating}}).rating == rating


def test_missing_name_and_blank_language():
    show = Show({"name": " ", "language": " ", "genres": "Drama"})
    assert str(show) == "Unknown show"
    assert show.language is None
    assert show.genres == set()
