#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Automatically generate a gnuplot script for portfolio selection."""

import os
from os.path import dirname, join
import sys
from shutil import which
import pathlib

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(f"Usage: {sys.argv[0]} <data_portfolio_selector_sparkle_vs_vbs_filename> "
              "<penalty_time> <vbs_name> <portfolio_selector_sparkle_name> "
              "<figure_portfolio_selector_sparkle_vs_vbs_filename>")
        exit(-1)

    data_portfolio_selector_sparkle_vs_vbs_filename = sys.argv[1]
    penalty_time = sys.argv[2]
    vbs_name = sys.argv[3].replace("_", "\\_")
    portfolio_selector_sparkle_name = sys.argv[4].replace("_", "\\_")
    figure_portfolio_selector_sparkle_vs_vbs_filename = sys.argv[5]

    output_eps_file = figure_portfolio_selector_sparkle_vs_vbs_filename + ".eps"
    output_pdf_file = figure_portfolio_selector_sparkle_vs_vbs_filename + ".pdf"

    vbs_name = vbs_name.replace("/", "_")
    output_gnuplot_script = portfolio_selector_sparkle_name + "_vs_" + vbs_name + ".plt"

    fout = pathlib.Path(output_gnuplot_script).open("w+")
    fout.write(f"set xlabel '{vbs_name}, PAR10'" + "\n")
    fout.write(f"set ylabel '{portfolio_selector_sparkle_name}, PAR10'\n")
    fout.write(f"set title '{portfolio_selector_sparkle_name} vs {vbs_name}'\n")
    fout.write("unset key\n")
    fout.write(f"set xrange [0.01:{penalty_time}]\n")
    fout.write(f"set yrange [0.01:{penalty_time}]\n")
    fout.write("set logscale x\n")
    fout.write("set logscale y\n")
    fout.write("set grid\n")
    fout.write("set size square\n")
    fout.write("set arrow from 0.01,0.01 to "
               f"{penalty_time},{penalty_time} nohead lc rgb 'black'\n")
    fout.write("set terminal postscript eps color solid linewidth 'Helvetica' 20\n")
    fout.write(f"set output '{output_eps_file}'\n")
    fout.write(f"plot '{data_portfolio_selector_sparkle_vs_vbs_filename}'\n")
    fout.close()

    cmd = f"gnuplot '{output_gnuplot_script}'"
    os.system(cmd)

    # Some systems are missing epstopdf so a copy is included
    epsbackup = pathlib.Path(join(dirname(__file__), "..", "epstopdf.pl")).resolve()
    epstopdf = which("epstopdf") or epsbackup
    os.system(f"{epstopdf} '{output_eps_file}'")

    os.system(f"rm -f '{output_gnuplot_script}'")
