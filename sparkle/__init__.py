"""Init file for Sparkle."""

from sparkle.configurator import (
    SMAC2,
    SMAC2Scenario,
    SMAC3,
    SMAC3Scenario,
    ParamILS,
    ParamILSScenario,
    IRACE,
    IRACEScenario,
)

from sparkle.instance import (
    FileInstanceSet,
    MultiFileInstanceSet,
    IterableFileInstanceSet,
)

from sparkle.selector import (
    Selector,
    SelectionScenario,
    Extractor,
)

from sparkle.solver import (
    Solver,
)

from sparkle.structures import (
    PerformanceDataFrame,
    FeatureDataFrame,
)

# No import from .tools, not important enough

__all__ = [
    "SMAC2",
    "SMAC2Scenario",
    "SMAC3",
    "SMAC3Scenario",
    "ParamILS",
    "ParamILSScenario",
    "IRACE",
    "IRACEScenario",
    "FileInstanceSet",
    "MultiFileInstanceSet",
    "IterableFileInstanceSet",
    "Selector",
    "SelectionScenario",
    "Extractor",
    "Solver",
    "PerformanceDataFrame",
    "FeatureDataFrame",
]

__name__ = "sparkle"
__version__ = "0.9.5"

description = "Platform for evaluating empirical algorithms"
licence = "MIT"
authors = [
    "Koen van der Blom",
    "Jeremie Gobeil",
    "Holger H. Hoos",
    "Chuan Luo",
    "Jeroen Rook",
    "Thijs Snelleman",
]
contact = "sparkle@aim.rwth-aachen.de"
