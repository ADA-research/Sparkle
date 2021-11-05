#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print(f'Usage: {sys.argv[0]} <data_parallel_portfolio_sparkle_vs_sbs_filename> '
              '<penalty_time> <sbs_name> <parallel_portfolio_sparkle_name> '
              '<figure_parallel_portfolio_sparkle_vs_sbs_filename>')
        exit(-1)

    data_parallel_portfolio_sparkle_vs_sbs_filename = sys.argv[1]
    penalty_time = sys.argv[2]
    upper_bound = float(penalty_time) * 1.5
    lower_bound = 0.01
    # TODO add different options
    performance_measure = 'PAR10'
    sbs_name = sys.argv[3]
    parallel_portfolio_sparkle_name = sys.argv[4]
    figure_parallel_portfolio_sparkle_vs_sbs_filename = sys.argv[5]

    output_eps_file = f'{figure_parallel_portfolio_sparkle_vs_sbs_filename}.eps'
    output_pdf_file = f'{figure_parallel_portfolio_sparkle_vs_sbs_filename}.pdf'

    sbs_name = sbs_name.replace('/', '_')
    output_gnuplot_script = f'{parallel_portfolio_sparkle_name}_vs_{sbs_name}.plt'
    fout = open(output_gnuplot_script, 'w+')
    fout.write(f'set xlabel \'{sbs_name}, PAR10\'\n')
    fout.write(f'set ylabel \'{parallel_portfolio_sparkle_name}, PAR10\'\n')
    fout.write(f'set title \'{parallel_portfolio_sparkle_name} vs {sbs_name}\'\n')

    fout.write('unset key\n')
    fout.write(f'set xrange [{lower_bound}:{upper_bound}]\n')
    fout.write(f'set yrange [{lower_bound}:{upper_bound}]\n')

    fout.write('set logscale x\n')
    fout.write('set logscale y\n')
    fout.write('set grid\n')

    fout.write('set size square\n')
    fout.write(f'set arrow from {lower_bound},{lower_bound} to {upper_bound},'
               f'{upper_bound} nohead lc rgb \'black\'\n')

    if performance_measure == 'PAR10':
        # Cutoff time x axis
        fout.write(f'set arrow from {penalty_time},{lower_bound} to {penalty_time},'
                   f'{upper_bound} nohead lc rgb \'black\' lt 2\n')
        # Cutoff time y axis
        fout.write(f'set arrow from {lower_bound},{penalty_time} to {upper_bound},'
                   f'{penalty_time} nohead lc rgb \'black\' lt 2\n')
    fout.write('set terminal postscript eps color dashed linewidth \"Helvetica\" 20\n')
    fout.write(f'set output \'{output_eps_file}\'\n')
    fout.write(f'plot \'{data_parallel_portfolio_sparkle_vs_sbs_filename}\' with points '
               'pt 2 ps 2\n')
    fout.close()

    cmd = f'gnuplot \'{output_gnuplot_script}\''
    os.system(cmd)

    cmd = f'epstopdf \'{output_eps_file}\''
    os.system(cmd)

    os.system('rm -f \'{output_gnuplot_script}\'')
