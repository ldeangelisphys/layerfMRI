
sub=`printf %02d $1`

sourcedir=/data02/ritu/2018_7T_14sub_raw

bd=/data00/leonardo/layers/rawdata_LIP/sub_${sub}

cd ${bd}

for i in `find . -name *task*`; do


  c4d ${i} -info-full | grep Canon
  # echo ${i}
  echo

done
