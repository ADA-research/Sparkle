"""Init file for Sparkle."""

import sparkle.about as about

__version__ = about.version

from sparkle.configurator import (
    SMAC2, SMAC2Scenario,
    SMAC3, SMAC3Scenario,
    ParamILS, ParamILSScenario,
    IRACE, IRACEScenario,
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

