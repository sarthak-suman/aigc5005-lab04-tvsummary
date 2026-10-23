import math
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .errors import SettingsError


@dataclass(frozen=True)
class Settings:
    """Validated settings; relative output paths use the working directory."""

    source_url: str
    timeout: float
    output_folder: Path
    seed: int
    sample_size: int
    log_level: str


def load_settings(path: Path = Path("config/tvsummary.toml")) -> Settings:
    try:
        with path.open("rb") as file:
            values = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise SettingsError(f"Could not read settings file {path}: {error}") from error
    return _validate_settings(values)


def _validate_settings(values: dict[str, Any]) -> Settings:
    required = {
        "source_url",
        "timeout",
        "output_folder",
        "seed",
        "sample_size",
        "log_level",
    }
    missing = required - values.keys()
    if missing:
        raise SettingsError("Missing settings: " + ", ".join(sorted(missing)))
    source_url = values["source_url"]
    if not isinstance(source_url, str):
        raise SettingsError("source_url must be an HTTP or HTTPS URL")
    try:
        parsed = urlparse(source_url)
        valid_url = parsed.scheme in {"http", "https"} and bool(parsed.hostname)
    except ValueError as error:
        raise SettingsError("source_url must be an HTTP or HTTPS URL") from error
    if not valid_url:
        raise SettingsError("source_url must be an HTTP or HTTPS URL")
    timeout = values["timeout"]
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, int | float)
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise SettingsError("timeout must be a positive finite number")
    output_folder = values["output_folder"]
    if not isinstance(output_folder, str) or not output_folder.strip():
        raise SettingsError("output_folder must be a nonempty path string")
    seed = values["seed"]
    sample_size = values["sample_size"]
    if type(seed) is not int:
        raise SettingsError("seed must be an integer")
    if type(sample_size) is not int or sample_size < 0:
        raise SettingsError("sample_size must be a nonnegative integer")
    log_level = values["log_level"]
    if not isinstance(log_level, str) or log_level not in {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }:
        raise SettingsError("log_level must be DEBUG, INFO, WARNING, ERROR or CRITICAL")
    return Settings(
        source_url, float(timeout), Path(output_folder), seed, sample_size, log_level
    )
