"""Tests for the feature extractor CLI entry points."""
import pytest
from pathlib import Path

from sparkle.CLI import add_feature_extractor, remove_feature_extractor


@pytest.mark.integration
def test_add_remove_solver_command(tmp_path: Path,
                                   monkeypatch: pytest.MonkeyPatch) -> None:
    """Test initialise command."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        extractor_path = Path("Examples") / "Resources" / "Extractors" /\
            "SAT-features-competition2012_revised_without_SatELite_sparkle"
        add_feature_extractor.main([str(extractor_path.absolute())])
        assert pytest_wrapped_e.type is SystemExit
        assert pytest_wrapped_e.value.code == 0
        remove_feature_extractor.main([extractor_path.name])
        assert pytest_wrapped_e.type is SystemExit
        assert pytest_wrapped_e.value.code == 0

# TODO: Test removing with extractor directory path
# TODO: Test adding / removing with nicknames
# TODO: Test removing with non extractor name/paths for failure