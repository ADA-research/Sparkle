#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
from os.path import abspath, dirname, join
import sys
from shutil import which

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Usage: %s <data_portfolio_selector_sparkle_vs_vbs_filename> '
              '<penalty_time> <vbs_name> <portfolio_selector_sparkle_name> '
              '<figure_portfolio_selector_sparkle_vs_vbs_filename>' % (sys.argv[0]))
        exit(-1)

    data_portfolio_selector_sparkle_vs_vbs_filename = sys.argv[1]
    penalty_time = sys.argv[2]
    vbs_name = sys.argv[3].replace('_', '\\_')
    portfolio_selector_sparkle_name = sys.argv[4].replace('_', '\\_')
    figure_portfolio_selector_sparkle_vs_vbs_filename = sys.argv[5]

    output_eps_file = figure_portfolio_selector_sparkle_vs_vbs_filename + '.eps'
    output_pdf_file = figure_portfolio_selector_sparkle_vs_vbs_filename + '.pdf'

    vbs_name = vbs_name.replace('/', '_')
    output_gnuplot_script = portfolio_selector_sparkle_name + '_vs_' + vbs_name + '.plt'

    fout = open(output_gnuplot_script, 'w+')
    fout.write("set xlabel '%s, PAR10'" % (vbs_name) + '\n')
    fout.write("set ylabel '%s, PAR10'" % (portfolio_selector_sparkle_name) + '\n')
    fout.write('set title '
               "'%s vs %s'" % (portfolio_selector_sparkle_name, vbs_name) + '\n')
    fout.write('unset key' + '\n')
    fout.write('set xrange [0.01:%s]' % (penalty_time) + '\n')
    fout.write('set yrange [0.01:%s]' % (penalty_time) + '\n')
    fout.write('set logscale x' + '\n')
    fout.write('set logscale y' + '\n')
    fout.write('set grid' + '\n')
    fout.write('set size square' + '\n')
    fout.write('set arrow from 0.01,0.01 to '
               "%s,%s nohead lc rgb 'black'" % (penalty_time, penalty_time) + '\n')
    fout.write('set terminal postscript eps color solid linewidth "Helvetica" 20' + '\n')
    fout.write("set output '%s'" % (output_eps_file) + '\n')
    fout.write("plot '%s'" % (data_portfolio_selector_sparkle_vs_vbs_filename) + '\n')
    fout.close()

    cmd = "gnuplot \'%s\'" % (output_gnuplot_script)
    os.system(cmd)

    # Some systems are missing epstopdf so a copy is included
    epsbackup = abspath(join(dirname(__file__), '..', 'epstopdf.pl'))
    epstopdf = which('epstopdf') or epsbackup
    os.system("%s '%s'" % (epstopdf, output_eps_file))

    os.system("rm -f '%s'" % (output_gnuplot_script))
