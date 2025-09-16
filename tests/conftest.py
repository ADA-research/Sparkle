"""Pytest configuration."""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Adding options to the Pytest args."""
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
        setattr(config.option, "markexpr", "performance")
    else:
        markers.append("not performance")
        setattr(config.option, "markexpr", "not performance")
    if config.option.all or config.option.CLI:
        markers.append("integration")
        setattr(config.option, "markexpr", "integration")
    else:
        markers.append("not integration")
        setattr(config.option, "markexpr", "not integration")
    setattr(config.option, "markexpr", markers)  # config.option
