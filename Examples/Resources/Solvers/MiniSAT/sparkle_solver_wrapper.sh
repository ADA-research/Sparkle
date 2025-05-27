#!/bin/bash
# Solver wrapper for MiniSat in Bash script. (Requires Bash 4 and jq)

# Read the arguments from the commandline and parse it into a dictionary
commandargs=("$@")

# A JSON parser to Bash dictionary (From https://stackoverflow.com/questions/71385680/json-dictionary-to-bash-hash-table-using-readarray)
declare -A args="($(jq -r 'to_entries[] | @sh "[\(.key)]=\(.value)"' <<< "$commandargs"))"

solverdir="${args['solver_dir']}"  # Where to find our source files
objectives="${args['objectives']}"  # Objectives to report on
instance="${args['instance']}"  # Path to the instance to execute

# Other possible standard parameters we could be interested in
cutoff_time="${args['cutoff_time']}"  # Maximum CPU time in seconds
seed="${args['seed']}"  # Seed to use

# Remove the default parameters from the dictionary
unset args['solver_dir']
unset args['objectives']
unset args['instance']
unset args['cutoff_time']
unset args['seed']

# Construct call from args dictionary
cmd="${solverdir}/minisat"

# This Solver does have configurable parameters, but no .pcs file
for i in "${!args[@]}"
do
    cmd+=" -${i}=${args[$i]}"
done

# Set seed
cmd+=" -rnd-seed=${seed}"
# For minisat the instance is at the end
cmd+=" ${instance}"

# Catch SIGTERM and determine behaviour: If we get killed, set status to TIMEOUT?
trap "echo {\"status\": \"TIMEOUT\", \"quality\": 0, \"solver_call\": \"$cmd\"}; exit $?" INT TERM EXIT KILL

output="$($cmd)"

# Print original output so the solution can be verified by SATVerifier
echo "$output"

# Parse the output
status="CRASHED"  # For possible string values here, see sparkle.types.SolverStatus

while IFS= read -r line; do
    if [[ $line == *"SATISFIABLE"* ]]; then
        status="SAT"
        break
    elif [[ $line == *"UNSATISFIABLE"* ]]; then
        status="UNSAT"
        break
    elif [[ $line == *"INDETERMINATE"* ]]; then
        status="TIMEOUT"
        break
    fi
done < <(printf '%s' "$output")

# Create new dictionary to communicate back to sparkle
echo "{\"status\": \"$status\", \"quality\": 0, \"solver_call\": \"$cmd\"}"
