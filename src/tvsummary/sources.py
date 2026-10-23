"""Download and validate TVMaze records."""
import requests
from .config import SOURCE_URL, TIMEOUT
from .models import Show


class DownloadError(Exception):
    """A download or response validation failed."""


class TVMazeSource:
    """Fetch show objects from the configured API."""

    def __init__(self, url=SOURCE_URL, timeout=TIMEOUT):
        self.url = url
        self.timeout = timeout

    def fetch(self):
        """Return cleaned shows or raise a clear download error."""
        try:
            return self._download()
        except (requests.RequestException, ValueError) as error:
            raise DownloadError(str(error)) from error

    def _download(self):
        """Download and validate a list of at least 50 show records."""
        response = requests.get(self.url, timeout=self.timeout)
        response.raise_for_status()
        records = response.json()

        if not isinstance(records, list):
            raise ValueError("The API did not return a list of records.")

        if len(records) < 50:
            raise ValueError("The API returned fewer than 50 records.")

        if any(not isinstance(record, dict) for record in records):
            raise ValueError("The API returned a malformed show record.")

        return [Show(record) for record in records]
