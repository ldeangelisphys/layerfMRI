#!/bin/bash

# This script runs do_basic_preprocessing.sh for all subjects in parallel


# subjects 1 4 7 have missing data
subjects=(2 3 5 6 8 9 10 11 12 13 14)

printf "%s\n" "${subjects[@]}" | xargs -n 1 -P 12 -I{} ./do_basic_preprocessing.sh {}

echo
echo
