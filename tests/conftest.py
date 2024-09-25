"""Pytest configuration."""
import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Adding options to the Pytest args."""
    parser.addoption("--cli", "--CLI", action="store_true", dest="CLI",
                     default=False, help="enable CLI decorated tests")
    parser.addoption("--only-cli", "--only-CLI", action="store_true", dest="only_cli",
                     default=False, help="only run CLI decorated tests")


def pytest_configure(config: pytest.Parser) -> None:
    """Handling custom Pytest args."""
    if not config.option.CLI and not config.option.only_cli:
        setattr(config.option, "markexpr", "not CLI")
    elif config.option.only_cli:
        setattr(config.option, "markexpr", "CLI")
