"""Offline tests using handmade records."""
import unittest
from tvsummary import Show, ShowsPerGenre, AverageRatingByLanguage


class ShowTests(unittest.TestCase):
    def test_clean_values(self):
        show = Show({"name": " Example ", "genres": [" Drama ", "Drama", "", None],
                     "language": " English ", "rating": {"average": 8}})
        self.assertEqual(show.genres, {"Drama"})
        self.assertEqual(show.language, "English")
        self.assertEqual(show.rating, 8)
        self.assertEqual(str(show), "Example")

    def test_invalid_values(self):
        for rating in [None, True, "8", -1, 11, float("nan"), float("inf")]:
            show = Show({"genres": "Drama", "language": " ", "rating": {"average": rating}})
            self.assertEqual(show.genres, set())
            self.assertIsNone(show.language)
            self.assertIsNone(show.rating)

    def test_aggregations(self):
        shows = [Show({"genres": ["Drama", "Drama"], "language": "English", "rating": {"average": 8}}),
                 Show({"genres": ["Drama"], "language": "English", "rating": {"average": 6}}), Show({})]
        self.assertEqual(ShowsPerGenre().compute(shows),
                         {"counts": {"Drama": 2}, "shows_without_valid_genres": 1})
        self.assertEqual(AverageRatingByLanguage().compute(shows), {
            "languages": {"English": {"average_rating": 7.0, "rated_shows": 2}},
            "shows_without_valid_language": 1, "shows_without_valid_rating": 1, "shows_included": 2})
