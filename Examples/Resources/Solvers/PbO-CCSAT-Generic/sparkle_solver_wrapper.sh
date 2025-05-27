#!/bin/bash
# Solver wrapper for PbO-CSSAT-Generic in Bash script. (Requires Bash 4 and jq)

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

# The remaining arguments will be possible parameters you defined in your .pcs file
# Construct call from args dictionary
cmd="${solverdir}/PbO-CCSAT -inst ${instance} -seed ${seed}"

for i in "${!args[@]}"
do
    cmd+=" -${i} ${args[$i]}"
done

#echo $cmd  # TODO remove
output="$($cmd)"

# Print original output so the solution can be verified by SATVerifier
echo $output

# Parse the output
status="CRASHED"  # For possible string values here, see sparkle.types.SolverStatus

while IFS= read -r line; do
    if [[ $line == *"s SATISFIABLE"* ]]; then
        status="SAT"
        break
    elif [[ $line == *"s UNSATISFIABLE"* ]]; then
        status="UNSAT"
        break
    elif [[ $line == *"s UNKNOWN"* ]]; then
        status="TIMEOUT"
        break
    fi
done < <(printf '%s' "$output")

# Create new dictionary to communicate back to sparkle
echo "{\"status\": \"$status\", \"quality\": 0, \"solver_call\": \"$cmd\"}"
