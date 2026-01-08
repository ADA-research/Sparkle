#!/usr/bin/env bash
set -euo pipefail

# ---------- argument parsing ----------
HELP=false
FEATURES=false
EXTRACTOR_DIR=""
INSTANCE_FILE=""
FEATURE_GROUP=""
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h) HELP=true ;;
    -help) HELP=true ;;
    -features) FEATURES=true ;;
    -extractor_dir) EXTRACTOR_DIR="$2"; shift ;;
    -instance_file) INSTANCE_FILE="$2"; shift ;;
    -feature_group) FEATURE_GROUP="$2"; shift ;;
    -output_file) OUTPUT_FILE="$2"; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
  shift
done

if [[ "$HELP" == true ]]; then
  RESULT="["
  for k in $(printf "%s\n" "${!FEATURE_MAP_DICT[@]}" | sort); do
    v="${FEATURE_MAP_DICT[$k]}"
    GROUP="${v%%|*}"
    NAME="${v##*|}"
    RESULT+="('$GROUP', '$NAME'), "
  done
  RESULT="${RESULT%, }]"  # remove trailing comma + space
  printf "%s\n" "$RESULT"
  echo "-h --help show this string\n"\
       "-features show the features produced by the extractor"\
       "-extractor_dir directory where the extractor executable is located"\
       "-instance_file file to produce features for"\
       "-feature_group feature group to run the extractor for. If not provided, runs for all groups."\
       "-output_file file to write output to. If not present, print features instead."\
  exit 0
fi

