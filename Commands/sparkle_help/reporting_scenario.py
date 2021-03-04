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


class Scenario(Enum):
	NONE = 0
	SELECTION = 1
	CONFIGURATION = 2


	def from_str(scenario):
		if scenario == 'NONE':
			scenario = Scenario.NONE
		elif scenario == 'SELECTION':
			scenario = Scenario.SELECTION
		elif scenario == 'CONFIGURATION':
			scenario = Scenario.CONFIGURATION

		return scenario


class ReportingScenario:
	# ReportingScenario path names and defaults
	__reporting_scenario_file = Path('latest_scenario.ini')
	__reporting_scenario_dir = Path('Output')
	DEFAULT_reporting_scenario_path = Path(PurePath(__reporting_scenario_dir / __reporting_scenario_file))

	# Constant default values
	DEFAULT_latest_scenario = Scenario.NONE

	DEFAULT_selection_portfolio_path = Path('')
	DEFAULT_selection_test_case_directory = Path('')

	DEFAULT_config_solver = Path('')
	DEFAULT_config_instance_set_train = Path('')
	DEFAULT_config_instance_set_test = Path('')


	def __init__(self):
		# ReportingScenario 'dictionary' in configparser format
		self.__scenario = configparser.ConfigParser()

		# Initialise scenario in default file path
		self.read_scenario_ini()

		return


	def read_scenario_ini(self, file_path: Path = DEFAULT_reporting_scenario_path):
		# If the file does not exist set default values
		if not Path(file_path).is_file():
			self.set_latest_scenario()
			self.set_selection_portfolio_path()
			self.set_selection_test_case_directory()
			self.set_config_solver()
			self.set_config_instance_set_train()
			self.set_config_instance_set_test()

		# Read file
		file_scenario = configparser.ConfigParser()
		file_scenario.read(str(file_path))

		# Set internal scenario based on data read from FILE if they were read successfully
		if file_scenario.sections() != []:
			section = 'latest'
			option_names = ('scenario',) # Comma so python understands it's a tuple...
			for option in option_names:
				if file_scenario.has_option(section, option):
					value = Scenario.from_str(file_scenario.get(section, option))
					self.set_latest_scenario(value)
					file_scenario.remove_option(section, option)

			section = 'selection'
			option_names = ('portfolio_path',) # Comma so python understands it's a tuple...
			for option in option_names:
				if file_scenario.has_option(section, option):
					value = Path(file_scenario.get(section, option))
					self.set_selection_portfolio_path(value)
					file_scenario.remove_option(section, option)

			section = 'selection'
			option_names = ('test_case_directory',) # Comma so python understands it's a tuple...
			for option in option_names:
				if file_scenario.has_option(section, option):
					value = Path(file_scenario.get(section, option))
					self.set_selection_test_case_directory(value)
					file_scenario.remove_option(section, option)

			section = 'configuration'
			option_names = ('solver',) # Comma so python understands it's a tuple...
			for option in option_names:
				if file_scenario.has_option(section, option):
					value = Path(file_scenario.get(section, option))
					self.set_config_solver(value)
					file_scenario.remove_option(section, option)

			option_names = ('instance_set_train',) # Comma so python understands it's a tuple...
			for option in option_names:
				if file_scenario.has_option(section, option):
					value = Path(file_scenario.get(section, option))
					self.set_config_instance_set_train(value)
					file_scenario.remove_option(section, option)

			option_names = ('instance_set_test',) # Comma so python understands it's a tuple...
			for option in option_names:
				if file_scenario.has_option(section, option):
					value = Path(file_scenario.get(section, option))
					self.set_config_instance_set_test(value)
					file_scenario.remove_option(section, option)

			# Report on any unknown settings that were read
			sections = file_scenario.sections()

			for section in sections:
				for option in file_scenario[section]:
					print('Unrecognised section - option combination:\'', section, option, '\'in file', str(file_path), 'ignored')

		# Print error if unable to read the scenario file
		else:
			print('ERROR: Failed to read latetst scenario from', str(file_path), 'The file may have been empty, or is in another format than INI. Default values will be used.')

		return


	def write_scenario_ini(self, file_path: Path = DEFAULT_reporting_scenario_path):
		# Create needed directories if they don't exist
		file_dir = file_path.parents[0]
		file_dir.mkdir(parents=True, exist_ok=True)

		# Write the scenario to file
		with open(str(file_path), 'w') as scenario_file:
			self.__scenario.write(scenario_file)

		return


	def __init_section(self, section: str):
		if section not in self.__scenario:
			self.__scenario[section] = {}

		return


	### Generic setters ###


	def path_setter(self, section: str, name: str, value: Path):
		if value != None:
			self.__init_section(section)
			self.__scenario[section][name] = str(value)

		self.write_scenario_ini()

		return


	### Generic getters ###


	def none_if_empty_path(self, path: Path):
		if str(path) == '' or str(path) == '.':
			path = None

		return path


	### Latest settings ###


	def set_latest_scenario(self, value: Scenario = DEFAULT_latest_scenario):
		section = 'latest'
		name = 'scenario'

		if value != None:
			self.__init_section(section)
			self.__scenario[section][name] = value.name

		self.write_scenario_ini()

		return


	def get_latest_scenario(self) -> Scenario:
		return Scenario.from_str(self.__scenario['latest']['scenario'])


	### Selection settings ###


	def set_selection_portfolio_path(self, value: Path = DEFAULT_selection_portfolio_path):
		section = 'selection'
		name = 'portfolio_path'
		self.path_setter(section, name, value)

		return


	def get_selection_portfolio_path(self) -> Path:
		return Path(self.__scenario['selection']['test_case_directory'])


	def set_selection_test_case_directory(self, value: Path = DEFAULT_selection_test_case_directory):
		section = 'selection'
		name = 'test_case_directory'
		self.path_setter(section, name, value)

		return


	def get_selection_test_case_directory(self) -> Path:
		try:
			path = self.__scenario['selection']['test_case_directory']
		except KeyError:
			path = ''

		return self.none_if_empty_path(Path(path))


	### Configuration settings ###


	def set_config_solver(self, value: Path = DEFAULT_config_solver):
		section = 'configuration'
		name = 'solver'
		self.path_setter(section, name, value)

		return


	def get_config_solver(self) -> Path:
		return self.none_if_empty_path(Path(self.__scenario['configuration']['solver']))


	def set_config_instance_set_train(self, value: Path = DEFAULT_config_instance_set_train):
		section = 'configuration'
		name = 'instance_set_train'
		self.path_setter(section, name, value)

		return


	def get_config_instance_set_train(self) -> Path:
		return self.none_if_empty_path(Path(self.__scenario['configuration']['instance_set_train']))


	def set_config_instance_set_test(self, value: Path = DEFAULT_config_instance_set_test):
		section = 'configuration'
		name = 'instance_set_test'
		self.path_setter(section, name, value)

		return


	def get_config_instance_set_test(self) -> Path:
		return self.none_if_empty_path(Path(self.__scenario['configuration']['instance_set_test']))
