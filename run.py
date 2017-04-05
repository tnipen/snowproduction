#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import matplotlib
# matplotlib.use('svg')
import numpy as np
import matplotlib.pylab as mpl
import netCDF4
import verif.util
import sys
#import mpl_toolkits.basemap
import matplotlib.colors
import argparse
import matplotlib
reload(sys)
sys.setdefaultencoding('ISO-8859-1')
print matplotlib.__version__

__version__ = "0.1.0"
__days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def main():
    parser = argparse.ArgumentParser(description="Create maps of snow production potential")
    parser.add_argument('--version', action="version", version=__version__)
    subparsers = parser.add_subparsers(title="valid commands", dest="command")
    p_compute = subparsers.add_parser('compute', help='Compute hours')                                         
    p_compute.add_argument('-d', help='Dates', dest="dates", type=parse_dates)
    p_compute.add_argument('-r', required=True, type=float, help='Threshold (degrees C)', dest="threshold")
    p_compute.add_argument('-f', type=str, help='Output filename', dest="filename")
    p_compute.add_argument('-month', help='Compute each month, then sum', action="store_true")
    p_compute.add_argument('-debug', help="Show debug information", action="store_true")
    p_compute.add_argument('-drybulb', help="Should the dry bulb temperature be used?", action="store_true")
    p_compute.add_argument('-i', help="Read values from this text file", dest="ifilename")

    p_plot = subparsers.add_parser('plot', help='Plot hours')
    p_plot.add_argument('file', type=str, help='Input filename')
    p_plot.add_argument('-xlim', help='x-axis limits', type=verif.util.parse_numbers)
    p_plot.add_argument('-ylim', help='y-axis limits', type=verif.util.parse_numbers)
    p_plot.add_argument('-edges', help='Colorbar edges', type=verif.util.parse_numbers)
    p_plot.add_argument('-cmap', help='Colormap', type=str)
    p_plot.add_argument('-maptype', help='maptype', type=str)
    p_plot.add_argument('-debug', help="Show debug information", action="store_true")
    p_plot.add_argument('-f', metavar="file", help="Plot to this file", dest="ofile")
    p_plot.add_argument('-fs', help="Figure size width,height", dest="figsize", type=verif.util.parse_numbers)
    p_plot.add_argument('-dpi', type=int, default=300, help="Dots per inch in figure")
    p_plot.add_argument('-tight', help="Without any border padding. Useful for exporting just the values.", action="store_true")
    p_plot.add_argument('-legfs', type=int, default=10, help="Legend font size")
    p_plot.add_argument('-fontsize', type=int, default=12, help="Font size")

    args = parser.parse_args()

    if args.command == "compute":
        [lats, lons, values] = get_values(args)
        if args.filename is None:
            print values
        else:
            save(lats, lons, values, args.filename)
    elif args.command == "plot":
        [lats, lons, values] = load_finished_file(args.file)
        plot(lats, lons, values, args)


