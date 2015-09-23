#!/bin/bash

dbs="base_case military tariff outage"

for db in $dbs; do
    echo $db.sqlite "-> $db"_flow.png
    cyan -db "$db".sqlite flowgraph -proto > flow.dot
    dot -Tpng -o figs/"$db"_flow.png flow.dot
done

# cyan -db=$db -simid=$simid built -p reactor
# cyan -db=$db -simid=$simid inv -p -nucs=Pu239 reactor
# cyan -db=$db -simid=$simid inv -p -nucs=Pu239 fuelfab
