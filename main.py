"""Run the TV summary package."""

import logging

from tvsummary import TVMazeSource, build_summary, write_summary
from tvsummary.config import OUTPUT
from tvsummary.errors import OutputError, TVSummaryError
from tvsummary.logging_setup import configure_logging

logger = logging.getLogger(__name__)


def main():
    """Wire downloading, calculations and writing together."""
    configure_logging("INFO")
    source = TVMazeSource()
    try:
        records = source.fetch()
    except TVSummaryError as error:
        logger.error("Download failed: %s", error)
        print(f"Download failed: {error}")
        return 1
    summary = build_summary(records, source.url)
    try:
        write_summary(summary)
    except OutputError as error:
        logger.error("Could not save the summary: %s", error)
        print(f"Could not save the summary: {error}")
        return 1
    print(f"Processed {len(records)} shows.")
    print(f"Summary saved to {OUTPUT}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
