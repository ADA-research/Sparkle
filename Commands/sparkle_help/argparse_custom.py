"""Custom helper class and functions to process CLI arguments with argparse."""
import argparse

from sparkle_help.sparkle_settings import SettingState


class SetByUser(argparse.Action):
    """Possible action to execute for CLI argument."""

    def __call__(self, parser, namespace, values, option_string = None):
        """
        Set attributes when called.

        Args:
            parser: Description
            namespace: Description
            values: Description
            option_string (None, optional): Description
        """
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest + "_nondefault", True)


def user_set_state(args: Namespace, arg_name: str) -> SettingState:
    """
    Return the SettingState of an argument.

    Args:
        args: Namespace returned by parse_args() function of argparse package.
        arg_name: Argument name.

    Returns:
        An object of type SettingState.
    """
    if hasattr(args, arg_name + "_nondefault"):
        return SettingState.CMD_LINE
    return SettingState.DEFAULT


def set_by_user(args: Namespace, arg_name: str) -> bool:
    """
    Return whether an argument was set through the CLI by the user or not.

    Args:
        args: Namespace returned by parse_args() function of argparse package.
        arg_name: Argument name.

    Returns:
      Boolean indicating whether the argument name is in the args namespace.
    """
    return hasattr(args, arg_name + "_nondefault"):
