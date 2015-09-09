#!/bin/bash

dbs="base_case military tariff"

for db in $dbs; do
    echo running $db
    rm $db.sqlite
    cyclus $db.xml -o $db.sqlite
done
