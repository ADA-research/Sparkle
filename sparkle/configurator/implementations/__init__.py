"""This package provides specific Configurator class implementations for Sparkle."""
from sparkle.configurator.configurator import Configurator
from sparkle.configurator.implementations.irace import IRACE, IRACEScenario
from sparkle.configurator.implementations.paramils import ParamILS, ParamILSScenario
from sparkle.configurator.implementations.smac2 import SMAC2, SMAC2Scenario
from sparkle.configurator.implementations.smac3 import SMAC3, SMAC3Scenario


def resolve_configurator(configurator_name: str) -> Configurator:
    """Returns the Configurator subclass by name."""
    subclass_names = [IRACE.__name__, ParamILS.__name__, SMAC2.__name__, SMAC3.__name__]
    if configurator_name in subclass_names:
        return eval(configurator_name)
    return None
