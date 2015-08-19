#!/bin/bash

db=$1

# split db in two, take first item as name for other files
IFS='.' read -ra FOO <<< $db
name=${FOO[0]}

echo working on $db

cyan -db $db post

cyan -db $db flowgraph > flow.dot
dot -Tpng -o "$name"_flow.png flow.dot

cyan -db $db inv -p -nucs=Pu239 reactor
cyan -db $db inv -p -nucs=Pu239 fabrication
