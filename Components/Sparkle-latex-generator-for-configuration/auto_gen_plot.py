#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Automatically generate a gnuplot script for algorithm configuration."""

import os
from os.path import abspath, dirname, join
import sys
from shutil import which

if __name__ == "__main__":
    if len(sys.argv) != 7 and len(sys.argv) != 9:
        print(f"Usage: {sys.argv[0]} "
              "<data_solver_configured_vs_default_filename> <penalty_time> "
              "<default_name> <configured_name> "
              "<figure_solver_configured_vs_default_filename> <performance_measure>")
        exit(-1)

    data_solver_configured_vs_default_filename = sys.argv[1]
    penalty_time = sys.argv[2]
    upper_bound = float(penalty_time) * 1.5
    lower_bound = 0.01
    default_name = sys.argv[3]
    configured_name = sys.argv[4]
    figure_solver_configured_vs_default_filename = sys.argv[5]
    performance_measure = sys.argv[6]

    if performance_measure != "PAR10":
        lower_bound = sys.argv[7]
        upper_bound = sys.argv[8]
    output_eps_file = figure_solver_configured_vs_default_filename + ".eps"
    output_pdf_file = figure_solver_configured_vs_default_filename + ".pdf"

    default_name = default_name.replace("/", "_")
    output_gnuplot_script = configured_name + "_vs_" + default_name + ".plt"

    fout = open(output_gnuplot_script, "w+")
    fout.write(f"set xlabel '{performance_measure} (default)'\n")
    fout.write(f"set ylabel '{performance_measure} (configured)'\n")
    fout.write("unset key" + "\n")

    fout.write(f"set xrange [{lower_bound}:{upper_bound}]\n")
    fout.write(f"set yrange [{lower_bound}:{upper_bound}]\n")

    fout.write("set logscale x" + "\n")
    fout.write("set logscale y" + "\n")
    fout.write("set grid" + "\n")
    fout.write("set size square" + "\n")
    fout.write(f"set arrow from {lower_bound},{lower_bound} to "
               f"{upper_bound},{upper_bound} nohead lc rgb 'black'\n")
    # Only plot cutoff boundaries for PAR10, they are not meaningful for QUALITY
    # performance
    if performance_measure == "PAR10":
        # Cutoff time x axis
        fout.write(f"set arrow from {penalty_time},{lower_bound} to "
                   f"{penalty_time},{upper_bound} nohead lc rgb 'black' lt 2"
                   + "\n")
        # Cutoff time y axis
        fout.write(f"set arrow from {lower_bound},{penalty_time} to "
                   f"{upper_bound},{penalty_time} nohead lc rgb 'black' lt 2\n")
    fout.write('set terminal postscript eps color dashed linewidth "Helvetica" 20\n')
    fout.write(f"set output '{output_eps_file}'\n")
    fout.write(f"plot '{data_solver_configured_vs_default_filename}' "
               "with points pt 2 ps 2\n")
    fout.close()

    cmd = f"gnuplot '{output_gnuplot_script}'"
    os.system(cmd)

    # Some systems are missing epstopdf so a copy is included
    epsbackup = abspath(join(dirname(__file__), "..", "epstopdf.pl"))
    epstopdf = which("epstopdf") or epsbackup
    os.system(f"{epstopdf} '{output_eps_file}'")

    os.system(f"rm -f '{output_gnuplot_script}'")
