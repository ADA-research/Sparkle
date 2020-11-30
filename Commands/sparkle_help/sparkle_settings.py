import configparser
from enum import Enum
from pathlib import Path
from pathlib import PurePath

from sparkle_help import sparkle_logging as slog
from sparkle_help import sparkle_global_help as sgh


class PerformanceMeasure(Enum):
	RUNTIME = 0
	QUALITY_ABSOLUTE = 1
	#QUALITY_RELATIVE = 2 # TODO: Add when this functionality is implemented


	def from_str(performance_measure):
		if performance_measure == 'RUNTIME':
			performance_measure = PerformanceMeasure.RUNTIME
		elif performance_measure == 'QUALITY_ABSOLUTE':
			performance_measure = PerformanceMeasure.QUALITY_ABSOLUTE
	
		return performance_measure


class SettingState(Enum):
	NOT_SET = 0
	DEFAULT = 1
	FILE = 2
	CMD_LINE = 3


class Settings:
	def __init__(self):
		# Settings 'dictionary' in configparser format
		self.__settings = configparser.ConfigParser()

		# Settinsg directory name
		self.__settings_dir = 'Setting'

		# Setting flags
		self.__performance_measure_set = SettingState.NOT_SET
		self.__config_target_cutoff_time_set = SettingState.NOT_SET
		self.__config_budget_per_run_set = SettingState.NOT_SET
		self.__config_number_of_runs_set = SettingState.NOT_SET

		return


	def read_settings_ini(self):
		# TODO: Implement
		return


	def write_settings_ini(self, file_name: Path = Path('sparkle_settings.ini')):
		file_path = PurePath(sgh.sparkle_global_output_dir / slog.caller_out_dir / self.__settings_dir / file_name)

		# Create needed directories if they don't exist
		file_dir = Path(file_path).parents[0]
		file_dir.mkdir(parents=True, exist_ok=True)

		# Write the settings to file
		with open(str(file_path), 'w') as settings_file:
			self.__settings.write(settings_file)

		return


	def __init_section(self, section: str):
		if section not in self.__settings:
			self.__settings[section] = {}

		return


	def __check_setting_state(self, current_state: SettingState, new_state: SettingState, name: str):
		if current_state == SettingState.FILE and new_state == SettingState.DEFAULT:
			print('Warning: Setting from file for', name, 'is being overwritten by default values!')
		if current_state == SettingState.CMD_LINE and new_state == SettingState.DEFAULT:
			print('Warning: Setting from command line argument for', name, 'is being overwritten by default values!')
		if current_state == SettingState.CMD_LINE and new_state == SettingState.FILE:
			print('Warning: Setting from command line argument for', name, 'is being overwritten by setting from file!')

		return


	def set_performance_measure(self, value: PerformanceMeasure = PerformanceMeasure.RUNTIME, origin: SettingState = SettingState.DEFAULT):
		section = 'general'
		name = 'performance_measure'

		self.__init_section(section)
		self.__check_setting_state(self.__performance_measure_set, origin, name)

		if value != None:
			self.__performance_measure_set = origin
			self.__settings[section][name] = value.name

		return


	def get_performance_measure(self) -> PerformanceMeasure:
		if self.__performance_measure_set == SettingState.NOT_SET:
			self.set_performance_measure()

		return PerformanceMeasure.from_str(self.__settings['general']['performance_measure'])


	# TODO: Decide whether configuration and selection cutoff times should be separate or not
	def set_config_target_cutoff_time(self, value: int = 60, origin: SettingState = SettingState.DEFAULT):
		section = 'configuration'
		name = 'target_cutoff_time'

		self.__init_section(section)
		self.__check_setting_state(self.__config_target_cutoff_time_set, origin, name)

		if value != None:
			self.__config_target_cutoff_time_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_config_target_cutoff_time(self) -> int:
		if self.__config_target_cutoff_time_set == SettingState.NOT_SET:
			self.set_config_target_cutoff_time()

		return int(self.__settings['configuration']['target_cutoff_time'])


	def set_config_budget_per_run(self, value: int = 600, origin: SettingState = SettingState.DEFAULT):
		section = 'configuration'
		name = 'budget_per_run'

		self.__init_section(section)
		self.__check_setting_state(self.__config_budget_per_run_set, origin, name)

		if value != None:
			self.__config_budget_per_run_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_config_budget_per_run(self) -> int:
		if self.__config_budget_per_run_set == SettingState.NOT_SET:
			self.set_config_budget_per_run()

		return int(self.__settings['configuration']['budget_per_run'])


	def set_config_number_of_runs(self, value: int = 25, origin: SettingState = SettingState.DEFAULT):
		print('debug: setting n_runs to', value, 'form', origin.name)
		section = 'configuration'
		name = 'number_of_runs'

		self.__init_section(section)
		self.__check_setting_state(self.__config_number_of_runs_set, origin, name)

		if value != None:
			self.__config_number_of_runs_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_config_number_of_runs(self) -> int:
		if self.__config_number_of_runs_set == SettingState.NOT_SET:
			self.set_config_number_of_runs()

		return int(self.__settings['configuration']['number_of_runs'])

