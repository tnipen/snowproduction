import numpy as np
import matplotlib.pylab as mpl
import netCDF4
import verif.util
import sys
import mpl_toolkits.basemap
import argparse

__version__ = "0.1.0"


def plot(lats, lons, values, args):
   mpl.clf()
   dlat = 0
   dlon = 0
   res = 'l'
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
           mpl.contourf(x, y, values, cmap=cmap)
       else:
           mpl.contourf(x, y, values, args.edges, cmap=cmap)
   else:
       mpl.contourf(values, cmap=cmap)
   cb = mpl.colorbar(extend="both")
   cb.set_label("Snow production potential (hours)")
   mpl.show()

def load_finished_file(filename):

    file = netCDF4.Dataset(filename, 'r')
    lats = verif.util.clean(file.variables["latitude"])
    lons = verif.util.clean(file.variables["longitude"])
    values = verif.util.clean(file.variables["values"])
    file.close()
    return [lats, lons, values]


def wetbulb(temperature, rh):
    """
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


def snow_production(temperature, rh, threshold=0):
    return wetbulb(temperature, rh) < threshold


def save(lats, lons, values, filename):
    """
    Creates a netcdf file with snow production values

    Arguments:
        lats: 2D numpy array with latitudes
        lons: 2D numpy array with longitudes
        values: 2D numpy array with snow production values
        filename (str): Write to this filename
    """

    file = netCDF4.Dataset(filename, 'w', format="NETCDF4")
    file.createDimension("x", lats.shape[1])
    file.createDimension("y", lats.shape[0])
    vLat=file.createVariable("latitude", "f4", ("y", "x"))
    vLon=file.createVariable("longitude", "f4", ("y", "x"))
    vValues=file.createVariable("values", "f4", ("y", "x"))

    vLat[:] = lats
    vLon[:] = lons
    vValues[:] = values
    vValues.units = "hours"
    file.close()


def get_values(dates, threshold):
    lats = None
    lons = None
    tindex = range(6, 30)

    total = None
    count = 0
    for date in dates:
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
            print ifilename
            ifile = netCDF4.Dataset(ifilename, 'r')
            print 1
            if lats is None:
                lats = verif.util.clean(ifile.variables["latitude"])
                lons = verif.util.clean(ifile.variables["longitude"])
            t2 = verif.util.clean(ifile.variables["air_temperature_2m"][tindex, :, :, :])-273.15
            rh2 = verif.util.clean(ifile.variables["relative_humidity_2m"][tindex, :, :, :])
            curr_hours = snow_production(t2, rh2, threshold)
            curr_hours = np.squeeze(np.sum(curr_hours, axis=0))
            if total is None:
                total = curr_hours
            else:
                total += curr_hours
            count += 1
            ifile.close()
        except Exception as e:
            print "Could not parse %s" % ifilename
            print e

    total = total * 1.0 / count * 365
    return [lats, lons, total]

def main():
    parser = argparse.ArgumentParser(description="Create maps of snow production potential")
    parser.add_argument('--version', action="version", version=__version__)
    subparsers = parser.add_subparsers(title="valid commands", dest="command")
    p_compute = subparsers.add_parser('compute', help='Compute hours')                                         
    p_compute.add_argument('-d', type=str, help='Dates', dest="dates")
    p_compute.add_argument('-r', required=True, type=float, help='Threshold (degrees C)', dest="threshold")
    p_compute.add_argument('-f', type=str, help='Output filename', dest="filename")

    p_plot = subparsers.add_parser('plot', help='Plot hours')
    p_plot.add_argument('-f', type=str, help='Input filename', dest="filename")
    p_plot.add_argument('-xlim', help='x-axis limits', type=verif.util.parse_numbers)
    p_plot.add_argument('-ylim', help='y-axis limits', type=verif.util.parse_numbers)
    p_plot.add_argument('-edges', help='Colorbar edges', type=verif.util.parse_numbers)
    p_plot.add_argument('-cmap', help='Colormap', type=str)
    p_plot.add_argument('-maptype', help='maptype', type=str)

    args = parser.parse_args()

    if args.command == "compute":
        dates = verif.util.parse_numbers(args.dates, True)
        [lats, lons, values] = get_values(dates, args.threshold)
        save(lats, lons, values, args.filename)
    elif args.command == "plot":
        [lats, lons, values] = load_finished_file(args.filename)
        plot(lats, lons, values, args)

if __name__ == '__main__':
    main()
