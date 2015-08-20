#!/bin/bash

db=cyclus.sqlite
simid= # defaults to first in db

#db=dre.sqlite
# simid=c2560eaf-6637-42ad-817f-8961623dbb36 # recycle
# simid=ab7d15ed-306f-48bb-b2c1-39dd474e4fae # base_case

# split db in two, take first item as name for other files
IFS='.' read -ra FOO <<< $db
name=${FOO[0]}

echo working on $db

cyan -db $db post

cyan -db=$db -simid=$simid -simid=$simid flowgraph -proto > flow.dot
dot -Tpng -o "$name"_flow.png flow.dot

cyan -db=$db -simid=$simid built -p reactor
cyan -db=$db -simid=$simid inv -p -nucs=Pu239 reactor
cyan -db=$db -simid=$simid inv -p -nucs=Pu239 fuelfab
