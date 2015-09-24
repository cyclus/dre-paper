#!/bin/bash

plot() {
    echo $1
    for db in $1; do
	echo $db.sqlite "-> $db"_flow.png
	cyan -db "$db".sqlite flowgraph -proto > flow.dot
	dot -Tpng -o figs/"$db"_flow.png flow.dot
    done
}

plot "base_case once_through military tariff outage"
plot "base_case_cbc once_through_cbc military_cbc tariff_cbc outage_cbc"

# cyan -db=$db -simid=$simid built -p reactor
# cyan -db=$db -simid=$simid inv -p -nucs=Pu239 reactor
# cyan -db=$db -simid=$simid inv -p -nucs=Pu239 fuelfab
