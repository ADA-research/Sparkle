#!/bin/bash
# Solver wrapper for CSCCAT in Bash script. (Requires Bash 4 and jq)

# Read the arguments from the commandline and parse it into a dictionary, removing possible leading/trailing quotes
commandargs=$( sed -e "s/^'//" -e "s/'$//" <<< "$*" )

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
cmd="${solverdir}/CSCCSat ${instance} ${seed}"

# Setup default output
status="CRASHED"  # For possible string values here, see sparkle.types.SolverStatus

# Create new dictionary to communicate back to sparkle
# We use a function to exit the script, to pass it to the bash trap function
sparkleoutput()
{
    # NOTE: The \" around string key/value is essential for Python to parse it
    echo "{\"status\": \"$status\", \"quality\": 0, \"solver_call\": \"$cmd\"}"
    exit
}

# We prepare a trigger on regular exit and some termination signals
trap sparkleoutput 0 SIGTERM SIGINT SIGQUIT SIGABRT SIGHUP

# This Solver does not have configurable parameters, continue to execution
# Execute the solver, with duplicated output:
# - One to the terminal so it can be verified by SATVerifier and we record the 'latest' log
# - One to our variable so we can return the correct status to Sparkle
exec 5>&1
output="$($cmd |tee >(cat - >&5))"

# Parse the output
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
