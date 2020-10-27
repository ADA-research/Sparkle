#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import argparse
from sparkle_help import sparkle_logging as sl


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()

	# Process command line arguments
	args = parser.parse_args()

	print('c Sparkle (Platform for evaluating empirical algorithms/solvers)')
	print('c Version: TBD')
	print('c License: TBD')
	print('c Written by Chuan Luo, Koen van der Blom, Jeroen Rook, and Holger H. Hoos')
	print('c Contact: k.van.der.blom@liacs.leidenuniv.nl')
	print('c For more details see README.md')

