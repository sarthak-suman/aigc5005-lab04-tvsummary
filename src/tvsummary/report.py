"""Build and write the summary."""

import json
import logging
from pathlib import Path
from typing import Any

from .aggregations import AverageRatingByLanguage, ShowsPerGenre
from .config import OUTPUT, SOURCE_URL
from .errors import OutputError
from .models import Show

logger = logging.getLogger(__name__)


def build_summary(records: list[Show], source_url: str = SOURCE_URL) -> dict[str, Any]:
    """Call each calculation through the same interface."""
    logger.info("Building summary for %s shows", len(records))
    summary: dict[str, Any] = {
        "source_url": source_url,
        "records_processed": len(records),
    }
    aggregations = [ShowsPerGenre(), AverageRatingByLanguage()]
    for aggregation in aggregations:
        summary[aggregation.key] = aggregation.compute(records)
    return summary


def write_summary(summary: dict[str, Any], path: Path = OUTPUT) -> None:
    """Write formatted UTF-8 JSON, creating the output directory."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(summary, file, indent=2, ensure_ascii=False)
            file.write("\n")
        logger.info("Saved summary to %s", path)

    except OSError as error:
        raise OutputError(f"Could not write summary to {path}: {error}") from error
