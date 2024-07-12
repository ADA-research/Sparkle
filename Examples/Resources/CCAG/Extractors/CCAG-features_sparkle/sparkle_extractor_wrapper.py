#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse
from sparkle.types import FeatureGroup


class CCAGInstanceFeature:
    feature_names = ["num_way", "num_option", "average_option_value", "num_constraint", "average_constraint_length"]

    def __init__(self, relative_path, ccag_model_file_path, ccag_constraint_file_path):
        self.relative_path = relative_path
        self.ccag_model_file_path = ccag_model_file_path
        self.ccag_constraint_file_path = ccag_constraint_file_path
        self.num_way, self.num_option, self.average_option_value = self._get_model_features()
        self.num_constraint, self.average_constraint_length = self._get_constraint_features()

    def get_ccag_features(self):
        feature_values = [self.num_way, self.num_option, self.average_option_value, self.num_constraint, self.average_constraint_length]
        return [(FeatureGroup.BASE.value, CCAGInstanceFeature.feature_names[i], str(value)) for i, value in enumerate(feature_values)]

    def _get_model_features(self):
        num_way = -1
        num_option = -1
        average_option_value = -1

        infile = open(self.ccag_model_file_path, "r")
        lines = infile.readlines()
        infile.close()

        if len(lines) <= 0:
            return num_way, num_option, average_option_value
        
        num_way = int(lines[0].strip())
        if len(lines) == 1:
            return num_way, num_option, average_option_value
        
        num_option = int(lines[1].strip())
        if len(lines) == 2:
            return num_way, num_option, average_option_value
        
        option_values = lines[2].strip().split()
        sum_option_values = 0
        for option_value in option_values:
            sum_option_values += int(option_value)
        average_option_value = sum_option_values / len(option_values)

        return num_way, num_option, average_option_value

    def _get_constraint_features(self):
        num_constraint = -1
        average_constraint_length = -1

        infile = open(self.ccag_constraint_file_path, "r")
        lines = infile.readlines()
        infile.close()

        if len(lines) <= 0:
            return num_constraint, average_constraint_length

        num_constraint = int(lines[0].strip())
        if len(lines) == 1:
            return num_constraint, average_constraint_length

        sum_constraint_length = 0
        for i in range(num_constraint):
            temp_constraint_length = int(lines[2*i+1].strip())
            sum_constraint_length += temp_constraint_length
        
        average_constraint_length = sum_constraint_length / num_constraint

        return num_constraint, average_constraint_length

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("-features",  action="store_true", help="Only print features and their groups as a list of tuples.")
parser.add_argument("-extractor_dir", type=str, help="Path to the extractor directory")
parser.add_argument("-instance_file", nargs="+", type=str, help="Paths to the instance files, grouped in order as [.model, .constraints]")
parser.add_argument("-output_file", type=str, help="Path to the output file")
args = parser.parse_args()

if args.features:
    # Return a list of feature names and their feature groups as [(feature_group, feature_name), ...]
    print([(FeatureGroup.BASE.value, name) for name in CCAGInstanceFeature.feature_names])
    sys.exit()

ccag_model_file_path = Path(args.instance_file[0])
ccag_constraint_file_path = Path(args.instance_file[1])
ccag = CCAGInstanceFeature(Path(args.extractor_dir), ccag_model_file_path, ccag_constraint_file_path)
features = ccag.get_ccag_features()
if args.output_file is not None:
    output_file = Path(args.output_file)
    output_file.open("w+").write(str(features))
else:
    print(features)