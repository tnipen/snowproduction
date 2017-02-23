#!/bin/bash
if [ "$1" == "" ]; then
   echo "usage: add_projection.sh input.nc projection.nc"
   exit
fi
ifile=$1
if [ "$2" == "" ]; then
   projfile="/lustre/storeB/users/lisesg/harmonie/AM2p5_MIST2_c38h12/archive//2012/10/25/00/AM2p5_MIST2_c38h12_2012102500_fp.nc"
else
   projfile=$2
fi

ncks -A -v x $projfile $ifile
ncks -A -v y $projfile $ifile
ncks -A -v latitude $projfile $ifile
ncks -A -v longitude $projfile $ifile
ncks -A -v projection_lambert $projfile $ifile
ncatted -a grid_mapping,snow_production_potential,a,c,projection_lambert $ifile
ncatted -a coordinates,snow_production_potential,a,c,"longitude latitude" $ifile
