"""Build and write the summary."""

import json
import logging

from .aggregations import AverageRatingByLanguage, ShowsPerGenre
from .config import OUTPUT, SOURCE_URL
from .errors import OutputError

logger = logging.getLogger(__name__)


def build_summary(records, source_url=SOURCE_URL):
    """Call each calculation through the same interface."""
    logger.info("Building summary for %s shows", len(records))
    summary = {"source_url": source_url, "records_processed": len(records)}
    aggregations = [ShowsPerGenre(), AverageRatingByLanguage()]
    for aggregation in aggregations:
        summary[aggregation.key] = aggregation.compute(records)
    return summary


def write_summary(summary, path=OUTPUT):
    """Write formatted UTF-8 JSON, creating the output directory."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(summary, file, indent=2, ensure_ascii=False)
            file.write("\n")
        logger.info("Saved summary to %s", path)

    except OSError as error:
        raise OutputError(f"Could not write summary to {path}: {error}") from error
