#!/bin/bash

set -e

timing_file="timing"

rm -f $timing_file

run() {
    echo $1
    for db in $1; do
	echo running $db
	rm -f $db.sqlite
	( time cyclus $db.xml -o $db.sqlite ) &> out
	echo "$db" >> $timing_file
	cat out | tail -n 3 >> $timing_file
	rm out
	cyan -db $db.sqlite post
    done
}

run "base_case once_through outage military tariff"
run "base_case_cbc once_through_cbc outage_cbc military_cbc tariff_cbc"

# run "tariff"
# run "tariff_cbc"
