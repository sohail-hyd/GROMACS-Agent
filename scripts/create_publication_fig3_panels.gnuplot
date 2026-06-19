set terminal svg enhanced size 900,650 font "Arial,22"
set border linewidth 1.8
set tics nomirror out
set grid linewidth 0.5
set key top right
set style line 1 linewidth 3
set style line 2 linewidth 3 dashtype 2
set style line 3 linewidth 2

# Panel b: Density time series
set output "figures/publication_fig3/fig3b_density_time_series.svg"
set xlabel "Time (ps)"
set ylabel "Density (kg m^{-3})"
set title "Density time series"
plot "results/plot_data/density.dat" using 1:2 with lines linestyle 1 title "Density"

# Panel c: O-O RDF
set output "figures/publication_fig3/fig3c_oo_rdf.svg"
set xlabel "r (nm)"
set ylabel "g_{OO}(r)"
set title "O-O radial distribution function"
set xrange [0:1.0]
plot "results/plot_data/rdf_OW_OW.dat" using 1:2 with lines linestyle 1 title "O-O RDF"

# Panel d: MSD
set output "figures/publication_fig3/fig3d_msd.svg"
set xlabel "Time (ps)"
set ylabel "MSD (nm^2)"
set title "Mean square displacement"
plot "results/plot_data/msd_water.dat" using 1:2 with lines linestyle 1 title "MSD"

# Panel e: Temperature
set output "figures/publication_fig3/fig3e_temperature_time_series.svg"
set xlabel "Time (ps)"
set ylabel "Temperature (K)"
set title "Temperature time series"
plot "results/plot_data/temperature_md.dat" using 1:2 with lines linestyle 1 title "Temperature"
