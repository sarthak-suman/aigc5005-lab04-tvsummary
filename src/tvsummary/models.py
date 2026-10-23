import logging
import math
from typing import Any

logger = logging.getLogger(__name__)


class Show:
    def __init__(self, record: dict[str, Any]) -> None:
        name = record.get("name")
        self.name = (
            name.strip() if isinstance(name, str) and name.strip() else "Unknown show"
        )
        genres = record.get("genres")
        self.genres = (
            {
                genre.strip()
                for genre in genres
                if isinstance(genre, str) and genre.strip()
            }
            if isinstance(genres, list)
            else set()
        )
        language = record.get("language")
        self.language = (
            language.strip() if isinstance(language, str) and language.strip() else None
        )
        rating_data = record.get("rating")
        rating = rating_data.get("average") if isinstance(rating_data, dict) else None
        self.rating = (
            rating
            if (
                isinstance(rating, (int, float))
                and not isinstance(rating, bool)
                and math.isfinite(rating)
                and 0 <= rating <= 10
            )
            else None
        )
        if rating is not None and self.rating is None:
            logger.warning("Excluded an invalid rating for show %s", self.name)

    def __str__(self) -> str:
        return self.name
