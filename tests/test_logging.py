"""Logging is observable without contacting the network."""

import logging

from tvsummary import Show, build_summary


def test_invalid_rating_is_logged(caplog):
    with caplog.at_level(logging.WARNING, logger="tvsummary.models"):
        show = Show({"name": "Example", "rating": {"average": 20}})
    assert show.rating is None
    assert "Excluded an invalid rating for show Example" in caplog.text


def test_summary_milestone_is_logged(caplog, shows):
    with caplog.at_level(logging.INFO, logger="tvsummary.report"):
        build_summary(shows)
    assert "Building summary for 3 shows" in caplog.text
