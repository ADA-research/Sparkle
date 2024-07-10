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
        return VerbosityLevel[name]
