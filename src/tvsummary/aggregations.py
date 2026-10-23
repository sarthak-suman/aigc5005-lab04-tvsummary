"""Related calculations sharing a compute interface."""
from abc import ABC, abstractmethod


class Aggregation(ABC):
    """Base for a named summary calculation."""

    def __init__(self, key):
        self.key = key

    @abstractmethod
    def compute(self, records):
        """Calculate one summary section."""
        raise NotImplementedError


class ShowsPerGenre(Aggregation):
    """Calculate shows per genre."""

    def __init__(self):
        super().__init__("shows_per_genre")

    def compute(self, records):
        """Count each show once in each of its valid genres."""
        counts = {}
        without_genres = 0

        for record in records:
            genres = record.genres

            if not genres:
                without_genres += 1

            for genre in genres:
                counts[genre] = counts.get(genre, 0) + 1

        return {
            "counts": dict(sorted(counts.items())),
            "shows_without_valid_genres": without_genres,
        }


class AverageRatingByLanguage(Aggregation):
    """Calculate average rating by language."""

    def __init__(self):
        super().__init__("average_rating_by_language")

    def compute(self, records):
        """Average valid ratings by language and report excluded shows."""
        groups = {}
        missing_language = 0
        missing_rating = 0

        for record in records:
            language = record.language
            rating = record.rating
            language_ok = language is not None
            rating_ok = rating is not None

            if not language_ok:
                missing_language += 1

            if not rating_ok:
                missing_rating += 1

            if not language_ok or not rating_ok:
                continue

            language = language.strip()

            if language not in groups:
                groups[language] = []

            groups[language].append(rating)

        averages = {
            language: {
                "average_rating": round(sum(ratings) / len(ratings), 2),
                "rated_shows": len(ratings),
            }
            for language, ratings in sorted(groups.items())
        }

        return {
            "languages": averages,
            "shows_without_valid_language": missing_language,
            "shows_without_valid_rating": missing_rating,
            "shows_included": sum(len(ratings) for ratings in groups.values()),
        }


