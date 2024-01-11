#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Automatically generate a gnuplot script for parallel algorithm portfolios."""

import os
import sys
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print(f"Usage: {sys.argv[0]} <data_parallel_portfolio_sparkle_vs_sbs_filename> "
              "<penalty_time> <sbs_name> <parallel_portfolio_sparkle_name> "
              "<figure_parallel_portfolio_sparkle_vs_sbs_filename>"
              "<performance_measure>")
        exit(-1)

    data_parallel_portfolio_sparkle_vs_sbs_filename = sys.argv[1]
    penalty_time = sys.argv[2]
    upper_bound = float(penalty_time) * 1.5
    lower_bound = 0.01
    # TODO add different options
    performance_measure = sys.argv[6]
    sbs_name = sys.argv[3]
    parallel_portfolio_sparkle_name = sys.argv[4]
    figure_parallel_portfolio_sparkle_vs_sbs_filename = sys.argv[5]

    output_eps_file = f"{figure_parallel_portfolio_sparkle_vs_sbs_filename}.eps"
    output_pdf_file = f"{figure_parallel_portfolio_sparkle_vs_sbs_filename}.pdf"

    sbs_name = sbs_name.replace("/", "_")
    sbs_name_path = sbs_name.replace("\\", "")
    output_gnuplot_script = f"{parallel_portfolio_sparkle_name}_vs_{sbs_name}.plt"

    with Path(output_gnuplot_script).open("w+") as outfile:
        outfile.write(f"set xlabel '{sbs_name}, {performance_measure}'\n")
        outfile.write(f"set ylabel '{parallel_portfolio_sparkle_name}, "
                      f"{performance_measure}'\n")
        outfile.write(f"set title '{parallel_portfolio_sparkle_name} vs {sbs_name}'\n")

        outfile.write("unset key\n")
        outfile.write(f"set xrange [{lower_bound}:{upper_bound}]\n")
        outfile.write(f"set yrange [{lower_bound}:{upper_bound}]\n")

        outfile.write("set logscale x\n")
        outfile.write("set logscale y\n")
        outfile.write("set grid\n")

        outfile.write("set size square\n")
        outfile.write(f"set arrow from {lower_bound},{lower_bound} to {upper_bound},"
                      f"{upper_bound} nohead lc rgb 'black'\n")

        if performance_measure == "PAR10":
            # Cutoff time x axis
            outfile.write(f"set arrow from {penalty_time},{lower_bound} to "
                          f"{penalty_time},{upper_bound} nohead lc rgb 'black' lt 2\n")
            # Cutoff time y axis
            outfile.write(f"set arrow from {lower_bound},{penalty_time} to {upper_bound}"
                          f",{penalty_time} nohead lc rgb 'black' lt 2\n")

        outfile.write('set terminal postscript eps color dashed linewidth "Helvetica"'
                      " 20\n")
        outfile.write(f"set output '{output_eps_file}'\n")
        outfile.write(f"plot '{data_parallel_portfolio_sparkle_vs_sbs_filename}' with "
                      "points pt 2 ps 2\n")

    cmd = f"gnuplot '{output_gnuplot_script}'"
    os.system(cmd)

    cmd = f"epstopdf '{output_eps_file}'"
    os.system(cmd)

    Path(output_gnuplot_script).unlink(missing_ok=True)
