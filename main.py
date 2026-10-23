"""Run the TV summary package."""

from tvsummary import TVMazeSource, build_summary, write_summary
from tvsummary.config import OUTPUT
from tvsummary.errors import OutputError, TVSummaryError


def main():
    """Wire downloading, calculations and writing together."""
    source = TVMazeSource()
    try:
        records = source.fetch()
    except TVSummaryError as error:
        print(f"Download failed: {error}")
        return 1
    summary = build_summary(records, source.url)
    try:
        write_summary(summary)
    except OutputError as error:
        print(f"Could not save the summary: {error}")
        return 1
    print(f"Processed {len(records)} shows.")
    print(f"Summary saved to {OUTPUT}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
