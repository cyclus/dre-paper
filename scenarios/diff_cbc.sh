#!/bin/bash

set -e

dbs="base_case once_through military tariff outage"
dbs="base_case"

commods="uox mox b_uox mil_mox"

for db in $dbs; do
    echo $db.sqlite " & $db"_cbc.sqlite
    for commod in $commods; do
	echo "Testing $commod"
	cyan -db="$db".sqlite flow -commod "$commod" > greedy_"$commod"
	cyan -db="$db"_cbc.sqlite flow -commod "$commod" > cbc_"$commod"
	diff greedy_"$commod" cbc_"$commod"
	rm greedy_"$commod" cbc_"$commod"
    done
done
