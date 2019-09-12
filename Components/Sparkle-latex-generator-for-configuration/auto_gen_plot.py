#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

import os
import sys
import fcntl

if __name__ == r'__main__':
	
	if len(sys.argv)!=6:
		print('Usage: %s <data_portfolio_selector_sparkle_vs_vbs_filename> <penalty_time> <vbs_name> <portfolio_selector_sparkle_name> <figure_portfolio_selector_sparkle_vs_vbs_filename>' % (sys.argv[0]))
		exit(-1)
	
	data_portfolio_selector_sparkle_vs_vbs_filename = sys.argv[1]
	penalty_time = sys.argv[2]
	upper_bound = float(penalty_time)*1.5
	lower_bound = 0.01
	vbs_name = sys.argv[3]
	portfolio_selector_sparkle_name = sys.argv[4]
	figure_portfolio_selector_sparkle_vs_vbs_filename = sys.argv[5]
	
	output_eps_file = figure_portfolio_selector_sparkle_vs_vbs_filename + r'.eps'
	output_pdf_file = figure_portfolio_selector_sparkle_vs_vbs_filename + r'.pdf'
	
	vbs_name = vbs_name.replace(r'/', r'_')
	output_gnuplot_script = portfolio_selector_sparkle_name + r'_vs_' + vbs_name + r'.plt'
	
	fout = open(output_gnuplot_script, 'w+')
	fout.write('set xlabel \'%s, PAR10\'' % (vbs_name) + '\n')
	fout.write('set ylabel \'%s, PAR10\'' % (portfolio_selector_sparkle_name)  + '\n')
	fout.write('set title \'%s vs %s\'' % (portfolio_selector_sparkle_name, vbs_name)  + '\n')
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
	fout.write('plot \'%s\' with points pt 2 ps 2' % (data_portfolio_selector_sparkle_vs_vbs_filename)  + '\n')
	fout.close()
	
	cmd = "gnuplot \'%s\'" % (output_gnuplot_script)
	os.system(cmd)
	
	cmd = "epstopdf \'%s\'" % (output_eps_file)
	os.system(cmd)
	
	os.system('rm -f \'%s\'' % (output_gnuplot_script))
	
