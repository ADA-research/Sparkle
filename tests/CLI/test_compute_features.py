"""Test the compute features CLI entry point."""

import pytest
from pathlib import Path

from sparkle.CLI import add_feature_extractor, add_instances, compute_features
from tests.CLI import tools as cli_tools


@pytest.mark.integration
def test_compute_features_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test compute features command."""
    settings_path = cli_tools.get_settings_path()
    extractor_path = (
        Path("Examples") / "Resources" / "Extractors" / "SAT-features-competition2012_"
        "revised_without_SatELite"
    ).absolute()
    instances_path = (Path("Examples") / "Resources" / "Instances" / "PTN").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Setup Platform
    # Add the instances
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_instances.main([str(instances_path)])
        # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Add the feature extractor
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_feature_extractor.main([str(extractor_path)])
        # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Run the compute features command on slurm
    print(settings_path)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        compute_features.main(
            ["--settings-file", str(settings_path), "--run-on", "slurm"]
        )
    cli_tools.kill_slurm_jobs()
    # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Run the compute features command on slurm
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        compute_features.main(
            ["--settings-file", str(settings_path), "--run-on", "slurm"]
        )
    cli_tools.kill_slurm_jobs()
    # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Run the compute features command on local
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        compute_features.main(
            ["--settings-file", str(settings_path), "--run-on", "local"]
        )
    # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Check filters
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        compute_features.main(
            [
                "--settings-file",
                str(settings_path),
                "--run-on",
                "slurm",
                "--extractors",
                "SAT-features-competition2012_revised_without_SatELite",
            ]
        )
    cli_tools.kill_slurm_jobs()
    # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        compute_features.main(
            [
                "--settings-file",
                str(settings_path),
                "--run-on",
                "slurm",
                "--instances",
                "bce7824.cnf",
            ]
        )
    cli_tools.kill_slurm_jobs()
    # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
