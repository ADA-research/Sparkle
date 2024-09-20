"""This package provides specific Configurator class implementations for Sparkle."""
from sparkle.configurator.configurator import Configurator
from sparkle.configurator.implementations.smac2 import SMAC2, SMAC2Scenario


def resolve_configurator(configurator_name: str) -> Configurator:
    """Returns the Configurator subclass by name."""
    subclass_names = [SMAC2.__name__]
    if configurator_name in subclass_names:
        return eval(configurator_name)
    return None
