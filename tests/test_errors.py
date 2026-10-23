import pytest

from tvsummary import DownloadError
from tvsummary.errors import (
    OutputError,
    ResponseShapeError,
    SettingsError,
    TVSummaryError,
)
from tvsummary.sources import DownloadError as SourceDownloadError


@pytest.mark.parametrize(
    "error_type", [DownloadError, ResponseShapeError, SettingsError, OutputError]
)
def test_expected_error_inherits_package_base(error_type):
    assert issubclass(error_type, TVSummaryError)


def test_original_download_error_import_is_preserved():
    assert SourceDownloadError is DownloadError
