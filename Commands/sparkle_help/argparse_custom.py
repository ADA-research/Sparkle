"""Custom helper class and functions to process CLI arguments with argparse."""
import argparse

from Commands.sparkle_help.sparkle_settings import SettingState


class SetByUser(argparse.Action):
    """Possible action to execute for CLI argument."""

    def __call__(self, parser, namespace, values, option_string=None):
        """Set attributes when called."""
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest + "_nondefault", True)


def user_set_state(args, arg_name: str) -> SettingState:
    """Return the SettingState of an argument."""
    if hasattr(args, arg_name + "_nondefault"):
        return SettingState.CMD_LINE
    else:
        return SettingState.DEFAULT


def set_by_user(args, arg_name: str) -> bool:
    """Return whether an argument was set through the CLI by the user or not."""
    if hasattr(args, arg_name + "_nondefault"):
        return True
    else:
        return False
