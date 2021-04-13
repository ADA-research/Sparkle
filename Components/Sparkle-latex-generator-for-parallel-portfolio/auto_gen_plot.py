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
	fout.write('set title \'parallel vs sequential\''  + '\n')
	fout.write('set boxwidth 0.5' + '\n')
	fout.write('set key outside right' + '\n')
	fout.write('set xtics rotate by 45 right' + '\n')
	fout.write('set style fill solid' + '\n')
	fout.write('set yrange [0:]' + '\n')
	fout.write('set ylabel "wallclock time (s)" ' + '\n')
	fout.write('set terminal postscript eps color solid linewidth \"Helvetica\" 20'  + '\n')
	fout.write('set output \'%s\'' % (output_eps_file)  + '\n')
	fout.write('set linetype 1 lc rgb "red"' + '\n')
	fout.write('set linetype 2 lc rgb "blue"' + '\n')
	fout.write('set linetype 3 lc rgb "blue"' + '\n')
	fout.write('plot \'%s\'' % (data_best_solvers_vs_average_solver_order_filename)  + ' using 1:3:($1+1):xtic(2) with boxes title "parallel" linecolor variable, NaN ls 2 with boxes title "sequential" \n')
	fout.close()
	
	cmd = "gnuplot \'%s\'" % (output_gnuplot_script)
	os.system(cmd)
	
	cmd = "epstopdf \'%s\'" % (output_eps_file)
	os.system(cmd)
	
	os.system('rm -f \'%s\'' % (output_gnuplot_script))