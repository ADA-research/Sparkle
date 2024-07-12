#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Extractor wrapper for SAT2024."""
import sys
import argparse
from enum import Enum
import subprocess
from sparkle.types import FeatureGroup, FeatureSubgroup, FeatureType
from pathlib import Path

feature_mapping = {
    "nvarsOrig": (FeatureGroup.BASE, FeatureType.NUMBER_OF_VARS_ORIGINAL),
    "nclausesOrig": (FeatureGroup.BASE, FeatureType.NUMBER_OF_CLAUSES_ORIGINAL),
    "nvars": (FeatureGroup.BASE, FeatureType.NUMBER_OF_VARS),
    "nclauses": (FeatureGroup.BASE, FeatureType.NUMBER_OF_CLAUSES),
    "reducedVars": (FeatureGroup.BASE, FeatureType.REDUCED_VARS),
    "reducedClauses": (FeatureGroup.BASE, FeatureType.REDUCED_CLAUSES),
    "Pre-featuretime": (FeatureGroup.BASE, FeatureType.PRE_FEATURE_TIME),
    "vars-clauses-ratio": (FeatureGroup.BASE, FeatureType.VARS_CLAUSES_RATIO),
    "POSNEG-RATIO-CLAUSE-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.POSNEG, FeatureType.CLAUSE_RATIO_MEAN)),
    "POSNEG-RATIO-CLAUSE-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.POSNEG, FeatureType.CLAUSE_COEFFICIENT_VARIATION)),
    "POSNEG-RATIO-CLAUSE-min": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.POSNEG, FeatureType.CLAUSE_RATIO_MINIMUM)),
    "POSNEG-RATIO-CLAUSE-max": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.POSNEG, FeatureType.CLAUSE_RATIO_MAXIMUM)),
    "POSNEG-RATIO-CLAUSE-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.POSNEG, FeatureType.CLAUSE_RATIO_ENTROPY)),
    "VCG-CLAUSE-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VCG, FeatureType.CLAUSE_MEAN)),
    "VCG-CLAUSE-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VCG, FeatureType.CLAUSE_COEFFICIENT_VARIATION)),
    "VCG-CLAUSE-min": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VCG, FeatureType.CLAUSE_MIN)),
    "VCG-CLAUSE-max": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VCG, FeatureType.CLAUSE_MAX)),
    "VCG-CLAUSE-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VCG, FeatureType.CLAUSE_ENTROPY)),
    "UNARY": (FeatureGroup.BASE, FeatureType.UNARY),
    "BINARY+": (FeatureGroup.BASE, FeatureType.BINARY),
    "TRINARY+": (FeatureGroup.BASE, FeatureType.TRINARY),
    "Basic-featuretime": (FeatureGroup.BASE, FeatureType.FEATURE_TIME),
    "VCG-VAR-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VCG, FeatureType.VAR_MEAN)),
    "VCG-VAR-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VCG, FeatureType.VAR_COEFFICIENT_VARIATION)),
    "VCG-VAR-min": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VCG, FeatureType.VAR_MIN)),
    "VCG-VAR-max": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VCG, FeatureType.VAR_MAX)),
    "VCG-VAR-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VCG, FeatureType.VAR_ENTROPY)),
    "POSNEG-RATIO-VAR-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.POSNEG, FeatureType.VAR_MEAN)),
    "POSNEG-RATIO-VAR-stdev": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.POSNEG, FeatureType.VAR_STD)),
    "POSNEG-RATIO-VAR-min": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.POSNEG, FeatureType.VAR_MIN)),
    "POSNEG-RATIO-VAR-max": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.POSNEG, FeatureType.VAR_MAX)),
    "POSNEG-RATIO-VAR-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.POSNEG, FeatureType.VAR_ENTROPY)),
    "HORNY-VAR-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.HORNY, FeatureType.VAR_MEAN)),
    "HORNY-VAR-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.HORNY, FeatureType.VAR_COEFFICIENT_VARIATION)),
    "HORNY-VAR-min": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.HORNY, FeatureType.VAR_MIN)),
    "HORNY-VAR-max": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.HORNY, FeatureType.VAR_MAX)),
    "HORNY-VAR-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.HORNY, FeatureType.VAR_ENTROPY)),
    "horn-clauses-fraction": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.HORNY, FeatureType.CLAUSE_FRACTION)),
    "VG-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VG, FeatureType.VAR_MEAN)),
    "VG-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VG, FeatureType.VAR_COEFFICIENT_VARIATION)),
    "VG-min": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VG, FeatureType.VAR_MIN)),
    "VG-max": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.VG, FeatureType.VAR_MAX)),
    "KLB-featuretime": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.KLB, FeatureType.FEATURE_TIME)),
    "CG-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.CG, FeatureType.CLAUSE_MEAN)),
    "CG-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.CG, FeatureType.CLAUSE_COEFFICIENT_VARIATION)),
    "CG-min": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.CG, FeatureType.CLAUSE_MIN)),
    "CG-max": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.CG, FeatureType.CLAUSE_MAX)),
    "CG-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.CG, FeatureType.CLAUSE_ENTROPY)),
    "cluster-coeff-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.CG, FeatureType.CLUSTER_COEFFICIENT_MEAN)),
    "cluster-coeff-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.CG, FeatureType.CLUSTER_COEFFICIENT_VARIATION)),
    "cluster-coeff-min": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.CG, FeatureType.CLUSTER_COEFFICIENT_MIN)),
    "cluster-coeff-max": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.CG, FeatureType.CLUSTER_COEFFICIENT_MAX)),
    "cluster-coeff-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.CG, FeatureType.CLUSTER_COEFFICIENT_ENTROPY)),
    "CG-featuretime": (FeatureGroup.BASE, FeatureType.with_subgroup(FeatureSubgroup.CG, FeatureType.FEATURE_TIME)),
    "SP-bias-mean": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.BIAS, FeatureType.MEAN)),
    "SP-bias-coeff-variation": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.BIAS, FeatureType.COEFFICIENT_VARIATION)),
    "SP-bias-min": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.BIAS, FeatureType.MIN)),
    "SP-bias-max": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.BIAS, FeatureType.MAX)),
    "SP-bias-q90": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.BIAS, FeatureType.QUANTILE_90)),
    "SP-bias-q10": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.BIAS, FeatureType.QUANTILE_10)),
    "SP-bias-q75": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.BIAS, FeatureType.QUANTILE_75)),
    "SP-bias-q25": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.BIAS, FeatureType.QUANTILE_25)),
    "SP-bias-q50": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.BIAS, FeatureType.QUANTILE_50)),
    "SP-unconstraint-mean": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.UNCONSTRAINT, FeatureType.MEAN)),
    "SP-unconstraint-coeff-variation": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.UNCONSTRAINT, FeatureType.COEFFICIENT_VARIATION)),
    "SP-unconstraint-min": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.UNCONSTRAINT, FeatureType.MIN)),
    "SP-unconstraint-max": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.UNCONSTRAINT, FeatureType.MAX)),
    "SP-unconstraint-q90": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.UNCONSTRAINT, FeatureType.QUANTILE_90)),
    "SP-unconstraint-q10": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.UNCONSTRAINT, FeatureType.QUANTILE_10)),
    "SP-unconstraint-q75": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.UNCONSTRAINT, FeatureType.QUANTILE_75)),
    "SP-unconstraint-q25": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.UNCONSTRAINT, FeatureType.QUANTILE_25)),
    "SP-unconstraint-q50": (FeatureGroup.SP, FeatureType.with_subgroup(FeatureSubgroup.UNCONSTRAINT, FeatureType.QUANTILE_50)),
    "sp-featuretime": (FeatureGroup.SP, FeatureType.FEATURE_TIME),
    "DIAMETER-mean": (FeatureGroup.DIAMETER, FeatureType.MEAN),
    "DIAMETER-coeff-variation": (FeatureGroup.DIAMETER, FeatureType.COEFFICIENT_VARIATION),
    "DIAMETER-min": (FeatureGroup.DIAMETER, FeatureType.MIN),
    "DIAMETER-max": (FeatureGroup.DIAMETER, FeatureType.MAX),
    "DIAMETER-entropy": (FeatureGroup.DIAMETER, FeatureType.ENTROPY),
    "DIAMETER-featuretime": (FeatureGroup.DIAMETER, FeatureType.FEATURE_TIME),
    "cl-num-mean": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.NUM, FeatureType.MEAN)),
    "cl-num-coeff-variation": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.NUM, FeatureType.COEFFICIENT_VARIATION)),
    "cl-num-min": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.NUM, FeatureType.MIN)),
    "cl-num-max": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.NUM, FeatureType.MAX)),
    "cl-num-q90": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.NUM, FeatureType.QUANTILE_90)),
    "cl-num-q10": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.NUM, FeatureType.QUANTILE_10)),
    "cl-num-q75": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.NUM, FeatureType.QUANTILE_75)),
    "cl-num-q25": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.NUM, FeatureType.QUANTILE_25)),
    "cl-num-q50": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.NUM, FeatureType.QUANTILE_50)),
    "cl-size-mean": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.SIZE, FeatureType.MEAN)),
    "cl-size-coeff-variation": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.SIZE, FeatureType.COEFFICIENT_VARIATION)),
    "cl-size-min": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.SIZE, FeatureType.MIN)),
    "cl-size-max": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.SIZE, FeatureType.MAX)),
    "cl-size-q90": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.SIZE, FeatureType.QUANTILE_90)),
    "cl-size-q10": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.SIZE, FeatureType.QUANTILE_10)),
    "cl-size-q75": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.SIZE, FeatureType.QUANTILE_75)),
    "cl-size-q25": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.SIZE, FeatureType.QUANTILE_25)),
    "cl-size-q50": (FeatureGroup.CL, FeatureType.with_subgroup(FeatureSubgroup.SIZE, FeatureType.QUANTILE_50)),
    "cl-featuretime": (FeatureGroup.CL, FeatureType.FEATURE_TIME),
    "vars-reduced-depth-1": (FeatureGroup.UNIT, "vars-reduced-depth-1"),
    "vars-reduced-depth-4": (FeatureGroup.UNIT, "vars-reduced-depth-4"),
    "vars-reduced-depth-16": (FeatureGroup.UNIT, "vars-reduced-depth-16"),
    "vars-reduced-depth-64": (FeatureGroup.UNIT, "vars-reduced-depth-64"),
    "vars-reduced-depth-256": (FeatureGroup.UNIT, "vars-reduced-depth-256"),
    "unit-featuretime": (FeatureGroup.UNIT, FeatureType.FEATURE_TIME),
    "saps_BestSolution_Mean": (FeatureGroup.LS, "saps_BestSolution_Mean"),
    "saps_BestSolution_CoeffVariance": (FeatureGroup.LS, "saps_BestSolution_CoeffVariance"),
    "saps_FirstLocalMinStep_Mean": (FeatureGroup.LS, "saps_FirstLocalMinStep_Mean"),
    "saps_FirstLocalMinStep_CoeffVariance": (FeatureGroup.LS, "saps_FirstLocalMinStep_CoeffVariance"),
    "saps_FirstLocalMinStep_Median": (FeatureGroup.LS, "saps_FirstLocalMinStep_Median"),
    "saps_FirstLocalMinStep_Q.10": (FeatureGroup.LS, "saps_FirstLocalMinStep_Q.10"),
    "saps_FirstLocalMinStep_Q.90": (FeatureGroup.LS, "saps_FirstLocalMinStep_Q.90"),
    "saps_BestAvgImprovement_Mean": (FeatureGroup.LS, "saps_BestAvgImprovement_Mean"),
    "saps_BestAvgImprovement_CoeffVariance": (FeatureGroup.LS, "saps_BestAvgImprovement_CoeffVariance"),
    "saps_FirstLocalMinRatio_Mean": (FeatureGroup.LS, "saps_FirstLocalMinRatio_Mean"),
    "saps_FirstLocalMinRatio_CoeffVariance": (FeatureGroup.LS, "saps_FirstLocalMinRatio_CoeffVariance"),
    "ls-saps-featuretime": (FeatureGroup.LS, "ls-saps-featuretime"),
    "gsat_BestSolution_Mean": (FeatureGroup.LS, "gsat_BestSolution_Mean"),
    "gsat_BestSolution_CoeffVariance": (FeatureGroup.LS, "gsat_BestSolution_CoeffVariance"),
    "gsat_FirstLocalMinStep_Mean": (FeatureGroup.LS, "gsat_FirstLocalMinStep_Mean"),
    "gsat_FirstLocalMinStep_CoeffVariance": (FeatureGroup.LS, "gsat_FirstLocalMinStep_CoeffVariance"),
    "gsat_FirstLocalMinStep_Median": (FeatureGroup.LS, "gsat_FirstLocalMinStep_Median"),
    "gsat_FirstLocalMinStep_Q.10": (FeatureGroup.LS, "gsat_FirstLocalMinStep_Q.10"),
    "gsat_FirstLocalMinStep_Q.90": (FeatureGroup.LS, "gsat_FirstLocalMinStep_Q.90"),
    "gsat_BestAvgImprovement_Mean": (FeatureGroup.LS, "gsat_BestAvgImprovement_Mean"),
    "gsat_BestAvgImprovement_CoeffVariance": (FeatureGroup.LS, "gsat_BestAvgImprovement_CoeffVariance"),
    "gsat_FirstLocalMinRatio_Mean": (FeatureGroup.LS, "gsat_FirstLocalMinRatio_Mean"),
    "gsat_FirstLocalMinRatio_CoeffVariance": (FeatureGroup.LS, "gsat_FirstLocalMinRatio_CoeffVariance"),
    "ls-gsat-featuretime": (FeatureGroup.LS, "ls-gsat-featuretime"),
    "lobjois-mean-depth-over-vars": (FeatureGroup.LOBJOIS, "lobjois-mean-depth-over-vars"),
    "lobjois-log-num-nodes-over-vars": (FeatureGroup.LOBJOIS, "lobjois-log-num-nodes-over-vars"),
    "lobjois-featuretime": (FeatureGroup.LOBJOIS, FeatureType.FEATURE_TIME),
    "LP_OBJ": (FeatureGroup.LP, "LP_OBJ"),
    "LPSLack-mean": (FeatureGroup.LP, "lpslack-mean"),
    "LPSLack-coeff-variation": (FeatureGroup.LP, "lpslack-coeff-variation"),
    "LPSLack-min": (FeatureGroup.LP, "lpslack-min"),
    "LPSLack-max": (FeatureGroup.LP, "lpslack-max"),
    "lpIntRatio": (FeatureGroup.LP, "lpIntRatio"),
    "lpTIME": (FeatureGroup.LP, FeatureType.FEATURE_TIME)
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handle I/O for the extractor.")
    parser.add_argument("-features",  action="store_true")
    parser.add_argument("-extractor_dir", type=str, help="Path to the extractor directory")
    parser.add_argument("-instance_file", type=str, help="Path to the instance file")
    parser.add_argument("-feature_group", type=str, help="The feature group to compute for this instance. If not present, all will be computed.")
    parser.add_argument("-output_file", type=str, help="Path to the output file")
    args = parser.parse_args()

    if args.features:
        # Print the stringified features and the group they belong to
        print([(feature_mapping[key][0].value, feature_mapping[key][1].value if isinstance(feature_mapping[key][1], Enum) else feature_mapping[key][1])
            for key in feature_mapping.keys()])
        sys.exit()

    extractor_dir = Path(args.extractor_dir)
    instance_path = Path(args.instance_file)
    output_file = Path(args.output_file) if args.output_file else None

    extractor_name = "SATFeatureCompetition2024"
    executable_name = "features"
    executable = extractor_dir / executable_name
    cmd = [extractor_dir / executable_name]
    #Feature group options: [-all] [-base] |[-sp] [-Dia] [-Cl] [-unit] [-ls] [-lp] [-lobjois] (lowercase)
    if args.feature_group is not None:
        cmd.append(f"-{args.feature_group}")
    else:
        cmd.append("-all")
    cmd.append(instance_path)

    extractor = subprocess.run(cmd, capture_output=True)

    # Read all lines from the input file
    raw_lines = extractor.stdout.decode().splitlines()

    # Process raw result file and write to the final result file
    # First, we need to map each feature_name to its standardised name
    if len(raw_lines) >= 2:
        features = raw_lines[-2].strip().split(",")
        values = raw_lines[-1].strip().split(",")
        # Remove the solved feature
        if features[-1] == "solved":
            features = features[:-1]
            values = values[:-1]
        processed_features = []
        for i, feature in enumerate(features):
            feature_group, feature_name = feature_mapping[feature]
            if isinstance(feature_name, Enum):
                feature_name = feature_name.value
            processed_features.append((feature_group.value, feature_name, values[i]))
            
    else:
        # Failed to compute features
        sys.exit(extractor.stdout.decode())

    if output_file is not None:
        with open(output_file, "w") as out_file:
            out_file.write(str(processed_features))
    else:
        print(processed_features)
