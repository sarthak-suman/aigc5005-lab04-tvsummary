"""Build and write the summary."""
import json
from .config import SOURCE_URL, OUTPUT
from .aggregations import ShowsPerGenre, AverageRatingByLanguage


def build_summary(records, source_url=SOURCE_URL):
    """Call each calculation through the same interface."""
    summary = {"source_url": source_url, "records_processed": len(records)}
    aggregations = [ShowsPerGenre(), AverageRatingByLanguage()]
    for aggregation in aggregations:
        summary[aggregation.key] = aggregation.compute(records)
    return summary


def write_summary(summary, path=OUTPUT):
    """Write formatted UTF-8 JSON, creating the output directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)
        file.write("\n")
