

origdir=/data00/layerfMRI/analyses/PPI/EV_predictors
nativedir=/data00/layerfMRI/Github_repo/layerfMRI//analyses/depth_native/02_feat_native//EV_predictors

for i in `ls ${origdir}`; do

	if [ -f ${nativedir}/${i} ]; then

		res=`diff -s ${origdir}/${i} ${nativedir}/${i} | awk '{print $6}'`
		echo ${i} is ${res} in PPI and native
	fi

done
