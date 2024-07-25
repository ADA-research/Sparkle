#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Extractor wrapper for SAT2012."""
import sys
import argparse
from enum import Enum
import subprocess
from sparkle.types import FeatureGroup, FeatureSubgroup, FeatureType
from pathlib import Path

parser = argparse.ArgumentParser(description="Handle I/O for the extractor.")
parser.add_argument("-features", action="store_true")
parser.add_argument("-extractor_dir", type=str, help="Path to the extractor directory")
parser.add_argument("-instance_file", type=str, help="Path to the instance file")
parser.add_argument("-output_file", type=str, help="Path to the output file")
args = parser.parse_args()

feature_mapping = {
    "nvarsOrig": (FeatureGroup.BASE, FeatureType.NUMBER_OF_VARS_ORIGINAL),
    "nclausesOrig": (FeatureGroup.BASE, FeatureType.NUMBER_OF_CLAUSES_ORIGINAL),
    "nvars": (FeatureGroup.BASE, FeatureType.NUMBER_OF_VARS),
    "nclauses": (FeatureGroup.BASE, FeatureType.NUMBER_OF_CLAUSES),
    "reducedVars": (FeatureGroup.BASE, FeatureType.REDUCED_VARS),
    "reducedClauses": (FeatureGroup.BASE, FeatureType.REDUCED_CLAUSES),
    "Pre-featuretime": (FeatureGroup.BASE, FeatureType.PRE_FEATURE_TIME),
    "vars-clauses-ratio": (FeatureGroup.BASE, FeatureType.VARS_CLAUSES_RATIO),
    "POSNEG-RATIO-CLAUSE-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.POSNEG, FeatureType.CLAUSE_RATIO_MEAN)),
    "POSNEG-RATIO-CLAUSE-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.POSNEG, FeatureType.CLAUSE_COEFFICIENT_VARIATION)),
    "POSNEG-RATIO-CLAUSE-min": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.POSNEG, FeatureType.CLAUSE_RATIO_MINIMUM)),
    "POSNEG-RATIO-CLAUSE-max": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.POSNEG, FeatureType.CLAUSE_RATIO_MAXIMUM)),
    "POSNEG-RATIO-CLAUSE-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.POSNEG, FeatureType.CLAUSE_RATIO_ENTROPY)),
    "VCG-CLAUSE-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VCG, FeatureType.CLAUSE_MEAN)),
    "VCG-CLAUSE-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VCG, FeatureType.CLAUSE_COEFFICIENT_VARIATION)),
    "VCG-CLAUSE-min": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VCG, FeatureType.CLAUSE_MIN)),
    "VCG-CLAUSE-max": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VCG, FeatureType.CLAUSE_MAX)),
    "VCG-CLAUSE-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VCG, FeatureType.CLAUSE_ENTROPY)),
    "UNARY": (FeatureGroup.BASE, FeatureType.UNARY),
    "BINARY+": (FeatureGroup.BASE, FeatureType.BINARY),
    "TRINARY+": (FeatureGroup.BASE, FeatureType.TRINARY),
    "Basic-featuretime": (FeatureGroup.BASE, FeatureType.FEATURE_TIME),
    "VCG-VAR-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VCG, FeatureType.VAR_MEAN)),
    "VCG-VAR-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VCG, FeatureType.VAR_COEFFICIENT_VARIATION)),
    "VCG-VAR-min": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VCG, FeatureType.VAR_MIN)),
    "VCG-VAR-max": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VCG, FeatureType.VAR_MAX)),
    "VCG-VAR-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VCG, FeatureType.VAR_ENTROPY)),
    "POSNEG-RATIO-VAR-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.POSNEG, FeatureType.VAR_MEAN)),
    "POSNEG-RATIO-VAR-stdev": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.POSNEG, FeatureType.VAR_STD)),
    "POSNEG-RATIO-VAR-min": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.POSNEG, FeatureType.VAR_MIN)),
    "POSNEG-RATIO-VAR-max": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.POSNEG, FeatureType.VAR_MAX)),
    "POSNEG-RATIO-VAR-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.POSNEG, FeatureType.VAR_ENTROPY)),
    "HORNY-VAR-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.HORNY, FeatureType.VAR_MEAN)),
    "HORNY-VAR-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.HORNY, FeatureType.VAR_COEFFICIENT_VARIATION)),
    "HORNY-VAR-min": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.HORNY, FeatureType.VAR_MIN)),
    "HORNY-VAR-max": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.HORNY, FeatureType.VAR_MAX)),
    "HORNY-VAR-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.HORNY, FeatureType.VAR_ENTROPY)),
    "horn-clauses-fraction": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.HORNY, FeatureType.CLAUSE_FRACTION)),
    "VG-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VG, FeatureType.VAR_MEAN)),
    "VG-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VG, FeatureType.VAR_COEFFICIENT_VARIATION)),
    "VG-min": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VG, FeatureType.VAR_MIN)),
    "VG-max": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.VG, FeatureType.VAR_MAX)),
    "KLB-featuretime": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.KLB, FeatureType.FEATURE_TIME)),
    "CG-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.CG, FeatureType.CLAUSE_MEAN)),
    "CG-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.CG, FeatureType.CLAUSE_COEFFICIENT_VARIATION)),
    "CG-min": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.CG, FeatureType.CLAUSE_MIN)),
    "CG-max": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.CG, FeatureType.CLAUSE_MAX)),
    "CG-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.CG, FeatureType.CLAUSE_ENTROPY)),
    "cluster-coeff-mean": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.CG, FeatureType.CLUSTER_COEFFICIENT_MEAN)),
    "cluster-coeff-coeff-variation": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.CG, FeatureType.CLUSTER_COEFFICIENT_VARIATION)),
    "cluster-coeff-min": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.CG, FeatureType.CLUSTER_COEFFICIENT_MIN)),
    "cluster-coeff-max": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.CG, FeatureType.CLUSTER_COEFFICIENT_MAX)),
    "cluster-coeff-entropy": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.CG, FeatureType.CLUSTER_COEFFICIENT_ENTROPY)),
    "CG-featuretime": (FeatureGroup.BASE, FeatureType.with_subgroup(
        FeatureSubgroup.CG, FeatureType.FEATURE_TIME))}


if args.features:
    # Print the stringified features and the group they belong to
    print([(feature_mapping[key][0].value, feature_mapping[key][1].value
           if isinstance(feature_mapping[key][1], Enum) else feature_mapping[key][1])
           for key in feature_mapping.keys()])
    sys.exit()

extractor_dir = Path(args.extractor_dir)
instance_path = Path(args.instance_file)
output_file = Path(args.output_file) if args.output_file else None

extractor_name = "SATFeatureCompetition2012"
executable_name = "features"
executable = extractor_dir / executable_name

extractor = subprocess.run([extractor_dir / executable_name, instance_path],
                           capture_output=True)

# Read all lines from the input file
raw_lines = extractor.stdout.decode().splitlines()

# Process raw result file and write to the final result file
# First, we need to map each feature_name to its standardised name
if len(raw_lines) >= 2:
    features = raw_lines[-2].strip().split(",")
    values = raw_lines[-1].strip().split(",")
    processed_features = []
    for i, feature in enumerate(features):
        feature_group, feature_name = feature_mapping[feature]
        if isinstance(feature_name, Enum):
            feature_name = feature_name.value
        processed_features.append([feature_group.value, feature_name, values[i]])
else:
    # Failed to compute features
    sys.exit(extractor.stdout.decode())

if output_file is not None:
    with open(output_file, "w") as out_file:
        out_file.write(str(processed_features))
else:
    print(processed_features)
