#!/bin/bash
# Template for users to create Bash script solver wrappers. (Requires Bash 4 and jq)

# Read the arguments from the commandline and parse it into a dictionary
commandargs=("$@")

# A JSON parser to Bash dictionary (From https://stackoverflow.com/questions/71385680/json-dictionary-to-bash-hash-table-using-readarray)
declare -A args="($(jq -r 'to_entries[] | @sh "[\(.key)]=\(.value)"' <<< "$commandargs"))"

solverdir="${args['solver_dir']}"  # Where to find our source files
objectives="${args['objectives']}"  # Objectives to report on
instance="${args['instance']}"  # Path to the instance to execute
seed="${args['seed']}"  # Seed to use

# Other possible standard parameters we could be interested in
cutoff_time="${args['cutoff_time']}"

# Remove the default parameters from the dictionary
unset args['solver_dir']
unset args['objectives']
unset args['instance']
unset args['cutoff_time']
unset args['seed']

# The remaining arguments will be possible parameters you defined in your .pcs file
# Construct call from args dictionary
cmd="${solverdir}/YOUR_EXECUTABLE_HERE"

for i in "${!args[@]}"
do
    cmd+=" -${i} ${args[$i]}"
done

# Optional, recommended: Catch SIGTERM and determine behaviour, if we get killed, set status to TIMEOUT
trap "echo {\"status\": \"TIMEOUT\", \"quality\": 0, \"solver_call\": \"$cmd\"}; exit $?" INT TERM EXIT KILL

# Execute the solver
output="$($cmd)"

# Optional: Print original output so the solution can be verified by SolutionVerifier
echo "$output"

# Parse the output
status="CRASHED"  # For possible string values here, see sparkle.types.SolverStatus

while IFS= read -r line; do
    if [[ $line == *"s SATISFIABLE"* ]]; then
        status="SUCCESS"
        break
    elif [[ $line == *"s UNSATISFIABLE"* ]]; then
        status="SUCCESS"
        break
    elif [[ $line == *"s UNKNOWN"* ]]; then
        status="TIMEOUT"
        break
    fi
done < <(printf '%s' "$output")

# Create new dictionary to communicate back to sparkle
# NOTE: The \" around string key/value is essential for Python to parse it
echo "{\"status\": \"$status\", \"quality\": 0, \"solver_call\": \"$cmd\"}"
