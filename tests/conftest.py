"""Pytest configuration."""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Adding options to the Pytest args."""
    parser.addoption(
        "--unit",
        "--unit-tests",
        "--UNIT",
        action="store_true",
        dest="unit",
        default=False,
        help="run unit tests",
    )
    parser.addoption(
        "--integration",
        "--cli",
        "--CLI",
        action="store_true",
        dest="CLI",
        default=False,
        help="enable integration (e.g. CLI) decorated tests",
    )
    parser.addoption(
        "--performance",
        action="store_true",
        dest="performance",
        default=False,
        help="perform performance load tests (e.g. high concurrency)",
    )
    parser.addoption(
        "--all",
        action="store_true",
        dest="all",
        default=False,
        help="run all unit tests, excluding performance tests",
    )


def pytest_configure(config: pytest.Parser) -> None:
    """Handling custom Pytest args."""
    markers = []
    if config.option.performance:
        # config.option
        markers.append("performance")
    else:
        markers.append("not performance")
    if config.option.all or config.option.CLI:
        markers.append("integration")
    else:
        markers.append("not integration")
    # Run unittests by default, currently an
    if config.option.unit or config.option.all or len(markers) == 0:
        markers.append("unit")
    else:
        markers.append("not unit")

    setattr(config.option, "markexpr", " and ".join(markers))
