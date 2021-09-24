#!/bin/env sh

# Script to cancel all jobs send to slurm from a certain time
# To source at the beginning of a script and call 'kill_all_started_jobs_slurm' at the end

STARTTIME=$(date -Iseconds)

kill_started_jobs_slurm(){
  jobsid=$(squeue -o "%u %V %A " | awk "{if (\$1 == \"$USER\" && \$2 >= \"$STARTTIME\") {print \$3}}")
  scancel $jobsid 
}


