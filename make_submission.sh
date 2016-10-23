#/usr/bin/bash

rm -rf latex_src
mkdir latex_src
cp *.tex *.bib *.pdf latex_src
tar -czf latex_src.tar.gz latex_src

pdftk paper.pdf cat 1-2 output title_page.pdf
pdftk paper.pdf cat 3-48 output manuscript.pdf
pdftk paper.pdf cat 49-53 output bibliography.pdf
