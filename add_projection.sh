if [ "$2" == "" ]; then
   echo "usage: add_projection.sh input.nc projection.nc"
   exit
fi
ifile=$1
projfile=$2

ncks -A -v x $projfile $ifile
ncks -A -v y $projfile $ifile
ncks -A -v latitude $projfile $ifile
ncks -A -v longitude $projfile $ifile
ncks -A -v projection_lambert $projfile $ifile
ncatted -a grid_mapping,values,a,c,projection_lambert $ifile
ncatted -a coordinates,values,a,c,"longitude latitude" $ifile
