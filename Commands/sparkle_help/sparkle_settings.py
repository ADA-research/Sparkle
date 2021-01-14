import configparser
from enum import Enum
from pathlib import Path
from pathlib import PurePath

try:
	from sparkle_help import sparkle_logging as slog
	from sparkle_help import sparkle_global_help as sgh
except ImportError:
	import sparkle_logging as slog
	import sparkle_global_help as sgh


class PerformanceMeasure(Enum):
	RUNTIME = 0
	QUALITY_ABSOLUTE = 1
	QUALITY = 1 # If not specified, assume ABSOLTUE QUALITY
	#QUALITY_RELATIVE = 2 # TODO: Add when this functionality is implemented


	def from_str(performance_measure):
		if performance_measure == 'RUNTIME':
			performance_measure = PerformanceMeasure.RUNTIME
		elif performance_measure == 'QUALITY_ABSOLUTE' or performance_measure == 'QUALITY':
			performance_measure = PerformanceMeasure.QUALITY_ABSOLUTE
	
		return performance_measure


class SolutionVerifier(Enum):
	NONE = 0
	SAT = 1


	def from_str(verifier):
		if verifier == 'NONE':
			verifier = SolutionVerifier.NONE
		elif verifier == 'SAT':
			verifier = SolutionVerifier.SAT

		return verifier


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
	DEFAULT_general_solution_verifier = SolutionVerifier.NONE
	DEFAULT_general_target_cutoff_time = 60
	DEFAULT_general_penalty_multiplier = 10

	DEFAULT_config_budget_per_run = 600
	DEFAULT_config_number_of_runs = 25

	DEFAULT_slurm_number_of_runs_in_parallel = 25
	DEFAULT_slurm_clis_per_node = 32

	DEFAULT_smac_target_cutoff_length = 'max'

	DEFAULT_ablation_racing = False


	def __init__(self, file_path: PurePath = None):
		# Settings 'dictionary' in configparser format
		self.__settings = configparser.ConfigParser()

		# Setting flags
		self.__general_performance_measure_set = SettingState.NOT_SET
		self.__general_solution_verifier_set = SettingState.NOT_SET
		self.__general_target_cutoff_time_set = SettingState.NOT_SET
		self.__general_penalty_multiplier_set = SettingState.NOT_SET

		self.__config_budget_per_run_set = SettingState.NOT_SET
		self.__config_number_of_runs_set = SettingState.NOT_SET

		self.__slurm_number_of_runs_in_parallel_set = SettingState.NOT_SET
		self.__slurm_clis_per_node_set = SettingState.NOT_SET
		self.__slurm_extra_options_set = dict()

		self.__smac_target_cutoff_length_set = SettingState.NOT_SET

		self.__ablation_racing_flag_set = SettingState.NOT_SET

		if file_path == None:
			# Initialise settings from default file path
			self.read_settings_ini()
		else:
			# Initialise settings from a given file path
			self.read_settings_ini(file_path)

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

			option_names = ('solution_verifier',) # Comma so python understands it's a tuple...
			for option in option_names:
				if file_settings.has_option(section, option):
					value = SolutionVerifier.from_str(file_settings.get(section, option))
					self.set_general_solution_verifier(value, state)
					file_settings.remove_option(section, option)

			option_names = ('target_cutoff_time', 'smac_each_run_cutoff_time', 'cutoff_time_each_performance_computation')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.getint(section, option)
					self.set_general_target_cutoff_time(value, state)
					file_settings.remove_option(section, option)

			option_names = ('penalty_multiplier', 'penalty_number')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.getint(section, option)
					self.set_general_penalty_multiplier(value, state)
					file_settings.remove_option(section, option)

			section = 'configuration'
			option_names = ('budget_per_run', 'smac_whole_time_budget')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.getint(section, option)
					self.set_config_budget_per_run(value, state)
					file_settings.remove_option(section, option)

			section = 'configuration'
			option_names = ('number_of_runs', 'num_of_smac_runs')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.getint(section, option)
					self.set_config_number_of_runs(value, state)
					file_settings.remove_option(section, option)

			section = 'slurm'
			option_names = ('number_of_runs_in_parallel', 'num_of_smac_runs_in_parallel', 'num_job_in_parallel')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.getint(section, option)
					self.set_slurm_number_of_runs_in_parallel(value, state)
					file_settings.remove_option(section, option)

			section = 'slurm'
			option_names = ('clis_per_node', )
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.getint(section, option)
					self.set_slurm_clis_per_node(value, state)
					file_settings.remove_option(section, option)

			section = 'smac'
			option_names = ('target_cutoff_length', 'smac_each_run_cutoff_length')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.get(section, option)
					self.set_smac_target_cutoff_length(value, state)
					file_settings.remove_option(section, option)

			section = 'ablation'
			option_names = ('racing', 'ablation_racing')
			for option in option_names:
				if file_settings.has_option(section, option):
					value = file_settings.getboolean(section, option)
					self.set_ablation_racing_flag(value, state)
					file_settings.remove_option(section, option)

			# TODO: Report on any unknown settings that were read
			sections = file_settings.sections()

			for section in sections:
				for option in file_settings[section]:
					# TODO: Quick fix to support partitions and excludes, but should not allow any option
					if section == "slurm":
						print("Unrecognised SLURM option '{option}' found in {file}. Option is added to any SLURM batches".format(
							option=option,
							file=str(file_path)))
						value = file_settings.get(section, option)
						self.add_slurm_extra_option(option, value, state)
					else:
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


	### General settings ###


	def set_general_performance_measure(self, value: PerformanceMeasure = DEFAULT_general_performance_measure, origin: SettingState = SettingState.DEFAULT):
		section = 'general'
		name = 'performance_measure'

		if value != None and self.__check_setting_state(self.__general_performance_measure_set, origin, name):
			self.__init_section(section)
			self.__general_performance_measure_set = origin
			self.__settings[section][name] = value.name

		return


	def get_general_performance_measure(self) -> PerformanceMeasure:
		if self.__general_performance_measure_set == SettingState.NOT_SET:
			self.set_general_performance_measure()

		return PerformanceMeasure.from_str(self.__settings['general']['performance_measure'])


	def set_general_penalty_multiplier(self, value: int = DEFAULT_general_penalty_multiplier, origin: SettingState = SettingState.DEFAULT):
		section = 'general'
		name = 'penalty_multiplier'

		if value != None and self.__check_setting_state(self.__general_penalty_multiplier_set, origin, name):
			self.__init_section(section)
			self.__general_penalty_multiplier_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_general_penalty_multiplier(self) -> int:
		if self.__general_penalty_multiplier_set == SettingState.NOT_SET:
			self.set_general_penalty_multiplier()

		return int(self.__settings['general']['penalty_multiplier'])


	def get_penalised_time(self) -> int:
		penalty_multiplier = self.get_general_penalty_multiplier()
		cutoff_time = self.get_general_target_cutoff_time()
		penalised_time = cutoff_time * penalty_multiplier

		return penalised_time


	def set_general_solution_verifier(self, value: SolutionVerifier = DEFAULT_general_solution_verifier, origin: SettingState = SettingState.DEFAULT):
		section = 'general'
		name = 'solution_verifier'

		if value != None and self.__check_setting_state(self.__general_solution_verifier_set, origin, name):
			self.__init_section(section)
			self.__general_solution_verifier_set = origin
			self.__settings[section][name] = value.name

		return


	def get_general_solution_verifier(self) -> SolutionVerifier:
		if self.__general_solution_verifier_set == SettingState.NOT_SET:
			self.set_general_solution_verifier()

		return SolutionVerifier.from_str(self.__settings['general']['solution_verifier'])


	def set_general_target_cutoff_time(self, value: int = DEFAULT_general_target_cutoff_time, origin: SettingState = SettingState.DEFAULT):
		section = 'general'
		name = 'target_cutoff_time'

		if value != None and self.__check_setting_state(self.__general_target_cutoff_time_set, origin, name):
			self.__init_section(section)
			self.__general_target_cutoff_time_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_general_target_cutoff_time(self) -> int:
		if self.__general_target_cutoff_time_set == SettingState.NOT_SET:
			self.set_general_target_cutoff_time()

		return int(self.__settings['general']['target_cutoff_time'])


	### Configuration settings ###


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
		section = 'configuration'
		name = 'number_of_runs'

		if value != None and self.__check_setting_state(self.__config_number_of_runs_set, origin, name):
			self.__init_section(section)
			self.__config_number_of_runs_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_config_number_of_runs(self) -> int:
		if self.__config_number_of_runs_set == SettingState.NOT_SET:
			self.set_config_number_of_runs()

		return int(self.__settings['configuration']['number_of_runs'])


	### Configuration: SMAC specific settings ###


	def set_smac_target_cutoff_length(self, value: str = DEFAULT_smac_target_cutoff_length, origin: SettingState = SettingState.DEFAULT):
		section = 'smac'
		name = 'target_cutoff_length'

		if value != None and self.__check_setting_state(self.__smac_target_cutoff_length_set, origin, name):
			self.__init_section(section)
			self.__smac_target_cutoff_length_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_smac_target_cutoff_length(self) -> str:
		if self.__smac_target_cutoff_length_set == SettingState.NOT_SET:
			self.set_smac_target_cutoff_length()

		return self.__settings['smac']['target_cutoff_length']


	### Slurm settings ###


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


	def set_slurm_clis_per_node(self, value: int = DEFAULT_slurm_clis_per_node, origin: SettingState = SettingState.DEFAULT):
		section = 'slurm'
		name = 'clis_per_node'

		if value != None and self.__check_setting_state(self.__slurm_clis_per_node_set, origin, name):
			self.__init_section(section)
			self.__slurm_clis_per_node_set = origin
			self.__settings[section][name] = str(value)

		return


	def get_slurm_clis_per_node(self) -> int:
		if self.__slurm_clis_per_node_set == SettingState.NOT_SET:
			self.set_slurm_clis_per_node()

		return int(self.__settings['slurm']['clis_per_node'])


	### SLURM extra options

	def add_slurm_extra_option(self, name: str, value: str, origin: SettingState = SettingState.DEFAULT):
		section = "slurm_extra"

		current_state = self.__slurm_extra_options_set[name] if name in self.__slurm_extra_options_set else SettingState.NOT_SET

		if value != None and self.__check_setting_state(current_state, origin, name):
			self.__init_section(section)
			self.__slurm_extra_options_set[name] = origin
			self.__settings[section][name] = str(value)

	def get_slurm_extra_options(self) -> dict:
		section = "slurm_extra"
		options = dict()

		if "slurm_extra" in self.__settings.sections():
			for option in self.__settings["slurm_extra"]:
				options[option] = self.__settings.get(section, option)

		return options



	### Ablation settings ###

	def set_ablation_racing_flag(self, value: bool = DEFAULT_ablation_racing, origin: SettingState = SettingState.DEFAULT):
		section = 'ablation'
		name = 'racing'

		if value != None and self.__check_setting_state(self.__ablation_racing_flag_set, origin, name):
			self.__init_section(section)
			self.__ablation_racing_flag_set = origin
			self.__settings[section][name] = str(value)

		return

	def get_ablation_racing_flag(self) -> bool:
		if self.__ablation_racing_flag_set == SettingState.NOT_SET:
			self.set_ablation_racing_flag()

		return bool(self.__settings['ablation']['racing'])

