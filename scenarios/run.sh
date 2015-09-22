#!/bin/bash

dbs="base_case base_case_cbc military military_cbc tariff tariff_cbc"

for db in $dbs; do
    echo running $db
    rm $db.sqlite
    cyclus $db.xml -o $db.sqlite
done
