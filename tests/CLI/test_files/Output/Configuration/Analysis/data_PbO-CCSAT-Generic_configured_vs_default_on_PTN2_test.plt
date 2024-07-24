set xlabel 'Default parameters [PAR10]'
set ylabel 'Configured parameters [PAR10]'
set title ''
unset key
set xrange [0.05623413251903491:1778.2794100389228]
set yrange [0.05623413251903491:1778.2794100389228]
set logscale x
set logscale y
set grid lc rgb '#CCCCCC' lw 2
set size square
set arrow from 0.05623413251903491,0.05623413251903491 to 1778.2794100389228,1778.2794100389228 nohead lc rgb '#AAAAAA'
set arrow from 0.05623413251903491,0.5623413251903491 to 177.82794100389228,1778.2794100389228 nohead lc rgb '#CCCCCC' dashtype '-'
set arrow from 0.5623413251903491,0.05623413251903491 to 1778.2794100389228,177.82794100389228 nohead lc rgb '#CCCCCC' dashtype '-'
set arrow from 0.05623413251903491,5.623413251903491 to 17.78279410038923,1778.2794100389228 nohead lc rgb '#CCCCCC' dashtype '-'
set arrow from 5.623413251903491,0.05623413251903491 to 1778.2794100389228,17.78279410038923 nohead lc rgb '#CCCCCC' dashtype '-'
set arrow from 0.05623413251903491,56.23413251903491 to 1.7782794100389228,1778.2794100389228 nohead lc rgb '#CCCCCC' dashtype '-'
set arrow from 56.23413251903491,0.05623413251903491 to 1778.2794100389228,1.7782794100389228 nohead lc rgb '#CCCCCC' dashtype '-'
set arrow from 0.05623413251903491,562.3413251903492 to 0.1778279410038923,1778.2794100389228 nohead lc rgb '#CCCCCC' dashtype '-'
set arrow from 562.3413251903492,0.05623413251903491 to 1778.2794100389228,0.1778279410038923 nohead lc rgb '#CCCCCC' dashtype '-'
set arrow from 0.05623413251903491,600 to 1778.2794100389228,600 nohead lc rgb '#AAAAAA'
set arrow from 600,0.05623413251903491 to 600,1778.2794100389228 nohead lc rgb '#AAAAAA'
set terminal postscript eps color solid linewidth "Helvetica" 20
set output 'data_PbO-CCSAT-Generic_configured_vs_default_on_PTN2_test.eps
set style line 1 pt 2 ps 1.5 lc rgb 'royalblue' 
plot 'data_PbO-CCSAT-Generic_configured_vs_default_on_PTN2_test.dat' ls 1
