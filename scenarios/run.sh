#!/bin/bash

set -e

run() {
    echo $1
    for db in $1; do
	echo running $db
	rm -f $db.sqlite
	cyclus $db.xml -o $db.sqlite &> out
	rm out
    done
}

run "base_case once_through military tariff outage"

run "base_case_cbc once_through_cbc military_cbc tariff_cbc outage_cbc"

