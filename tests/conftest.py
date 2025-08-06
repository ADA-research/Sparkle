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
        "--all", action="store_true", dest="all", default=False, help="run all tests"
    )


def pytest_configure(config: pytest.Parser) -> None:
    """Handling custom Pytest args."""
    if config.option.all:
        return
    if config.option.CLI:
        setattr(config.option, "markexpr", "integration")
    else:
        setattr(config.option, "markexpr", "not integration")
