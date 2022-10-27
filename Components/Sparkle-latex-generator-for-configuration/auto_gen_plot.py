#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''Automatically generate a gnuplot script for algorithm configuration.'''

import os
from os.path import abspath, dirname, join
import sys
from shutil import which

if __name__ == '__main__':
    if len(sys.argv) != 7 and len(sys.argv) != 9:
        print('Usage: %s <data_solver_configured_vs_default_filename> <penalty_time> '
              '<default_name> <configured_name> '
              '<figure_solver_configured_vs_default_filename> <performance_measure>'
              % (sys.argv[0]))
        exit(-1)

    data_solver_configured_vs_default_filename = sys.argv[1]
    penalty_time = sys.argv[2]
    upper_bound = float(penalty_time) * 1.5
    lower_bound = 0.01
    default_name = sys.argv[3]
    configured_name = sys.argv[4]
    figure_solver_configured_vs_default_filename = sys.argv[5]
    performance_measure = sys.argv[6]

    if performance_measure != 'PAR10':
        lower_bound = sys.argv[7]
        upper_bound = sys.argv[8]
    output_eps_file = figure_solver_configured_vs_default_filename + '.eps'
    output_pdf_file = figure_solver_configured_vs_default_filename + '.pdf'

    default_name = default_name.replace('/', '_')
    output_gnuplot_script = configured_name + '_vs_' + default_name + '.plt'

    fout = open(output_gnuplot_script, 'w+')
    fout.write("set xlabel '%s (default)'\n" % (performance_measure))
    fout.write("set ylabel '%s (configured)'\n" % (performance_measure))
    fout.write('unset key' + '\n')

    fout.write('set xrange [%s:%s]' % (lower_bound, upper_bound) + '\n')
    fout.write('set yrange [%s:%s]' % (lower_bound, upper_bound) + '\n')

    fout.write('set logscale x' + '\n')
    fout.write('set logscale y' + '\n')
    fout.write('set grid' + '\n')
    fout.write('set size square' + '\n')
    fout.write("set arrow from %s,%s to %s,%s nohead lc rgb 'black'"
               % (lower_bound, lower_bound, upper_bound, upper_bound) + '\n')
    # Only plot cutoff boundaries for PAR10, they are not meaningful for QUALITY
    # performance
    if performance_measure == 'PAR10':
        # Cutoff time x axis
        fout.write("set arrow from %s,%s to %s,%s nohead lc rgb 'black' lt 2"
                   % (penalty_time, lower_bound, penalty_time, upper_bound) + '\n')
        # Cutoff time y axis
        fout.write("set arrow from %s,%s to %s,%s nohead lc rgb 'black' lt 2"
                   % (lower_bound, penalty_time, upper_bound, penalty_time) + '\n')
    fout.write('set terminal postscript eps color dashed linewidth "Helvetica" 20\n')
    fout.write("set output '%s'" % (output_eps_file) + '\n')
    fout.write("plot '%s' with points pt 2 ps 2"
               % (data_solver_configured_vs_default_filename) + '\n')
    fout.close()

    cmd = "gnuplot '%s'" % (output_gnuplot_script)
    os.system(cmd)

    # Some systems are missing epstopdf so a copy is included
    epsbackup = abspath(join(dirname(__file__), '..', 'epstopdf.pl'))
    epstopdf = which('epstopdf') or epsbackup
    os.system("%s '%s'" % (epstopdf, output_eps_file))

    os.system("rm -f '%s'" % (output_gnuplot_script))