# ---------- load generated FEATURE_MAP ----------
FEATURE_MAP=$(cat <<'EOF'
nvarsOrig,base,n_vars_original
nclausesOrig,base,n_clauses_original
nvars,base,n_vars
nclauses,base,n_clauses
reducedVars,base,reduced_vars
reducedClauses,base,reduced_clauses
Pre-featuretime,base,pre_featuretime
vars-clauses-ratio,base,vars_clauses_ratio
POSNEG-RATIO-CLAUSE-mean,base,Postive-Negative-Literals_clause_ratio_mean
POSNEG-RATIO-CLAUSE-coeff-variation,base,Postive-Negative-Literals_clause_coefficient_of_variation
POSNEG-RATIO-CLAUSE-min,base,Postive-Negative-Literals_clause_ratio_minimum
POSNEG-RATIO-CLAUSE-max,base,Postive-Negative-Literals_clause_ratio_maximum
POSNEG-RATIO-CLAUSE-entropy,base,Postive-Negative-Literals_clause_ratio_entropy
VCG-CLAUSE-mean,base,Variable-Clause-Graph_clause_mean
VCG-CLAUSE-coeff-variation,base,Variable-Clause-Graph_clause_coefficient_of_variation
VCG-CLAUSE-min,base,Variable-Clause-Graph_clause_min
VCG-CLAUSE-max,base,Variable-Clause-Graph_clause_max
VCG-CLAUSE-entropy,base,Variable-Clause-Graph_clause_entropy
UNARY,base,unary
BINARY+,base,binary
TRINARY+,base,trinary
Basic-featuretime,base,feature_time
VCG-VAR-mean,base,Variable-Clause-Graph_variable_mean
VCG-VAR-coeff-variation,base,Variable-Clause-Graph_variable_coefficient_of_variation
VCG-VAR-min,base,Variable-Clause-Graph_variable_min
VCG-VAR-max,base,Variable-Clause-Graph_variable_max
VCG-VAR-entropy,base,Variable-Clause-Graph_variable_entropy
POSNEG-RATIO-VAR-mean,base,Postive-Negative-Literals_variable_mean
POSNEG-RATIO-VAR-stdev,base,Postive-Negative-Literals_variable_standard_deviation
POSNEG-RATIO-VAR-min,base,Postive-Negative-Literals_variable_min
POSNEG-RATIO-VAR-max,base,Postive-Negative-Literals_variable_max
POSNEG-RATIO-VAR-entropy,base,Postive-Negative-Literals_variable_entropy
HORNY-VAR-mean,base,Horn-Formula_variable_mean
HORNY-VAR-coeff-variation,base,Horn-Formula_variable_coefficient_of_variation
HORNY-VAR-min,base,Horn-Formula_variable_min
HORNY-VAR-max,base,Horn-Formula_variable_max
HORNY-VAR-entropy,base,Horn-Formula_variable_entropy
horn-clauses-fraction,base,Horn-Formula_clauses_fraction
VG-mean,base,Variable-Graph_variable_mean
VG-coeff-variation,base,Variable-Graph_variable_coefficient_of_variation
VG-min,base,Variable-Graph_variable_min
VG-max,base,Variable-Graph_variable_max
KLB-featuretime,base,Kevin-Leyton-Brown_feature_time
CG-mean,base,Clause-Graph_clause_mean
CG-coeff-variation,base,Clause-Graph_clause_coefficient_of_variation
CG-min,base,Clause-Graph_clause_min
CG-max,base,Clause-Graph_clause_max
CG-entropy,base,Clause-Graph_clause_entropy
cluster-coeff-mean,base,Clause-Graph_cluster_coefficient_mean
cluster-coeff-coeff-variation,base,Clause-Graph_cluster_coefficient_of_variation
cluster-coeff-min,base,Clause-Graph_cluster_coefficient_min
cluster-coeff-max,base,Clause-Graph_cluster_coefficient_max
cluster-coeff-entropy,base,Clause-Graph_cluster_coefficient_entropy
CG-featuretime,base,Clause-Graph_feature_time
SP-bias-mean,sp,bias_mean
SP-bias-coeff-variation,sp,bias_coefficient_of_variation
SP-bias-min,sp,bias_min
SP-bias-max,sp,bias_max
SP-bias-q90,sp,bias_q90
SP-bias-q10,sp,bias_q10
SP-bias-q75,sp,bias_q75
SP-bias-q25,sp,bias_q25
SP-bias-q50,sp,bias_q50
SP-unconstraint-mean,sp,unconstraint_mean
SP-unconstraint-coeff-variation,sp,unconstraint_coefficient_of_variation
SP-unconstraint-min,sp,unconstraint_min
SP-unconstraint-max,sp,unconstraint_max
SP-unconstraint-q90,sp,unconstraint_q90
SP-unconstraint-q10,sp,unconstraint_q10
SP-unconstraint-q75,sp,unconstraint_q75
SP-unconstraint-q25,sp,unconstraint_q25
SP-unconstraint-q50,sp,unconstraint_q50
sp-featuretime,sp,feature_time
DIAMETER-mean,dia,mean
DIAMETER-coeff-variation,dia,coefficient_of_variation
DIAMETER-min,dia,min
DIAMETER-max,dia,max
DIAMETER-entropy,dia,entropy
DIAMETER-featuretime,dia,feature_time
cl-num-mean,cl,num_mean
cl-num-coeff-variation,cl,num_coefficient_of_variation
cl-num-min,cl,num_min
cl-num-max,cl,num_max
cl-num-q90,cl,num_q90
cl-num-q10,cl,num_q10
cl-num-q75,cl,num_q75
cl-num-q25,cl,num_q25
cl-num-q50,cl,num_q50
cl-size-mean,cl,size_mean
cl-size-coeff-variation,cl,size_coefficient_of_variation
cl-size-min,cl,size_min
cl-size-max,cl,size_max
cl-size-q90,cl,size_q90
cl-size-q10,cl,size_q10
cl-size-q75,cl,size_q75
cl-size-q25,cl,size_q25
cl-size-q50,cl,size_q50
cl-featuretime,cl,feature_time
vars-reduced-depth-1,unit,vars-reduced-depth-1
vars-reduced-depth-4,unit,vars-reduced-depth-4
vars-reduced-depth-16,unit,vars-reduced-depth-16
vars-reduced-depth-64,unit,vars-reduced-depth-64
vars-reduced-depth-256,unit,vars-reduced-depth-256
unit-featuretime,unit,feature_time
saps_BestSolution_Mean,ls,saps_BestSolution_Mean
saps_BestSolution_CoeffVariance,ls,saps_BestSolution_CoeffVariance
saps_FirstLocalMinStep_Mean,ls,saps_FirstLocalMinStep_Mean
saps_FirstLocalMinStep_CoeffVariance,ls,saps_FirstLocalMinStep_CoeffVariance
saps_FirstLocalMinStep_Median,ls,saps_FirstLocalMinStep_Median
saps_FirstLocalMinStep_Q.10,ls,saps_FirstLocalMinStep_Q.10
saps_FirstLocalMinStep_Q.90,ls,saps_FirstLocalMinStep_Q.90
saps_BestAvgImprovement_Mean,ls,saps_BestAvgImprovement_Mean
saps_BestAvgImprovement_CoeffVariance,ls,saps_BestAvgImprovement_CoeffVariance
saps_FirstLocalMinRatio_Mean,ls,saps_FirstLocalMinRatio_Mean
saps_FirstLocalMinRatio_CoeffVariance,ls,saps_FirstLocalMinRatio_CoeffVariance
ls-saps-featuretime,ls,ls-saps-featuretime
gsat_BestSolution_Mean,ls,gsat_BestSolution_Mean
gsat_BestSolution_CoeffVariance,ls,gsat_BestSolution_CoeffVariance
gsat_FirstLocalMinStep_Mean,ls,gsat_FirstLocalMinStep_Mean
gsat_FirstLocalMinStep_CoeffVariance,ls,gsat_FirstLocalMinStep_CoeffVariance
gsat_FirstLocalMinStep_Median,ls,gsat_FirstLocalMinStep_Median
gsat_FirstLocalMinStep_Q.10,ls,gsat_FirstLocalMinStep_Q.10
gsat_FirstLocalMinStep_Q.90,ls,gsat_FirstLocalMinStep_Q.90
gsat_BestAvgImprovement_Mean,ls,gsat_BestAvgImprovement_Mean
gsat_BestAvgImprovement_CoeffVariance,ls,gsat_BestAvgImprovement_CoeffVariance
gsat_FirstLocalMinRatio_Mean,ls,gsat_FirstLocalMinRatio_Mean
gsat_FirstLocalMinRatio_CoeffVariance,ls,gsat_FirstLocalMinRatio_CoeffVariance
ls-gsat-featuretime,ls,ls-gsat-featuretime
lobjois-mean-depth-over-vars,lobjois,lobjois-mean-depth-over-vars
lobjois-log-num-nodes-over-vars,lobjois,lobjois-log-num-nodes-over-vars
lobjois-featuretime,lobjois,feature_time
LP_OBJ,lp,LP_OBJ
LPSLack-mean,lp,lpslack-mean
LPSLack-coeff-variation,lp,lpslack-coeff-variation
LPSLack-min,lp,lpslack-min
LPSLack-max,lp,lpslack-max
lpIntRatio,lp,lpIntRatio
lpTIME,lp,feature_time
EOF
)

