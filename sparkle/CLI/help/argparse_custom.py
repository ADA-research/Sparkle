"""Custom helper class and functions to process CLI arguments with argparse."""

from __future__ import annotations
from pathlib import Path
from typing import Any


class ArgumentContainer:
    """Helper class for more convenient argument packaging and access."""

    def __init__(
        self: ArgumentContainer, names: list[str], kwargs: dict[str, Any]
    ) -> None:
        """Create an ArgumentContainer.

        Args:
            names: List of names for the contained argument. For positional arguments
                this will typically contain two, the first one starting with '-' and the
                second one starting with '--'.
            kwargs: Keyword arguments needed by the method parser.add_argument which adds
                the contained argument to a parser.
        """
        self.names = names
        self.kwargs = kwargs


AllJobsArgument = ArgumentContainer(
    names=["--all"],
    kwargs={"action": "store_true", "help": "use all known job ID(s) for the command"},
)

AllSolverConfigurationArgument = ArgumentContainer(
    names=["--all-configurations"],
    kwargs={
        "action": "store_true",
        "help": "use all known configurations for the command",
    },
)

AllConfigurationArgument = ArgumentContainer(
    names=["--all-configurations"],
    kwargs={"action": "store_true", "help": "use all known Solver configurations"},
)

BestConfigurationArgument = ArgumentContainer(
    names=["--best-configuration"],
    kwargs={
        "required": False,
        "nargs": "?",
        "type": Path,
        "const": True,
        "default": False,
        "help": "Paths to instance(s) or instanceset(s) over "
        "which to determine the best configuration. If "
        "empty, all known instances are used.",
    },
)

BestSolverConfigurationArgument = ArgumentContainer(
    names=["--best-configuration"],
    kwargs={
        "action": "store_true",
        "help": "use the best configurations for the command",
    },
)

CancelJobsArgument = ArgumentContainer(
    names=["--cancel"],
    kwargs={"action": "store_true", "help": "cancel the job(s) with the given ID(s)"},
)

CheckTypeArgument = ArgumentContainer(
    names=["type"],
    kwargs={
        "choices": [
            "extractor",
            "feature-extractor",
            "solver",
            "instance-set",
            "ExtractorFeature-Extractor",
            "Instance-Set",
            "Solver",
            "FeatureExtractor",
            "InstanceSet",
        ],
        "help": "type of the object to check",
    },
)

CheckPathArgument = ArgumentContainer(
    names=["path"], kwargs={"type": Path, "help": "path to the object to check"}
)

CleanupArgumentAll = ArgumentContainer(
    names=["--all"], kwargs={"action": "store_true", "help": "clean all output files"}
)

CleanupArgumentRemove = ArgumentContainer(
    names=["--remove"],
    kwargs={
        "action": "store_true",
        "help": "remove all files in the platform, including "
        "user data such as InstanceSets and Solvers",
    },
)

CleanUpPerformanceDataArgument = ArgumentContainer(
    names=["--performance-data"],
    kwargs={"action": "store_true", "help": "clean performance data from empty lines"},
)

ConfigurationArgument = ArgumentContainer(
    names=["--configuration"],
    kwargs={
        "required": False,
        "type": str,
        "nargs": "+",
        "help": "The indices of which configurations to use",
    },
)

DefaultSolverConfigurationArgument = ArgumentContainer(
    names=["--default-configuration"],
    kwargs={
        "action": "store_true",
        "help": "use the default configurations for the command",
    },
)

DeterministicArgument = ArgumentContainer(
    names=["--deterministic"],
    kwargs={
        "action": "store_true",
        "help": "Flag indicating the solver is deterministic",
    },
)

DownloadExamplesArgument = ArgumentContainer(
    names=["--download-examples"],
    kwargs={
        "action": "store_true",
        "default": False,
        "required": False,
        "help": "Download the Examples into the directory.",
    },
)

ExtractorPathArgument = ArgumentContainer(
    names=["extractor_path"],
    kwargs={
        "metavar": "extractor-path",
        "type": str,
        "help": "path or nickname of the feature extractor",
    },
)

