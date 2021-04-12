#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import fcntl

if __name__ == r'__main__':
	print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	if len(sys.argv)!=3:
		print('Usage: %s <data_best_solvers_vs_average_solver> <figure_best_solvers_vs_average_solver>' % (sys.argv[0]))
		exit(-1)
	
	data_best_solvers_vs_average_solver_order_filename = sys.argv[1]
	figure_best_solvers_vs_average_solver_order_filename = sys.argv[2]
	
	output_eps_file = figure_best_solvers_vs_average_solver_order_filename + r'.eps'
	output_pdf_file = figure_best_solvers_vs_average_solver_order_filename + r'.pdf'
	
	output_gnuplot_script = 'figure_best_solvers_vs_average_solver.plt'
	# So far so good
	fout = open(output_gnuplot_script, 'w+')
	# fout.write('set title \'parallel vs sequential\''  + '\n')
	# fout.write('set boxwidth 0.5' + '\n')
	# fout.write('set style fill solid' + '\n')
	# fout.write('set terminal postscript eps color solid linewidth \"Helvetica\" 20'  + '\n')
	fout.write('set output \'%s\'' % (output_eps_file)  + '\n')
	fout.write('plot \'%s\'' % (data_best_solvers_vs_average_solver_order_filename)  + 'using 1:2:xtic(1) with boxes \n')
	fout.close()
	
	cmd = "gnuplot \'%s\'" % (output_gnuplot_script)
	os.system(cmd)
	
	cmd = "epstopdf \'%s\'" % (output_eps_file)
	os.system(cmd)
	
	os.system('rm -f \'%s\'' % (output_gnuplot_script))