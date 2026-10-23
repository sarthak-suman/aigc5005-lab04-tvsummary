from dataclasses import FrozenInstanceError

import pytest

from tvsummary.config import load_settings
from tvsummary.errors import SettingsError

VALID_CONFIG = """source_url = "https://example.invalid/shows"
timeout = 2
output_folder = "data/processed"
seed = 42
sample_size = 2
log_level = "DEBUG"
"""


def test_valid_settings_are_frozen(tmp_path):
    path = tmp_path / "settings.toml"
    path.write_text(VALID_CONFIG)
    settings = load_settings(path)
    assert settings.seed == 42
    assert settings.timeout == 2.0
    with pytest.raises(FrozenInstanceError):
        settings.seed = 1


def test_missing_config_is_chained(tmp_path):
    with pytest.raises(SettingsError, match="Could not read settings file") as caught:
        load_settings(tmp_path / "missing.toml")
    assert isinstance(caught.value.__cause__, OSError)


def test_incomplete_settings(tmp_path):
    path = tmp_path / "incomplete.toml"
    path.write_text("seed = 42\n")
    with pytest.raises(SettingsError, match="Missing settings.*sample_size"):
        load_settings(path)


def test_invalid_toml_is_chained(tmp_path):
    path = tmp_path / "invalid.toml"
    path.write_text("seed = [")
    with pytest.raises(SettingsError, match="Could not read settings") as caught:
        load_settings(path)
    assert isinstance(caught.value.__cause__, ValueError)


@pytest.mark.parametrize(
    "old, new, message",
    [
        ("timeout = 2", "timeout = 0", "timeout"),
        ("timeout = 2", "timeout = true", "timeout"),
        ("timeout = 2", "timeout = inf", "timeout"),
        ("seed = 42", "seed = true", "seed"),
        ("sample_size = 2", "sample_size = -1", "sample_size"),
        ("sample_size = 2", "sample_size = true", "sample_size"),
        ('log_level = "DEBUG"', 'log_level = "verbose"', "log_level"),
        ('output_folder = "data/processed"', 'output_folder = ""', "output_folder"),
        ("https://example.invalid/shows", "ftp://example.invalid/shows", "source_url"),
        ("https://example.invalid/shows", "https://[invalid", "source_url"),
    ],
)
def test_invalid_settings(tmp_path, old, new, message):
    path = tmp_path / "invalid.toml"
    path.write_text(VALID_CONFIG.replace(old, new))
    with pytest.raises(SettingsError, match=message):
        load_settings(path)
