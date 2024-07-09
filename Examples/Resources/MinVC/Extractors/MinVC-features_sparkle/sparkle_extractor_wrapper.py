#!/usr/bin/env python3
"""Extractor wrapper for MinVC."""
import argparse
import sys
from pathlib import Path
from sparkle.types import FeatureGroup


class MinVCInstanceFeature:
    feature_names = ["num_vertex", "num_edge", "density", "max_degree", "min_degree", "avg_degree"]

    def __init__(self, relative_path: Path, minvc_instance_file_name: Path):
        self.relative_path = relative_path
        self.minvc_instance_file_name = minvc_instance_file_name
        self.num_vertex, self.num_edge = self._get_num_vertex_and_num_edge()
        self.density = 2*self.num_edge / (self.num_vertex*(self.num_vertex-1))
        self.map_adj_matrix = self._get_map_adj_matrix()
        self.max_degree, self.min_degree, self.avg_degree = self._get_degree_related_info()

    def get_minvc_features(self):
        feature_values = [self.num_vertex, self.num_edge, self.density, self.max_degree, self.min_degree, self.avg_degree]
        return [(FeatureGroup.BASE.value, MinVCInstanceFeature.feature_names[i], value) for i, value in enumerate(feature_values)]

    def _get_num_vertex_and_num_edge(self):
        num_vertex = 0
        num_edge = 0
        for myline in self.minvc_instance_file_name.open().readlines():
            mylist = myline.strip().split()
            if len(mylist) == 4 and mylist[0] == "p" and mylist[1] == "edge":
                num_vertex = int(mylist[2])
                num_edge = int(mylist[3])
                break
        return num_vertex, num_edge
    
    def _get_map_adj_matrix(self):
        map_adj_matrix = {}
        for myline in self.minvc_instance_file_name.open().readlines():
            mylist = myline.strip().split()
            if len(mylist) == 3 and mylist[0] == "e":
                temp_v1 = int(mylist[1])
                temp_v2 = int(mylist[2])
                v1 = min(temp_v1, temp_v2)
                v2 = max(temp_v1, temp_v2)
                
                if map_adj_matrix.__contains__(v1):
                    map_adj_matrix[v1].append(v2)
                else:
                    map_adj_matrix[v1] = [v2, ]
                
                if map_adj_matrix.__contains__(v2):
                    map_adj_matrix[v2].append(v1)
                else:
                    map_adj_matrix[v2] = [v1, ]
        return map_adj_matrix
    
    def _get_degree_related_info(self):
        list_vertex_degree = []
        for key in self.map_adj_matrix.keys():
            tmp_degree = len(self.map_adj_matrix[key])
            list_vertex_degree.append(tmp_degree)
        
        max_degree = max(list_vertex_degree)
        min_degree = min(list_vertex_degree)
        avg_degree = sum(list_vertex_degree) / len(list_vertex_degree)
        return max_degree, min_degree, avg_degree

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("-features",  action="store_true", help="Only print features and their groups as a list of tuples.")
parser.add_argument("-extractor_dir", type=str, help="Path to the extractor directory")
parser.add_argument("-instance_file", type=str, help="Path to the instance file")
parser.add_argument("-output_file", type=str, help="Path to the output file")
args = parser.parse_args()

if args.features:
    # Return a list of feature names and their feature groups as [(feature_group, feature_name), ...]
    print([(FeatureGroup.BASE.value, name) for name in MinVCInstanceFeature.feature_names])
    sys.exit()

relative_path = Path(args.extractor_dir)
minvc_instance_file_name = Path(args.instance_file)

minvc = MinVCInstanceFeature(relative_path, minvc_instance_file_name)
features = minvc.get_minvc_features()

if args.output_file is not None:
    output_file = Path(args.output_file)
    output_file.open("w+").write(str(features))
else:
    print(features)