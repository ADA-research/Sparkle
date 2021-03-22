#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

from enum import Enum


class CommandName(Enum):
	ABOUT = 0
	ADD_FEATURE_EXTRACTOR = 1
	ADD_INSTANCES = 2
	ADD_SOLVER = 3
	CLEANUP_CURRENT_SPARKLE_PLATFORM = 4
	CLEANUP_TEMPORARY_FILES = 5
	COMPUTE_FEATURES = 6
	COMPUTE_MARGINAL_CONTRIBUTION = 7
	CONFIGURE_SOLVER = 8
	CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR = 9
	GENERATE_REPORT = 10
	INITIALISE = 11
	LOAD_RECORD = 12
	REMOVE_FEATURE_EXTRACTOR = 13
	REMOVE_INSTANCES = 14
	REMOVE_RECORD = 15
	REMOVE_SOLVER = 16
	RUN_ABLATION = 17
	RUN_SOLVERS = 18
	RUN_SPARKLE_PORTFOLIO_SELECTOR = 19
	RUN_STATUS = 20
	SAVE_RECORD = 21
	SPARKLE_WAIT = 22
	SYSTEM_STATUS = 23
	VALIDATE_CONFIGURED_VS_DEFAULT = 24

	def from_str(command_name: str):
		if command_name == 'ABOUT':
			command_name = CommandName.ABOUT
		elif command_name == 'ADD_FEATURE_EXTRACTOR':
			command_name = CommandName.ADD_FEATURE_EXTRACTOR
		elif command_name == 'ADD_INSTANCES':
			command_name = CommandName.ADD_INSTANCES
		elif command_name == 'ADD_SOLVER':
			command_name = CommandName.ADD_SOLVER
		elif command_name == 'CLEANUP_CURRENT_SPARKLE_PLATFORM':
			command_name = CommandName.CLEANUP_CURRENT_SPARKLE_PLATFORM
		elif command_name == 'CLEANUP_TEMPORARY_FILES':
			command_name = CommandName.CLEANUP_TEMPORARY_FILES
		elif command_name == 'COMPUTE_FEATURES':
			command_name = CommandName.COMPUTE_FEATURES
		elif command_name == 'COMPUTE_MARGINAL_CONTRIBUTION':
			command_name = CommandName.COMPUTE_MARGINAL_CONTRIBUTION
		elif command_name == 'CONFIGURE_SOLVER':
			command_name = CommandName.CONFIGURE_SOLVER
		elif command_name == 'CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR':
			command_name = CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR
		elif command_name == 'GENERATE_REPORT':
			command_name = CommandName.GENERATE_REPORT
		elif command_name == 'INITIALISE':
			command_name = CommandName.INITIALISE
		elif command_name == 'LOAD_RECORD':
			command_name = CommandName.LOAD_RECORD
		elif command_name == 'REMOVE_FEATURE_EXTRACTOR':
			command_name = CommandName.REMOVE_FEATURE_EXTRACTOR
		elif command_name == 'REMOVE_INSTANCES':
			command_name = CommandName.REMOVE_INSTANCES
		elif command_name == 'REMOVE_RECORD':
			command_name = CommandName.REMOVE_RECORD
		elif command_name == 'REMOVE_SOLVER':
			command_name = CommandName.REMOVE_SOLVER
		elif command_name == 'RUN_ABLATION':
			command_name = CommandName.RUN_ABLATION
		elif command_name == 'RUN_SOLVERS':
			command_name = CommandName.RUN_SOLVERS
		elif command_name == 'RUN_SPARKLE_PORTFOLIO_SELECTOR':
			command_name = CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR
		elif command_name == 'RUN_STATUS':
			command_name = CommandName.RUN_STATUS
		elif command_name == 'SAVE_RECORD':
			command_name = CommandName.SAVE_RECORD
		elif command_name == 'SPARKLE_WAIT':
			command_name = CommandName.SPARKLE_WAIT
		elif command_name == 'SYSTEM_STATUS':
			command_name = CommandName.SYSTEM_STATUS
		elif command_name == 'VALIDATE_CONFIGURED_VS_DEFAULT':
			command_name = CommandName.VALIDATE_CONFIGURED_VS_DEFAULT

		return command_name


# NOTE: This dependency list contains all possible direct dependencies, including
# optional dependencies, and 'either or' dependencies
#
# Optional dpendency: GENERATE_REPORT is possible based on just CONFIGURE_SOLVER,
# but can optionally wait for VALIDATE_CONFIGURED_VS_DEFAULT as well
#
# 'Either or' dependency: GENERATE_REPORT can run after CONFIGURE_SOLVER, but
# also after CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR, but does not need both
#
# TODO: Check if empty dependency lists are correct. These were not important
# when this was implemented, but might have 'trivial' dependencies, such as the
# INITIALISE command.
COMMAND_DEPENDENCIES = {
	CommandName.ABOUT: [],
	CommandName.ADD_FEATURE_EXTRACTOR: [],
	CommandName.ADD_INSTANCES: [],
	CommandName.ADD_SOLVER: [],
	CommandName.CLEANUP_CURRENT_SPARKLE_PLATFORM: [],
	CommandName.CLEANUP_TEMPORARY_FILES: [],
	CommandName.COMPUTE_FEATURES: [CommandName.ADD_FEATURE_EXTRACTOR, CommandName.ADD_INSTANCES],
	CommandName.COMPUTE_MARGINAL_CONTRIBUTION: [CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR],
	CommandName.CONFIGURE_SOLVER: [CommandName.ADD_INSTANCES, CommandName.ADD_SOLVER],
	CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR: [CommandName.COMPUTE_FEATURES, CommandName.RUN_SOLVERS],
	CommandName.GENERATE_REPORT: [CommandName.CONFIGURE_SOLVER, CommandName.VALIDATE_CONFIGURED_VS_DEFAULT, CommandName.RUN_ABLATION, CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR, CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR],
	CommandName.INITIALISE: [],
	CommandName.LOAD_RECORD: [],
	CommandName.REMOVE_FEATURE_EXTRACTOR: [],
	CommandName.REMOVE_INSTANCES: [],
	CommandName.REMOVE_RECORD: [],
	CommandName.REMOVE_SOLVER: [],
	CommandName.RUN_ABLATION: [CommandName.CONFIGURE_SOLVER],
	CommandName.RUN_SOLVERS: [CommandName.ADD_INSTANCES, CommandName.ADD_SOLVER],
	CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR: [CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR],
	CommandName.RUN_STATUS: [],
	CommandName.SAVE_RECORD: [],
	CommandName.SPARKLE_WAIT: [],
	CommandName.SYSTEM_STATUS: [],
	CommandName.VALIDATE_CONFIGURED_VS_DEFAULT: [CommandName.CONFIGURE_SOLVER]
}