def plot(lats, lons, values, args):
   font = {'family' : 'normal',
       'weight' : 'bold',
       'size'   : args.fontsize}
   font = {'sans-serif' : 'Arial',
         'family': 'san-serif',
       'size'   : args.fontsize}
   matplotlib.rc('font', **font)

   mpl.clf()
   dlat = 0
   dlon = 0
   cmap = mpl.cm.RdBu
   if args.cmap is not None:
       cmap = args.cmap
   if args.maptype is not None:
       llcrnrlat = max(-90, np.min(lats) - dlat / 10)
       urcrnrlat = min(90, np.max(lats) + dlat / 10)
       llcrnrlon = np.min(lons) - dlon / 10
       urcrnrlon = np.max(lons) + dlon / 10
       llcrnrlat = 56
       urcrnrlat = 72
       llcrnrlon = 0
       urcrnrlon = 30
       res = verif.util.get_map_resolution([llcrnrlat, urcrnrlat], [llcrnrlon, urcrnrlon])
       if args.xlim is not None:
           llcrnrlon = args.xlim[0]
           urcrnrlon = args.xlim[1]
       if args.ylim is not None:
           llcrnrlat = args.ylim[0]
           urcrnrlat = args.ylim[1]
       map = mpl_toolkits.basemap.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat,
             urcrnrlon=urcrnrlon, urcrnrlat=urcrnrlat, projection='tmerc', lat_0=60, lon_0=10,
             resolution=res)
       map.drawcoastlines(linewidth=0.25)
       map.drawcountries(linewidth=0.25)
       map.drawmapboundary()
       [x,y] = map(lons, lats)
       if args.edges is None:
           mpl.contourf(x, y, values, cmap=cmap, extend="both")
       else:
           # mpl.contour(x, y, values, [0,1000,2000,3000,4000,5000,6000,7000,8000], colors="k", linewidths=0.3)
           mpl.contourf(x, y, values, args.edges, cmap=cmap, extend="both")
   else:
       if args.edges is None:
           # mpl.contourf(values, cmap=cmap, extend="both")
           mpl.imshow(values, cmap=cmap)
       else:
           print args.edges
           a = 0.2857
           b = 0.5714
           a = 0.25
           b = 0.50
           # a = 0.333
           # b = 0.666
           """
           cdict = {'red': [ (0.0, 0.68,0.9),
                            (a, 0.99,0.19),
                            (b, 0.855,   0.2),
                            (1,   0.776,1)],
                    'green': [(0,0.68,0.33),
                              (a,0.82,0.639),
                              (b,0.854,0.51),
                              (1,0.86,1)],
                    'blue': [(0,0.68,0.05),
                             (a,0.635,0.329),
                             (b,0.922,0.74),
                             (1,0.94,1)]}
                             """
           cdict = {'red': [ (0.0, 0.68,0.9),
                            (a, 0.99,0.19),
                            (b, 0.855,   0.776),
                            (1,   0.2,1)],
                    'green': [(0,0.68,0.33),
                              (a,0.82,0.639),
                              (b,0.854,0.86),
                              (1,0.51,1)],
                    'blue': [(0,0.68,0.05),
                             (a,0.635,0.329),
                             (b,0.922,0.94),
                             (1,0.74,1)]}
           """ 5 colours
           cdict = {'red': [(0,   1,   0.388),
                            (0.2, 0.68,0.9),
                            (0.4, 0.99,0.19),
                            (0.6, 0.78,   0.459),
                            (0.8, 0.855,   0.2),
                            (1,   0.776,1)],
                    'green': [(0,1,0.388),
                              (0.2,0.68,0.33),
                              (0.4,0.82,0.639),
                              (0.6,0.91,0.420),
                              (0.8,0.854,0.51),
                              (1,0.86,1)],
                    'blue': [(0,0,0.388),
                             (0.2,0.68,0.05),
                             (0.4,0.635,0.329),
                             (0.6,0.752,0.694),
                             (0.8,0.922,0.74),
                             (1,0.94,1)]}
           """
           epic = matplotlib.colors.LinearSegmentedColormap('epic', cdict)
           mpl.register_cmap(cmap=epic)
           cnt = mpl.contourf(values, args.edges, cmap=cmap, extend="max")
           # mpl.imshow(values[::-1,:], cmap=cmap, interpolation="nearest")
           def has_aa(x):
               return hasattr(x, 'set_antialiased')
           #for o in mpl.gcf().findobj(has_aa):
           #    print o
           #    o.set_antialiased(False)

           #for c in cnt.collections:
           #    #c.set_edgecolor("face")
           #    #print c
           #    c.set_rasterized(True)

           # mpl.imshow((values[::-1,:]/400).astype(int), cmap=cmap, interpolation='nearest')
           #mpl.imshow(values[200:210,200:210], cmap=cmap, interpolation='nearest')
   if args.legfs is not None and args.legfs > 0:
       # ax = mpl.axes([0.1,0.03, 0.1, 0.9])
       cb = mpl.colorbar(extend="both")  # , ax=ax)
       cb.ax.set_position([0.05,0.4,0.1,0.5])
       cb.set_ticks(np.linspace(0,4000,5))  # 16
       #cb.set_ticks([0,1000,2000,3000,4000])
       # cb.set_fontsize(args.legfs)
       cb.set_label(u"Snøproduksjonspotensial (timer/år)", labelpad=-120, fontsize=26)

   mpl.gca().set_position([0,0,1,1])  # mpl.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)

   if args.figsize is not None:
       mpl.gcf().set_size_inches((args.figsize),
                                 forward=True)

   if args.ofile is None:
       mpl.show()
   else:
       #mpl.savefig(args.ofile, bbox_inches='tight', dpi=args.dpi)
       mpl.savefig(args.ofile, dpi=args.dpi)


