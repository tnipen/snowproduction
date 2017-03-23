hakadal:
	./run.py compute -i hakadal.txt -r=-3
	./run.py compute -i hakadal.txt -r=-7

map-3.png: snow_production_-3_1km.nc makefile run.py
	./run.py plot snow_production_-3_1km.nc -edges 0:200:4000 -dpi 100 -f $@ -fs 15.5,19.5 -fontsize 22 -cmap=epic #Vega20c

map-7.png: snow_production_-7_1km.nc makefile run.py
	./run.py plot snow_production_-7_1km.nc -edges 0:200:4000 -dpi 100 -f $@ -fs 15.5,19.5 -fontsize 22 -cmap=epic #Vega20c

snow_production_-3.nc:
	./run.py compute -f $@ -d 20121001:5:20161231 -r=-3 -debug -month
	ncks -A -v projection_lambert,x,y /lustre/storeB/immutable/short-term-archive/DNMI_AROME_METCOOP/2016/11/06/AROME_MetCoOp_00_fp.nc_20161106 $@
	ncatted -a grid_mapping,snow_production_potential,o,c,projection_lambert $@

snow_production_-7.nc:
	./run.py compute -f $@ -d 20121001:5:20161231 -r=-7 -debug -month
	ncks -A -v projection_lambert,x,y /lustre/storeB/immutable/short-term-archive/DNMI_AROME_METCOOP/2016/11/06/AROME_MetCoOp_00_fp.nc_20161106 $@
	ncatted -a grid_mapping,snow_production_potential,o,c,projection_lambert $@

proj.nc: makefile
	./run.py compute -f $@ -d 20161101:5:20161130 -r=-3 -debug
	ncks -A -v projection_lambert,x,y /lustre/storeB/immutable/short-term-archive/DNMI_AROME_METCOOP/2016/11/06/AROME_MetCoOp_00_fp.nc_20161106 $@
	ncatted -a grid_mapping,snow_production_potential,o,c,projection_lambert $@

snow_production_-3_1km.nc: snow_production_-3.nc
	fimex $< --input.type nc4 $@ --output.type nc4\
		--interpolate.projString "+proj=utm +zone=33 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs"\
      --interpolate.yAxisUnit m\
      --interpolate.xAxisUnit m\
      --interpolate.xAxisValues -75000,-74000,...,1120000\
      --interpolate.yAxisValues 6450000,6451000,...,8000000\
      --interpolate.method nearestneighbor\
      --interpolate.latitudeName latitude\
      --interpolate.longitudeName longitude

snow_production_-7_1km.nc: snow_production_-7.nc
	fimex $< --input.type nc4 $@ --output.type nc4\
		--interpolate.projString "+proj=utm +zone=33 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs"\
      --interpolate.yAxisUnit m\
      --interpolate.xAxisUnit m\
      --interpolate.xAxisValues -75000,-74000,...,1120000\
      --interpolate.yAxisValues 6450000,6451000,...,8000000\
      --interpolate.method nearestneighbor\
      --interpolate.latitudeName latitude\
      --interpolate.longitudeName longitude

proj_1km.nc:
	fimex proj.nc --input.type nc4 $@ --output.type nc4\
		--interpolate.projString "+proj=utm +zone=33 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs"\
      --interpolate.yAxisUnit m\
      --interpolate.xAxisUnit m\
      --interpolate.xAxisValues -74500,-73500,...,1119500\
      --interpolate.yAxisValues 6450500,6451500,...,7999500\
      --interpolate.method nearestneighbor\
      --interpolate.latitudeName latitude\
      --interpolate.longitudeName longitude

proj_map.png: proj_1km.nc run.py
	./run.py plot proj_1km.nc -dpi 5 -f $@ -fs 239,310
