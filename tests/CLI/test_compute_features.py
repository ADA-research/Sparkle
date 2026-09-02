"""Test the compute features CLI entry point."""

import pytest
from pathlib import Path
from runrunner.base import Runner, Status

from sparkle.CLI import add_feature_extractor, add_instances, compute_features
from sparkle.instance import Instance_Set
from sparkle.platform import Settings
from sparkle.selector import Extractor
from sparkle.structures import FeatureDataFrame
from tests.CLI import tools as cli_tools


@pytest.mark.integration
def test_compute_features_external_instance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test computing features for an instance outside the platform directory."""
    settings_path = cli_tools.get_settings_path()
    extractor_path = (
        Path("Examples") / "Resources" / "Extractors" / "SAT-features-competition2012_"
        "revised_without_SatELite"
    ).absolute()
    instance_path = (
        Path("Examples") / "Resources" / "Instances" / "PTN2" / "plain7824.cnf"
    ).absolute()
    platform_instance_dir = tmp_path / "Instances"
    platform_instance_dir.mkdir()
    assert not instance_path.is_relative_to(platform_instance_dir)
    instance_set = Instance_Set(instance_path)
    extractor = Extractor(extractor_path)
    feature_data = FeatureDataFrame(
        tmp_path / "feature_data.csv",
        instance_pairs=instance_set.instance_pairs,
        extractor_data={extractor.name: extractor.features},
    )
    settings = Settings(settings_path)
    monkeypatch.setattr(settings, "DEFAULT_instance_dir", platform_instance_dir)
    monkeypatch.setattr(settings, "DEFAULT_extractor_dir", extractor_path.parent)
    monkeypatch.setattr(compute_features.gv, "settings", lambda: settings)
    log_dir = tmp_path / "Log"
    log_dir.mkdir()
    monkeypatch.setattr(compute_features.sl, "caller_log_dir", log_dir)

    runs = compute_features.compute_features(
        feature_data,
        recompute=False,
        run_on=Runner.LOCAL,
        instance_sets=[instance_set],
    )

    assert runs
    assert all(run.status == Status.COMPLETED for run in runs)
    computed_feature_data = FeatureDataFrame(feature_data.csv_filepath)
    instance_features = computed_feature_data.get_instance(
        *instance_set.instance_pairs[0], as_dataframe=True
    )
    assert not instance_features.isna().all().all()


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
                "PTN/bce7824.cnf",
            ]
        )
    cli_tools.kill_slurm_jobs()
    # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