GenerateJSONArgument = ArgumentContainer(
    names=["--only-json"],
    kwargs={
        "required": False,
        "default": False,
        "type": bool,
        "help": "if set to True, only generate machine readable output",
    },
)

InstancePathOptional = ArgumentContainer(
    names=["instance_path"],
    kwargs={
        "type": Path,
        "nargs": "?",
        "help": "Path to an instance to use for the command",
    },
)

InstanceSetPathsArgument = ArgumentContainer(
    names=[
        "--instance-path",
        "--instance-set-path",
        "--instance",
        "--instance-set",
        "--instances",
        "--instance-sets",
        "--instance-paths",
        "--instance-set-paths",
    ],
    kwargs={
        "required": False,
        "nargs": "+",
        "type": Path,
        "help": "Path to an instance (set)",
    },
)

InstanceSetRequiredArgument = ArgumentContainer(
    names=["--instance", "--instance-set"],
    kwargs={"required": True, "type": Path, "help": "path to instance (set)"},
)

InstanceSetTestArgument = ArgumentContainer(
    names=["--instance-set-test"],
    kwargs={"required": False, "type": Path, "help": "path to test instance set"},
)

InstanceSetTrainArgument = ArgumentContainer(
    names=["--instance-set-train"],
    kwargs={"required": True, "type": Path, "help": "path to training instance set"},
)

InstanceSetTestAblationArgument = ArgumentContainer(
    names=["--instance-set-test"],
    kwargs={"required": False, "type": str, "help": "path to test instance set"},
)

InstanceSetTrainOptionalArgument = ArgumentContainer(
    names=["--instance-set-train"],
    kwargs={"required": False, "type": Path, "help": "path to training instance set"},
)

InstanceSetsReportArgument = ArgumentContainer(
    names=["--instance-sets", "--instance-set"],
    kwargs={
        "required": False,
        "nargs": "+",
        "type": str,
        "help": "Instance Set(s) to use for the report. If not "
        "specified, all Instance Sets are used.",
    },
)

InstancesPathArgument = ArgumentContainer(
    names=["instances_path"],
    kwargs={
        "metavar": "instances-path",
        "type": str,
        "help": "path to the instance set",
    },
)

InstancesPathRemoveArgument = ArgumentContainer(
    names=["instances_path"],
    kwargs={
        "metavar": "instances-path",
        "type": str,
        "help": "path to or nickname of the instance set",
    },
)

JobIDsArgument = ArgumentContainer(
    names=["--job-ids"],
    kwargs={
        "required": False,
        "nargs": "+",
        "type": str,
        "default": None,
        "help": "job ID(s) to use for the command",
    },
)

NicknameFeatureExtractorArgument = ArgumentContainer(
    names=["--nickname"],
    kwargs={"type": str, "help": "set a nickname for the feature extractor"},
)

NicknameInstanceSetArgument = ArgumentContainer(
    names=["--nickname"],
    kwargs={"type": str, "help": "set a nickname for the instance set"},
)

NicknamePortfolioArgument = ArgumentContainer(
    names=["--portfolio-name"],
    kwargs={
        "type": Path,
        "help": "Specify a name of the portfolio. "
        "If none is given, one will be generated.",
    },
)

NicknameSolverArgument = ArgumentContainer(
    names=["--nickname"], kwargs={"type": str, "help": "set a nickname for the solver"}
)

NoCopyArgument = ArgumentContainer(
    names=["--no-copy"],
    kwargs={
        "action": "store_true",
        "required": False,
        "help": "do not copy the source directory to "
        "the platform directory, but create a"
        " symbolic link instead",
    },
)

NoSavePlatformArgument = ArgumentContainer(
    names=["--no-save"],
    kwargs={
        "action": "store_false",
        "default": True,
        "required": False,
        "help": "do not save the platform upon re-initialisation.",
    },
)

RecomputeFeaturesArgument = ArgumentContainer(
    names=["--recompute"],
    kwargs={
        "action": "store_true",
        "help": "Re-run feature extractor for instances with "
        "previously computed features",
    },
)

RecomputePortfolioSelectorArgument = ArgumentContainer(
    names=["--recompute-portfolio-selector"],
    kwargs={
        "action": "store_true",
        "help": "force the construction of a new portfolio "
        "selector even when it already exists for the current "
        "feature and performance data.",
    },
)

