class TVSummaryError(Exception):
    """Base class for expected package failures handled by main()."""


class DownloadError(TVSummaryError):
    """The source could not be reached or returned an HTTP failure."""


class ResponseShapeError(TVSummaryError):
    """The source returned invalid JSON or an unexpected record structure."""


class SettingsError(TVSummaryError):
    """The settings file is missing, incomplete or unusable."""


class OutputError(TVSummaryError):
    """A report could not be written to its destination."""
