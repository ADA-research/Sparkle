import configparser
from enum import Enum
from pathlib import Path
from pathlib import PurePath

from sparkle_help import sparkle_logging as slog
from sparkle_help import sparkle_global_help as sgh


class PerformanceMeasure(Enum):
	RUNTIME = 0
	QUALITY_ABSOLUTE = 1
	QUALITY = 1 # If not specified, assume ABSOLTUE QUALITY
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
	# Settings path names and default
	__settings_file = Path('sparkle_settings.ini')
	__settings_dir = Path('Settings')
	DEFAULT_settings_path = PurePath(__settings_dir / __settings_file)

	# Constant default values
	DEFAULT_general_performance_measure = PerformanceMeasure.RUNTIME

	DEFAULT_config_target_cutoff_time = 60
	DEFAULT_config_budget_per_run = 600
	DEFAULT_config_number_of_runs = 25

	DEFAULT_slurm_number_of_runs_in_parallel = 25


	def __init__(self):
		# Settings 'dictionary' in configparser format
		self.__settings = configparser.ConfigParser()

		# Setting flags
		self.__general_performance_measure_set = SettingState.NOT_SET

		self.__config_target_cutoff_time_set = SettingState.NOT_SET
		self.__config_budget_per_run_set = SettingState.NOT_SET
		self.__config_number_of_runs_set = SettingState.NOT_SET

		self.__slurm_number_of_runs_in_parallel_set = SettingState.NOT_SET

		# Initialise settings from default file path
		self.read_settings_ini()

		return


	def read_settings_ini(self, file_path: PurePath = DEFAULT_settings_path, state: SettingState = SettingState.FILE):
		# Read file
		file_settings = configparser.ConfigParser()
		file_settings.read(str(file_path))

		# Set internal settings based on data read from FILE if they were read succesfully
		if file_settings.sections() != []:
			section = 'general'
			option_names = ('performance_measure', 'smac_run_obj')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = PerformanceMeasure.from_str(file_settings.get(section, option))
					self.set_general_performance_measure(value, state)
					file_settings.remove_option(section, option)

			section = 'configuration'
			option_names = ('target_cutoff_time', 'smac_each_run_cutoff_time')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.getint(section, option)
					self.set_config_target_cutoff_time(value, state)
					file_settings.remove_option(section, option)

			option_names = ('budget_per_run', 'smac_whole_time_budget')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.getint(section, option)
					self.set_config_budget_per_run(value, state)
					file_settings.remove_option(section, option)

			option_names = ('number_of_runs', 'num_of_smac_runs')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.getint(section, option)
					self.set_config_number_of_runs(value, state)
					file_settings.remove_option(section, option)

			section = 'slurm'
			option_names = ('number_of_runs_in_parallel', 'num_of_smac_runs_in_parallel')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.getint(section, option)
					self.set_slurm_number_of_runs_in_parallel(value, state)
					file_settings.remove_option(section, option)

			# TODO: Report on any unknown settings that were read
			sections = file_settings.sections()

			for section in sections:
				for option in file_settings[section]:
					print('Unrecognised section - option combination:\'', section, option, '\'in file', str(file_path), 'ignored') 

		# Print error if unable to read the settings
		else:
			print('ERROR: Failed to read settings from', str(file_path), 'The file may have been empty, located in a different path, or be in another format than INI. Settings from different sources will be used (e.g. default values).')

		return


	def write_used_settings(self):
		# Write to general output directory
		file_path_output = PurePath(sgh.sparkle_global_output_dir / slog.caller_out_dir / self.__settings_dir / self.__settings_file)
		self.write_settings_ini(Path(file_path_output))

		# Write to latest settings file
		file_path_latest = PurePath(self.__settings_dir / 'latest.ini')
		self.write_settings_ini(Path(file_path_latest))

		return


	def write_settings_ini(self, file_path: Path):
		# Create needed directories if they don't exist
		file_dir = file_path.parents[0]
		file_dir.mkdir(parents=True, exist_ok=True)

		# Write the settings to file
		with open(str(file_path), 'w') as settings_file:
			self.__settings.write(settings_file)

		return


	def __init_section(self, section: str):
		if section not in self.__settings:
			self.__settings[section] = {}

		return


	def __check_setting_state(self, current_state: SettingState, new_state: SettingState, name: str) -> bool:
		change_setting_ok = True

		if current_state == SettingState.FILE and new_state == SettingState.DEFAULT:
			change_setting_ok = False
			print('Warning: Atempting to overwrite setting for', name, 'with default value; keeping the value read from file!')
		elif current_state == SettingState.CMD_LINE and new_state == SettingState.DEFAULT:
			change_setting_ok = False
			print('Warning: Atempting to overwrite setting for', name, 'with default value; keeping the value read from command line!')
		elif current_state == SettingState.CMD_LINE and new_state == SettingState.FILE:
			change_setting_ok = False
			print('Warning: Atempting to overwrite setting for', name, 'with value from file; keeping the value read from command line!')

		return change_setting_ok


	def set_general_performance_measure(self, value: PerformanceMeasure = DEFAULT_general_performance_measure, origin: SettingState = SettingState.DEFAULT):
		print('debug: in set_perf_measure')
		section = 'general'
		name = 'performance_measure'

		if value != None and self.__check_setting_state(self.__general_performance_measure_set, origin, name):
			print('debug: setting perf_measure to', value, 'form', origin.name)

			self.__init_section(section)
			self.__general_performance_measure_set = origin
			self.__settings[section][name] = value.name

		return


	def get_general_performance_measure(self) -> PerformanceMeasure:
		if self.__general_performance_measure_set == SettingState.NOT_SET:
			self.set_general_performance_measure()

		return PerformanceMeasure.from_str(self.__settings['general']['performance_measure'])


	# TODO: Decide whether configuration and selection cutoff times should be separate or not
	def set_config_target_cutoff_time(self, value: int = DEFAULT_config_target_cutoff_time, origin: SettingState = SettingState.DEFAULT):
		section = 'configuration'
		name = 'target_cutoff_time'

		if value != None and self.__check_setting_state(self.__config_target_cutoff_time_set, origin, name):
			self.__init_section(section)
			self.__config_target_cutoff_time_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_config_target_cutoff_time(self) -> int:
		if self.__config_target_cutoff_time_set == SettingState.NOT_SET:
			self.set_config_target_cutoff_time()

		return int(self.__settings['configuration']['target_cutoff_time'])


	def set_config_budget_per_run(self, value: int = DEFAULT_config_budget_per_run, origin: SettingState = SettingState.DEFAULT):
		section = 'configuration'
		name = 'budget_per_run'

		if value != None and self.__check_setting_state(self.__config_budget_per_run_set, origin, name):
			self.__init_section(section)
			self.__config_budget_per_run_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_config_budget_per_run(self) -> int:
		if self.__config_budget_per_run_set == SettingState.NOT_SET:
			self.set_config_budget_per_run()

		return int(self.__settings['configuration']['budget_per_run'])


	def set_config_number_of_runs(self, value: int = DEFAULT_config_number_of_runs, origin: SettingState = SettingState.DEFAULT):
		print('debug: in set config num of runs')
		section = 'configuration'
		name = 'number_of_runs'

		if value != None and self.__check_setting_state(self.__config_number_of_runs_set, origin, name):
			print('debug: setting n_runs to', value, 'form', origin.name)
			self.__init_section(section)
			self.__config_number_of_runs_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_config_number_of_runs(self) -> int:
		if self.__config_number_of_runs_set == SettingState.NOT_SET:
			self.set_config_number_of_runs()

		return int(self.__settings['configuration']['number_of_runs'])


	def set_slurm_number_of_runs_in_parallel(self, value: int = DEFAULT_slurm_number_of_runs_in_parallel, origin: SettingState = SettingState.DEFAULT):
		section = 'slurm'
		name = 'number_of_runs_in_parallel'

		if value != None and self.__check_setting_state(self.__slurm_number_of_runs_in_parallel_set, origin, name):
			self.__init_section(section)
			self.__slurm_number_of_runs_in_parallel_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_slurm_number_of_runs_in_parallel(self) -> int:
		if self.__slurm_number_of_runs_in_parallel_set == SettingState.NOT_SET:
			self.set_slurm_number_of_runs_in_parallel()

		return int(self.__settings['slurm']['number_of_runs_in_parallel'])

