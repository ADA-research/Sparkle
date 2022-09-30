''' Class and functions to manage the external code runners '''
from enum import Enum


class Runners(str, Enum):
    ''' Enumeration of the possible runners '''
    LOCAL = 'local'
    SLURM = 'slurm'
