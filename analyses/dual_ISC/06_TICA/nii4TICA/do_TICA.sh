#!/bin/bash

rm -rf resTICA

melodic -i listfiles \
        -o resTICA \
        -m mask.nii.gz \
        -a tica \
        --report \
        --vn \
        -v 




#EOF
