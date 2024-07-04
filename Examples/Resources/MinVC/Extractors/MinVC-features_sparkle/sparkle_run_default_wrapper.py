#!/usr/bin/env python3

import sys
from pathlib import Path


def get_last_level_directory_name(filepath):
	if filepath[-1] == r'/': filepath = filepath[0:-1]
	right_index = filepath.rfind(r'/')
	if right_index<0: pass
	else: filepath = filepath[right_index+1:]
	return filepath

class MinVCInstanceFeature:
    def __init__(self, relative_path, minvc_instance_file_name):
        self.relative_path = relative_path
        self.minvc_instance_file_name = minvc_instance_file_name
        self.num_vertex, self.num_edge = self._get_num_vertex_and_num_edge()
        self.density = 2*self.num_edge / (self.num_vertex*(self.num_vertex-1))
        self.map_adj_matrix = self._get_map_adj_matrix()
        self.max_degree, self.min_degree, self.avg_degree = self._get_degree_related_info()
        return
    
    def save_minvc_features(self, result_feature_file_name):
        extractor_directory_last_level = Path(self.relative_path).name
        
        list_feature_names = ['num_vertex', 'num_edge', 'density', 'max_degree', 'min_degree', 'avg_degree']
        list_feature_values = [self.num_vertex, self.num_edge, self.density, self.max_degree, self.min_degree, self.avg_degree]

        fout = open(result_feature_file_name, 'w+')
        for feature_name in list_feature_names:
            fout.write(',%s' % (feature_name + extractor_directory_last_level))
        fout.write('\n')

        fout.write('%s' % self.minvc_instance_file_name)
        for feature_value in list_feature_values:
            fout.write(',%s' % (str(feature_value)))
        fout.write('\n')

        fout.close()
        return

    def _get_num_vertex_and_num_edge(self):
        num_vertex = 0
        num_edge = 0
        fin = open(self.minvc_instance_file_name, 'r')
        while True:
            myline = fin.readline()
            if not myline: break
            mylist = myline.strip().split()
            if len(mylist) == 4 and mylist[0] == 'p' and mylist[1] == 'edge':
                num_vertex = int(mylist[2])
                num_edge = int(mylist[3])
                break
        fin.close()
        return num_vertex, num_edge
    
    def _get_map_adj_matrix(self):
        map_adj_matrix = {}
        fin = open(self.minvc_instance_file_name, 'r')
        while True:
            myline = fin.readline()
            if not myline: break
            mylist = myline.strip().split()
            if len(mylist) == 3 and mylist[0] == 'e':
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
        fin.close()
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



relative_path = sys.argv[1]
minvc_instance_file_name = sys.argv[2]
result_feature_file_name = sys.argv[3]

minvc_instance_feature = MinVCInstanceFeature(relative_path, minvc_instance_file_name)
minvc_instance_feature.save_minvc_features(result_feature_file_name)