RecomputeRunSolversArgument = ArgumentContainer(
    names=["--recompute"],
    kwargs={
        "action": "store_true",
        "help": "recompute the performance of all solvers on all instances",
    },
)

PerformanceDataJobsArgument = ArgumentContainer(
    names=["--performance-data-jobs"],
    kwargs={
        "action": "store_true",
        "help": "compute the remaining jobs in the Performance DataFrame",
    },
)

RebuildRunsolverArgument = ArgumentContainer(
    names=["--rebuild-runsolver"],
    kwargs={
        "action": "store_true",
        "required": False,
        "default": False,
        "help": "Clean the RunSolver executable and rebuild it.",
    },
)


SeedArgument = ArgumentContainer(
    names=["--seed"], kwargs={"type": int, "help": "seed to use for the command"}
)

SelectionScenarioArgument = ArgumentContainer(
    names=["--selection-scenario"],
    kwargs={"required": True, "type": Path, "help": "the selection scenario to use"},
)

SelectorAblationArgument = ArgumentContainer(
    names=["--solver-ablation"],
    kwargs={
        "required": False,
        "action": "store_true",
        "help": "construct a selector for each solver ablation combination",
    },
)

SettingsFileArgument = ArgumentContainer(
    names=["--settings-file"],
    kwargs={
        "type": Path,
        "help": "Specify the settings file to use in case you want"
        " supplement or override the default file.",
    },
)

SkipChecksArgument = ArgumentContainer(
    names=["--skip-checks"],
    kwargs={
        "dest": "run_checks",
        "default": True,
        "action": "store_false",
        "help": "Checks the solver's functionality by testing it on an instance "
        "and the pcs file, when applicable.",
    },
)

SnapshotArgument = ArgumentContainer(
    names=["snapshot_file_path"],
    kwargs={
        "metavar": "snapshot-file-path",
        "type": str,
        "help": "path to the snapshot file",
    },
)

SnapshotNameArgument = ArgumentContainer(
    names=["--name"],
    kwargs={"required": False, "type": str, "help": "name of the snapshot"},
)

SolverArgument = ArgumentContainer(
    names=["--solver"],
    kwargs={"required": True, "type": Path, "help": "path to solver"},
)

SolversArgument = ArgumentContainer(
    names=["--solvers", "--solver-paths", "--solver", "--solver-path"],
    kwargs={
        "required": False,
        "nargs": "+",
        "type": str,
        "help": "Specify the list of solvers to be "
        "used. If not specifed, all solvers "
        "known in Sparkle will be used.",
    },
)
SolverRemoveArgument = ArgumentContainer(
    names=["solver"],
    kwargs={
        "metavar": "solver",
        "type": str,
        "help": "name, path to or nickname of the solver",
    },
)

SolverPathArgument = ArgumentContainer(
    names=["solver_path"],
    kwargs={"metavar": "solver-path", "type": str, "help": "path to the solver"},
)

SolversReportArgument = ArgumentContainer(
    names=["--solvers", "--solver"],
    kwargs={
        "nargs": "+",
        "type": str,
        "default": None,
        "help": "Solver(s) to use for the report. If not specified, all solvers are "
        "included.",
    },
)

TestSetRunAllConfigurationArgument = ArgumentContainer(
    names=["--test-set-run-all-configurations"],
    kwargs={
        "required": False,
        "action": "store_true",
        "help": "run all found configurations on the test set",
    },
)

UseFeaturesArgument = ArgumentContainer(
    names=["--use-features"],
    kwargs={
        "required": False,
        "action": "store_true",
        "help": "use the training set's features for configuration",
    },
)

SolutionVerifierArgument = ArgumentContainer(
    names=["--solution-verifier"],
    kwargs={
        "type": str,
        "default": None,
        "help": "the class name of the solution verifier to use "
        "for the Solver. If it is a Path, will resolve as "
        "a SolutionFileVerifier class with the specified "
        "Path instead.",
    },
)

ObjectiveArgument = ArgumentContainer(
    names=["--objective"], kwargs={"type": str, "help": "the objective to use."}
)
