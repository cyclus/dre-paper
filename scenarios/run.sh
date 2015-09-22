#!/bin/bash

run() {
    echo $1
    for db in $1; do
	echo running $db
	rm $db.sqlite
	cyclus $db.xml -o $db.sqlite
    done
}

run "base_case military tariff outage"

# run "base_case_cbc military_cbc tariff_cbc"

