import logging


def configure_logging(level: str) -> None:
    """Set the root level without replacing handlers owned by callers."""
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger().setLevel(level)
