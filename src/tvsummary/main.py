"""Command-line entry point and the package exception boundary."""

import argparse
import logging
import sys
from pathlib import Path

from .config import load_settings
from .errors import TVSummaryError
from .logging_setup import configure_logging
from .report import build_summary, write_run_info, write_summary
from .sources import TVMazeSource

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """Run the package; expected failures return 1 without a traceback."""
    parser = argparse.ArgumentParser(description="Summarize TVMaze shows")
    parser.add_argument("--config", type=Path, default=Path("config/tvsummary.toml"))
    args = parser.parse_args(argv)
    configured = False
    try:
        settings = load_settings(args.config)
        configure_logging(settings.log_level)
        configured = True
        source = TVMazeSource(settings.source_url, settings.timeout)
        records = source.fetch()
        summary = build_summary(
            records, source.url, seed=settings.seed, sample_size=settings.sample_size
        )
        write_summary(summary, settings.output_folder / "summary.json")
        write_run_info(settings)
    except TVSummaryError as error:
        if not configured:
            configure_logging("ERROR")
        logger.error("Run failed: %s", error)
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Processed {len(records)} shows.")
    print(f"Summary saved to {settings.output_folder / 'summary.json'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
