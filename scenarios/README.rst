
# Scenarios

A number of input files are provided, some of which are used in the paper, some
of which are used for testing purposes.

## dre_recycle.xml

A file very similar to ``cycamore/input/recycle.xml`` that includes minimal
updates such that:

- ``DeployInst`` is used
- there are only inventory constraints, no buffer constraints

## base_case.xml

An update of ``dre_recycle.xml`` to include the full reactor deployment that
will be used in the paper scenarios.

## military.xml

Similar to ``base_case.xml`` but adding a military MOX supplier; used in the paper.

## tariff.xml

Adds an additional external fuel cycle with a TariffRegion; used in the paper.

## *_ui.xml

Input files that were used to generate the Cycic images in the paper.
