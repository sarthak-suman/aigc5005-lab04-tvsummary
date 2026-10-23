"""Protect the current entry-point failure exit code and output."""

import importlib.util
from pathlib import Path

from tvsummary import DownloadError


def test_main_download_failure(monkeypatch, capsys):
    spec = importlib.util.spec_from_file_location(
        "lab_entry", Path(__file__).parents[1] / "main.py"
    )
    entry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entry)

    def fail(self):
        raise DownloadError("no network")

    monkeypatch.setattr(entry.TVMazeSource, "fetch", fail)
    assert entry.main() == 1
    assert capsys.readouterr().out == "Download failed: no network\n"
