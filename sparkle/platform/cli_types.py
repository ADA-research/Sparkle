#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper types for command line interface."""

from enum import Enum


class VerbosityLevel(Enum):
    """Possible setting states."""

    QUIET = 0
    STANDARD = 1

    @staticmethod
    def from_string(name: str) -> "VerbosityLevel":
        """Converts string to VerbosityLevel."""
        try:
            return VerbosityLevel[name]
        except KeyError:
            raise ValueError(f"'{name}' is not a valid VerbosityLevel")
