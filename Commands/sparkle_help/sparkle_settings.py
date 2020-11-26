import configparser
from enum import Enum


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
		self.__settings = configparser.ConfigParser()
		self.__performance_measure_set = SettingState.NOT_SET
		self.__config_target_cutoff_time_set = SettingState.NOT_SET

		return


	def read_settings_ini(self):
		# TODO: Implement
		return


	# TODO: Decide on a sensible path to write to (maybe Log or Tmp)
	def write_settings_ini(file_path = 'sparkle_settings.ini'):
		with open (file_path, 'w') as settings_file:
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
		self.__performance_measure_set = origin
		self.__settings[section][name] = value.name

		return


	def get_performance_measure(self) -> PerformanceMeasure:
		if self.__performance_measure_set == SettingState.NOT_SET:
			self.set_performance_measure()

		return self.__settings['general']['performance_measure']


	# TODO: Decide whether configuration and selection cutoff times should be separate or not
	def set_config_target_cutoff_time(self, value: str = '60', origin: SettingState = SettingState.DEFAULT):
		section = 'configuration'
		name = 'config_target_cutoff_time'

		self.__init_section(section)
		self.__check_setting_state(self.__config_target_cutoff_time_set, origin, name)
		self.__performance_measure_set = origin
		self.__settings[section][name] = value

		return


	def get_config_target_cutoff_time(self) -> int:
		if self.__config_target_cutoff_time_set == SettingState.NOT_SET:
			self.set_config_target_cutoff_time()

		return self.__settings['configuration']['config_target_cutoff_time']