# ---------- build associative array ----------
declare -A FEATURE_MAP_DICT
while IFS=',' read -r key group name; do
  key="${key//$'\r'/}"   # strip carriage returns
  name="${name//$'\r'/}"
  FEATURE_MAP_DICT["$key"]="$group|$name"
done <<< "$FEATURE_MAP"

# ---------- -features mode: print Python-style list of tuples ----------
if [[ "$FEATURES" == true ]]; then
  RESULT="["
  for k in $(printf "%s\n" "${!FEATURE_MAP_DICT[@]}" | sort); do
    v="${FEATURE_MAP_DICT[$k]}"
    GROUP="${v%%|*}"
    NAME="${v##*|}"
    RESULT+="('$GROUP', '$NAME'), "
  done
  RESULT="${RESULT%, }]"  # remove trailing comma + space
  printf "%s\n" "$RESULT"
  exit 0
fi

# ---------- sanity checks ----------
[[ -z "$EXTRACTOR_DIR" || -z "$INSTANCE_FILE" ]] && {
  echo "Missing required arguments" >&2
  exit 1
}

EXE="$EXTRACTOR_DIR/features"

# ---------- build command string ----------
CMD="$EXE"

if [[ -n "$FEATURE_GROUP" ]]; then
  CMD+=" -$FEATURE_GROUP"
else
  CMD+=" -all"
fi

CMD+=" \"$INSTANCE_FILE\""

# ---------- run extractor ----------
OUTPUT=$(eval "$CMD" 2>&1) || {
  echo "$OUTPUT"
  exit 1
}

# ---------- parse output ----------
LINES=$(printf "%s\n" "$OUTPUT" | tail -n 2)

FEATURE_LINE=$(printf "%s\n" "$LINES" | head -n 1)
VALUE_LINE=$(printf "%s\n" "$LINES" | tail -n 1)

IFS=',' read -r -a FEATURES <<< "$FEATURE_LINE"
IFS=',' read -r -a VALUES <<< "$VALUE_LINE"

# Remove "solved" if present
LAST_INDEX=$((${#FEATURES[@]} - 1))
if [[ "${FEATURES[$LAST_INDEX]//$'\r'/}" == "solved" ]]; then
  unset 'FEATURES[$LAST_INDEX]'
  unset 'VALUES[$LAST_INDEX]'
fi

# ---------- build RESULT ----------
RESULT="["
for i in "${!FEATURES[@]}"; do
  FEATURE="${FEATURES[$i]//$'\r'/}"  # strip \r
  VALUE="${VALUES[$i]//$'\r'/}"
  MAP_VALUE="${FEATURE_MAP_DICT[$FEATURE]}"
  [[ -z "$MAP_VALUE" ]] && continue
  GROUP="${MAP_VALUE%%|*}"
  NAME="${MAP_VALUE##*|}"
  RESULT+="('$GROUP', '$NAME', '$VALUE'), "
done
RESULT="${RESULT%, }]"  # remove trailing comma + space

# ---------- output ----------
if [[ -n "$OUTPUT_FILE" ]]; then
  printf "%s\n" "$RESULT" > "$OUTPUT_FILE"
else
  printf "%s\n" "$RESULT"
fi
