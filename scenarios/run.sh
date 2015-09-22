#!/bin/bash

run() {
    for db in $1; do
	echo running $db
	rm $db.sqlite
	cyclus $db.xml -o $db.sqlite
    done
}

dbs="base_case military tariff outage"
run $dbs

# dbs="base_case_cbc military_cbc tariff_cbc"
# run $dbs

