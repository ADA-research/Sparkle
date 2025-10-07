"""This package provides configurator support for Sparkle."""

from sparkle.configurator.configurator import (
    Configurator,
    ConfigurationScenario,
    AblationScenario,
)

from sparkle.configurator.implementations import (
    SMAC2,
    SMAC2Scenario,
    SMAC3,
    SMAC3Scenario,
    ParamILS,
    ParamILSScenario,
    IRACE,
    IRACEScenario,
)
