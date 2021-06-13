#!/bin/sh
for i in data/vitek_pdfs/*.pdf; do
    filename=$(basename $i)
    name="${filename%.*}"
    name=$(echo $name | cut -f2 -d'_')
    python data/pdf2csv.py -pf $i -cf data/vitek_csvs/${name}.csv
done
