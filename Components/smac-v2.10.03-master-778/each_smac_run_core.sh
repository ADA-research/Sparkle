#!/bin/bash
# $1 path to scenario, all information about budget, path to instances, target function (sparkle smac wrapper) etc
# $2 seed
# $4 execution directory
# $3 Output file
./smac --scenario-file $1 --seed $2 --execdir $4 > $3
