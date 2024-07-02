#!/usr/bin/env python3
from pathlib import Path
import argparse

global sparkle_special_string
sparkle_special_string = r"__@@SPARKLE@@__"

class CCAGInstanceFeature:
    def __init__(self, relative_path, ccag_model_file_path, ccag_constraint_file_path):
        self.relative_path = relative_path
        self.ccag_model_file_path = ccag_model_file_path
        self.ccag_constraint_file_path = ccag_constraint_file_path
        self.num_way, self.num_option, self.average_option_value = self._get_model_features()
        self.num_constraint, self.average_constraint_length = self._get_constraint_features()
        return

    def save_ccag_features(self, result_feature_file_name):
        list_feature_names = ["num_way", "num_option", "average_option_value", "num_constraint", "average_constraint_length"]
        list_feature_values = [self.num_way, self.num_option, self.average_option_value, self.num_constraint, self.average_constraint_length]

        fout = open(result_feature_file_name, "w+")
        for feature_name in list_feature_names:
            fout.write(",%s"% (feature_name + sparkle_special_string + self.relative_path.name))
        fout.write("\n")

        fout.write("%s %s"% (self.ccag_model_file_path, self.ccag_constraint_file_path))
        for feature_value in list_feature_values:
            fout.write(",%s"% (str(feature_value)))
        fout.write("\n")

        fout.close()
        return

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
parser.add_argument("-extractor_dir", type=str, help="Path to the extractor directory")
parser.add_argument("-instance_file", nargs="+", type=str, help="Paths to the instance files, grouped in order as [.model, .constraints]")
parser.add_argument("-output_file", type=str, help="Path to the output file")
args = parser.parse_args()

ccag_model_file_path = Path(args.instance_file[0])
ccag_constraint_file_path = Path(args.instance_file[1])

ccag_instance_feature = CCAGInstanceFeature(Path(args.extractor_dir), ccag_model_file_path, ccag_constraint_file_path)
ccag_instance_feature.save_ccag_features(args.output_file)