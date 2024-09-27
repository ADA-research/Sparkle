"""Tests for the reporting_scenario module."""
from sparkle.CLI.help import reporting_scenario as rs


def test_none_if_empty_path() -> None:
    """Test the none_if_empty_path function behaves correctly for different inputs."""
    repsce = rs.ReportingScenario()
    assert repsce.none_if_empty_path("") is None
    assert repsce.none_if_empty_path("CLI/") == "CLI/"
