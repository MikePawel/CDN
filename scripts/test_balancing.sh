#!/bin/bash

for ((i=1; i<=10; i++))
do
    echo "Request $i"
# First request

wget "comsys.rwth-aachen.DIA-DC.group5"

wget "folks.i4.DIA-DC.group5"

echo
echo
echo "------Request $i DONE------"
done