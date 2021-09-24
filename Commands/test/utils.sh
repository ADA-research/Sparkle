#!/bin/bash

STARTTIME=$(date -Iseconds)

# Function to cancel all jobs sent to Slurm from the time this script was imported (STARTTIME)
# Source at the beginning of a script and call 'kill_all_started_jobs_slurm' at the end
kill_started_jobs_slurm(){
  jobids=$(squeue -o "%u %V %A " | awk "{if (\$1 == \"$USER\" && \$2 >= \"$STARTTIME\") {print \$3}}")
  scancel $jobids 
}

