#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Automatically generate a gnuplot script for portfolio selection."""

# import os
from os.path import dirname, join
import subprocess
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
    with pathlib.Path(output_gnuplot_script).open("w+") as fout:
        fout.write(f"set xlabel '{vbs_name}, PAR10'\n"
                   f"set ylabel '{portfolio_selector_sparkle_name}, PAR10'\n"
                   f"set title '{portfolio_selector_sparkle_name} vs {vbs_name}'\n"
                   "unset key\n"
                   f"set xrange [0.01:{penalty_time}]\n"
                   f"set yrange [0.01:{penalty_time}]\n"
                   "set logscale x\n"
                   "set logscale y\n"
                   "set grid\n"
                   "set size square\n"
                   "set arrow from 0.01,0.01 to "
                   f"{penalty_time},{penalty_time} nohead lc rgb 'black'\n"
                   "set terminal postscript eps color solid linewidth 'Helvetica' 20\n"
                   f"set output '{output_eps_file}'\n"
                   f"plot '{data_portfolio_selector_sparkle_vs_vbs_filename}'\n")

    # cmd = f"gnuplot '{output_gnuplot_script}'"
    gnuplot_process = subprocess.run(["gnuplot", output_gnuplot_script],
                                     capture_output=True)
    if gnuplot_process.returncode != 0:
        print("Error whilst running Gnuplot:"
              f"{gnuplot_process.stdout}, {gnuplot_process.stderr}")

    # Some systems are missing epstopdf so a copy is included
    epsbackup = pathlib.Path(join(dirname(__file__), "..", "epstopdf.pl")).resolve()
    epstopdf = which("epstopdf") or epsbackup
    # os.system(f"{epstopdf} '{output_eps_file}'")
    epstopdf_subprocess = subprocess([epstopdf, output_eps_file],
                                     capture_output=True)
    if epstopdf_subprocess.returncode != 0:
        print("Error whilst running EpsToPdf:"
              f"{epstopdf_subprocess.stdout}, {epstopdf_subprocess.stderr}")
    pathlib.Path(output_gnuplot_script).unlink(missing_ok=True)
