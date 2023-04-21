from Commands.sparkle_help import reporting_scenario as rs
from pathlib import Path

def test_none_if_empty_path() -> None:
    repsce = rs.ReportingScenario()
    assert repsce.none_if_empty_path("") == None
    assert repsce.none_if_empty_path("Commands/") == "Commands/"

def test_read_scenario_ini() -> None:
    repsce = rs.ReportingScenario()
    