def parse_dates(string):
    """
    Translate dates in the form 20130101:20140101 into an array of date integers
    """
    dates = verif.util.parse_numbers(string, True)
    dates = [int(date) for date in dates]
    return dates 


def load_finished_file(filename):
    """ Retrieve lat, lon, and values from file """
    file = netCDF4.Dataset(filename, 'r')
    lats = verif.util.clean(file.variables["latitude"])
    lons = verif.util.clean(file.variables["longitude"])
    values = verif.util.clean(file.variables["snow_production_potential"])
    file.close()
    return [lats, lons, values]


def wetbulb(temperature, rh):
    """
    Computes the wetbulb temperature of arrays

    Arguments:
       rh: surface relative humidity between 0 and 1
       temperature: surface temperature in degrees C

    Returns:
       twet: surface wetbulb temperature in degrees C
    """
    P = 101.325;
    e = rh*0.611*np.exp((17.63*temperature)/(temperature+243.04));
    Td = (116.9 + 243.04*np.log(e))/(16.78-np.log(e));
    gamma = 0.00066 * P;
    delta = (4098*e)/pow(Td+243.04,2);
    TWet = (gamma * temperature + delta * Td)/(gamma + delta);
    TWet[e < 1e-9] = -50
    return TWet


def snow_production(temperature, rh, threshold=0, use_wetbulb=True):
    if use_wetbulb:
        return wetbulb(temperature, rh) < threshold
    else:
        return temperature < threshold


def save(lats, lons, values, filename, x=None, y=None, proj=None):
    """
    Creates a netcdf file with snow production values

    Arguments:
        lats: 2D numpy array with latitudes
        lons: 2D numpy array with longitudes
        values: 2D numpy array with snow production values
        filename (str): Write to this filename
    """

    file = netCDF4.Dataset(filename, 'w', format="NETCDF3_CLASSIC")
    file.createDimension("x", lats.shape[1])
    file.createDimension("y", lats.shape[0])
    vLat=file.createVariable("latitude", "f4", ("y", "x"))
    vLon=file.createVariable("longitude", "f4", ("y", "x"))
    vValues=file.createVariable("snow_production_potential", "f4", ("y", "x"))
    if x is not None:
        vX=file.createVariable("x", "f4", ("x"))
    if y is not None:
        vY=file.createVariable("y", "f4", ("y"))
    if proj is not None:
        vProj=file.createVariable("proj", "string", None)

    vLat[:] = lats
    vLat.units = "degrees_north" ;
    vLon[:] = lons
    vLon.units = "degrees_east" ;
    vValues[:] = values
    vValues.units = "hours"
    vValues.coordinates = "longitude latitude"
    if x is not None:
        vX[:] = x
    if y is not None:
        vY[:] = y
    if proj is not None:
        vProj[:] = proj
    file.close()


def get_values(args):
    if args.ifilename is not None:
        return get_values_text(args)
    else:
        return get_values_netcdf(args)


