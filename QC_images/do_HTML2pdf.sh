#!/bin/bash

# Converts HTML to pdf

bd=/data00/layerfMRI/Github_repo/layerfMRI/QC_images

arr=$(find ${bd} -name "*.html" | awk -F. '{print $1}')

printf "%s\n" ${arr[@]} | xargs -n 1 -P 30 -I{} pandoc {}.html -o {}.pdf


# EOF
