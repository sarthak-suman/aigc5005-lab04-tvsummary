"""Download and validate TVMaze records."""

import requests

from .config import SOURCE_URL, TIMEOUT
from .errors import DownloadError, ResponseShapeError
from .models import Show


class TVMazeSource:
    """Fetch show objects from the configured API."""

    def __init__(self, url=SOURCE_URL, timeout=TIMEOUT):
        self.url = url
        self.timeout = timeout

    def fetch(self):
        """Return cleaned shows or raise a clear package error."""
        return self._download()

    def _download(self):
        """Download and validate a list of at least 50 show records."""
        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as error:
            raise DownloadError(f"Could not download shows: {error}") from error

        try:
            records = response.json()
        except ValueError as error:
            raise ResponseShapeError("The API did not return valid JSON.") from error

        if not isinstance(records, list):
            raise ResponseShapeError("The API did not return a list of records.")
        if len(records) < 50:
            raise ResponseShapeError("The API returned fewer than 50 records.")
        if any(not isinstance(record, dict) for record in records):
            raise ResponseShapeError("The API returned a malformed show record.")

        return [Show(record) for record in records]