def get_values_text(args):
    file = open(args.ifilename)
    header = None
    index = 0
    total = [0]*12
    count = [0]*12
    for line in file:
        if header is None:
            header = line
        else:
            words = [word for word in line.strip().split(' ') if word != ""]
            if len(words) == 7 and words[5] != "x" and words[6] != "x" and words[5] != "-" and words[6] != "-":
                month = int(words[2])
                m = month - 1
                t2 = [float(words[5])]
                rh2 = [float(words[6]) / 100.0]
                total[m] += np.sum(snow_production(np.array(t2), np.array(rh2), args.threshold))
                count[m] += 1
    hours = 0
    for m in range(0, 12):
        if count[m] == 0:
            verif.util.warning("Missing data for month %d" % (m + 1))
        else:
            temp = total[m] * __days_in_month[m] / count[m] * 24
            hours += temp
            print "Values for month %d: %d %d" % (m + 1, count[m], temp)
    return [1,1,hours]


def get_values_netcdf(args):
    lats = None
    lons = None
    x = None
    y = None
    proj = None
    tindex = range(6, 30)

    if args.month:
        # Store values for each month
        total = [None]*12
        count = [0]*12
    else:
        total = None
        count = 0
    for date in args.dates:
        if args.debug:
            print date
        year = int(date / 10000)
        month = int(date / 100) % 100
        day = int(date % 100)
        if date <= 20121231:
            dir = "/lustre/storeB/users/lisesg/harmonie/AM2p5_MIST2_c38h12/archive/"
            ifilename = "%s/%04d/%02d/%02d/00/AM2p5_MIST2_c38h12_%d00_fp.nc" % (dir, year, month, day, date)
        elif date <= 20131221:
            dir = "/lustre/storeB/immutable/archive/projects/MIST2/AM2p5_MIST2/archive/"
            ifilename = "%s/%04d/%02d/%02d/00/AM2p5_MIST2_%d00_fp.nc" % (dir, year, month, day, date)
        elif date <= 20140430:
            # AROME Norway
            continue
        elif date <= 20140616:
            dir = "/lustre/storeB/immutable/short-term-archive/DNMI_AROME_METCOOP/"
            ifilename = "%s/%04d/%02d/%02d/arome_metcoop2_5km_%d_00.nc" % (dir, year, month, day, date)
        else:
            dir = "/lustre/storeB/immutable/short-term-archive/DNMI_AROME_METCOOP/"
            ifilename = "%s/%04d/%02d/%02d/AROME_MetCoOp_00_fp.nc_%d" % (dir, year, month, day, date)
        try:
            ifile = netCDF4.Dataset(ifilename, 'r')
            if lats is None:
                lats = verif.util.clean(ifile.variables["latitude"])
                lons = verif.util.clean(ifile.variables["longitude"])
                # x = verif.util.clean(Ifile.variables["x"])
                # y = verif.util.clean(Ifile.variables["y"])
                # proj = verif.util.clean(Ifile.variables["proj"])
            t2 = verif.util.clean(ifile.variables["air_temperature_2m"][tindex, :, :, :])-273.15
            rh2 = verif.util.clean(ifile.variables["relative_humidity_2m"][tindex, :, :, :])
            curr_hours = snow_production(t2, rh2, args.threshold, not args.drybulb)
            curr_hours = np.squeeze(np.sum(curr_hours, axis=0))
            if args.month:
                m = month - 1
                if total[m] is None:
                    total[m] = curr_hours
                else:
                    total[m] += curr_hours
                count[m] += 1
            else:
                if total is None:
                    total = curr_hours
                else:
                    total += curr_hours
                count += 1
            ifile.close()
        except Exception as e:
            print "Could not parse %s" % ifilename
            print e

    if args.month:
        hours = None
        for m in range(0, 12):
            if total[m] is None:
                verif.util.warning("Missing data for month %d" % (m + 1))
            else:
                if hours is None:
                    hours = np.zeros(total[m].shape, int)
                print "Values for month %d: %d" % (m + 1, count[m])
                hours += total[m] * __days_in_month[m] / count[m]
    else:
        hours = total * 1.0 / count * 365
    return [lats, lons, hours]

if __name__ == '__main__':
    main()
