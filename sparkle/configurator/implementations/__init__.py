"""This package provides specific Configurator class implementations for Sparkle."""
from sparkle.configurator.configurator import Configurator
from sparkle.configurator.implementations.smac_v2 import SMACv2


def resolve_configurator(configurator_name: str) -> Configurator:
    """Returns the Configurator subclass by name."""
    subclass_names = [SMACv2.__name__]
    if configurator_name in subclass_names:
        return eval(configurator_name)
    return None
