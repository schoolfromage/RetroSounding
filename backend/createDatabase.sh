#!/bin/bash

for file in ./csvs/*; do
	echo "Adding ${file}"
	python3.8 ./scrapers/csv_to_whoosh.py $file ./GamesIndex/
	echo "Done"
done
