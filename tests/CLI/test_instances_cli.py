"""Tests regarding the instances CLI entry points."""

import pytest
from pathlib import Path

from sparkle.CLI import add_instances, remove_instances


@pytest.mark.integration
def test_add_remove_instances_iterable_file_instance_set(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test adding/removing command for a set of files."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        instances_path = Path("Examples") / "Resources" / "Instances" / "PTN"
        add_instances.main([str(instances_path.absolute())])
        assert pytest_wrapped_e.type is SystemExit
        assert pytest_wrapped_e.value.code == 0
        remove_instances.main([instances_path.name])
        assert pytest_wrapped_e.type is SystemExit
        assert pytest_wrapped_e.value.code == 0


@pytest.mark.integration
def test_add_remove_instances_multi_file_instance_set(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test adding/removing command for instances consisting of multiple files."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        instances_path = Path("Examples") / "Resources" / "Instances" / "CCAG"
        add_instances.main([str(instances_path.absolute())])
        assert pytest_wrapped_e.type is SystemExit
        assert pytest_wrapped_e.value.code == 0
        remove_instances.main([instances_path.name])
        assert pytest_wrapped_e.type is SystemExit
        assert pytest_wrapped_e.value.code == 0

# TODO: Test removing with instances directory path
# TODO: Test adding / removing with nicknames
# TODO: Test removing with non instance name/paths for failure
