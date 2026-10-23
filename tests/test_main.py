import json
from dataclasses import replace
from pathlib import Path
import platform


import pytest

from tvsummary import DownloadError
from tvsummary import main as entry
from tvsummary.config import Settings
from tvsummary.errors import OutputError, ResponseShapeError


@pytest.fixture
def settings(tmp_path):
    return Settings(
        "https://example.invalid", 2.0, tmp_path / "processed", 42, 2, "INFO"
    )


@pytest.mark.parametrize(
    "failure",
    [
        DownloadError("no network"),
        ResponseShapeError("bad response"),
        OutputError("cannot write"),
    ],
)
def test_main_expected_failure(monkeypatch, capsys, settings, failure):
    monkeypatch.setattr(entry, "load_settings", lambda path: settings)

    def fail(self):
        raise failure

    monkeypatch.setattr(entry.TVMazeSource, "fetch", fail)
    assert entry.main([]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == f"Error: {failure}\n"
    assert "Traceback" not in captured.err


def test_main_missing_config(capsys, tmp_path):
    assert entry.main(["--config", str(tmp_path / "missing.toml")]) == 1
    captured = capsys.readouterr()
    assert captured.err.startswith("Error: Could not read settings file")
    assert "Traceback" not in captured.err


def test_main_success_writes_both_reports(monkeypatch, capsys, settings, shows):
    requested = []

    def fake_load(path):
        requested.append(path)
        return settings

    monkeypatch.setattr(entry, "load_settings", fake_load)
    monkeypatch.setattr(entry.TVMazeSource, "fetch", lambda self: shows)
    assert entry.main(["--config", "custom.toml"]) == 0
    assert requested == [Path("custom.toml")]
    assert "Processed 3 shows." in capsys.readouterr().out
    summary = json.loads((settings.output_folder / "summary.json").read_text())
    run_info = json.loads((settings.output_folder / "run_info.json").read_text())
    assert len(summary["featured_shows"]) == 2
    assert run_info["settings"]["seed"] == 42
    assert set(run_info["tool_versions"]) == {"pytest", "mypy", "ruff"}
    assert all(run_info["tool_versions"].values())
    assert run_info["python_version"] == platform.python_version()


def test_main_output_failure(monkeypatch, capsys, settings, shows, tmp_path):
    occupied = tmp_path / "occupied"
    occupied.write_text("file", encoding="utf-8")
    monkeypatch.setattr(
        entry, "load_settings", lambda path: replace(settings, output_folder=occupied)
    )
    monkeypatch.setattr(entry.TVMazeSource, "fetch", lambda self: shows)
    assert entry.main([]) == 1
    assert capsys.readouterr().err.startswith("Error: Could not write summary")


def test_main_does_not_hide_programming_errors(monkeypatch, settings):
    monkeypatch.setattr(entry, "load_settings", lambda path: settings)

    def fail(self):
        raise RuntimeError("programming bug")

    monkeypatch.setattr(entry.TVMazeSource, "fetch", fail)
    with pytest.raises(RuntimeError, match="programming bug"):
        entry.main([])
