import json
import logging
import platform
import random
from dataclasses import asdict
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .aggregations import AverageRatingByLanguage, ShowsPerGenre
from .config import Settings, load_settings
from .errors import OutputError, SettingsError
from .models import Show

logger = logging.getLogger(__name__)


def build_summary(
    records: list[Show],
    source_url: str | None = None,
    *,
    seed: int | None = None,
    sample_size: int | None = None,
) -> dict[str, Any]:
    """Keep all Lab 03 calculations and add locally seeded show selection."""
    settings = load_settings() if None in (source_url, seed, sample_size) else None
    source_url = (
        source_url
        if source_url is not None
        else settings.source_url
        if settings
        else ""
    )
    seed = seed if seed is not None else settings.seed if settings else 0
    sample_size = (
        sample_size
        if sample_size is not None
        else settings.sample_size
        if settings
        else 0
    )
    if sample_size < 0 or sample_size > len(records):
        raise SettingsError("sample_size must be between 0 and the number of shows")
    logger.info("Building summary for %s shows", len(records))
    summary: dict[str, Any] = {
        "source_url": source_url,
        "records_processed": len(records),
    }
    aggregations = [ShowsPerGenre(), AverageRatingByLanguage()]
    for aggregation in aggregations:
        summary[aggregation.key] = aggregation.compute(records)
    summary["featured_shows"] = random.Random(seed).sample(
        [record.name for record in records], sample_size
    )
    return summary


def write_summary(summary: dict[str, Any], path: Path | None = None) -> None:
    """Write UTF-8 JSON, creating the parent folder when necessary."""
    if path is None:
        path = load_settings().output_folder / "summary.json"
    _write_json(summary, path)


def write_run_info(settings: Settings) -> None:
    """Record the settings, interpreter version and checking tool versions."""
    recorded_settings = asdict(settings)
    recorded_settings["output_folder"] = str(settings.output_folder)
    tool_versions: dict[str, str] = {}
    for tool in ("pytest", "mypy", "ruff"):
        try:
            tool_versions[tool] = version(tool)
        except PackageNotFoundError as error:
            raise SettingsError(
                f"Required checking tool is not installed: {tool}"
            ) from error
    _write_json(
        {
            "settings": recorded_settings,
            "python_version": platform.python_version(),
            "tool_versions": tool_versions,
        },
        settings.output_folder / "run_info.json",
    )


def _write_json(document: dict[str, Any], path: Path) -> None:
    """Translate filesystem failures at the output boundary."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(document, file, indent=2, ensure_ascii=False)
            file.write("\n")
    except OSError as error:
        raise OutputError(
            f"Could not write summary or run info to {path}: {error}"
        ) from error
    logger.info("Saved report to %s", path)
