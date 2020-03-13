#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import fcntl

if __name__ == r'__main__':
	
	if len(sys.argv)!=6:
		print('Usage: %s <data_solver_configured_vs_default_filename> <penalty_time> <default_name> <configured_name> <figure_solver_configured_vs_default_filename>' % (sys.argv[0]))
		exit(-1)
	
	data_solver_configured_vs_default_filename = sys.argv[1]
	penalty_time = sys.argv[2]
	upper_bound = float(penalty_time)*1.5
	lower_bound = 0.01
	default_name = sys.argv[3]
	configured_name = sys.argv[4]
	figure_solver_configured_vs_default_filename = sys.argv[5]
	
	output_eps_file = figure_solver_configured_vs_default_filename + r'.eps'
	output_pdf_file = figure_solver_configured_vs_default_filename + r'.pdf'
	
	default_name = default_name.replace(r'/', r'_')
	output_gnuplot_script = configured_name + r'_vs_' + default_name + r'.plt'
	
	fout = open(output_gnuplot_script, 'w+')
	fout.write('set xlabel \'PAR10 (default)\'\n')
	fout.write('set ylabel \'PAR10 (configured)\'\n')
	fout.write('unset key'  + '\n')
	fout.write('set xrange [%s:%s]' % (lower_bound, upper_bound) + '\n')
	fout.write('set yrange [%s:%s]' % (lower_bound, upper_bound)  + '\n')
	fout.write('set logscale x'  + '\n')
	fout.write('set logscale y'  + '\n')
	fout.write('set grid'  + '\n')
	fout.write('set size square'  + '\n')
	fout.write('set arrow from %s,%s to %s,%s nohead lc rgb \'black\'' % (lower_bound, lower_bound, upper_bound, upper_bound)  + '\n')
	# Cutoff time x axis
	fout.write('set arrow from %s,%s to %s,%s nohead lc rgb \'black\' lt 2' % (penalty_time, lower_bound, penalty_time, upper_bound)  + '\n')
	# Cutoff time y axis
	fout.write('set arrow from %s,%s to %s,%s nohead lc rgb \'black\' lt 2' % (lower_bound, penalty_time, upper_bound, penalty_time)  + '\n')
	fout.write('set terminal postscript eps color dashed linewidth \"Helvetica\" 20'  + '\n')
	fout.write('set output \'%s\'' % (output_eps_file)  + '\n')
	fout.write('plot \'%s\' with points pt 2 ps 2' % (data_solver_configured_vs_default_filename)  + '\n')
	fout.close()
	
	cmd = "gnuplot \'%s\'" % (output_gnuplot_script)
	os.system(cmd)
	
	cmd = "epstopdf \'%s\'" % (output_eps_file)
	os.system(cmd)
	
	os.system('rm -f \'%s\'' % (output_gnuplot_script))
	
