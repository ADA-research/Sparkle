import argparse

from sparkle_help.sparkle_settings import SettingState

class SetByUser(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest+'_nondefault', True)

def user_set(args, arg_name: str) -> SettingState:
	if hasattr(args, arg_name + '_nondefault'):
		return SettingState.CMD_LINE
	else:
		return SettingState.DEFAULT

