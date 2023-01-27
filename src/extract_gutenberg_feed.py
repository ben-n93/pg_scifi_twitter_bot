""" Module for capturing the latest CSV data from Project Guntenberg's data feed.
"""

import os 
import csv

import requests

IDS_CSV = "data/IDs_log.csv"
SF_CATALOG = "data/sf_catalog.csv"
PG_CATALOG = "data/pg_catalog.csv"

# Access Project Guntenberg CSV feed and write catalog to CSV file.
URL = "https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"

with open(os.path.split(URL)[1], 'wb') as f, \
        requests.get(URL, stream=True) as r:
    for line in r.iter_lines():
        f.write(line+'\n'.encode())

# Create/replace CSV file with science fiction books.
os.remove(SF_CATALOG)

with open(PG_CATALOG) as input_file, open(SF_CATALOG, 'a') as output_file:

    field_names = ['Text#', 'Title', 'Authors']
    csv_reader = csv.DictReader(input_file)
    csv_writer = csv.DictWriter(output_file, field_names)
    csv_writer.writeheader()

    for row in csv_reader:
        if "Science Fiction" in row["Bookshelves"] and row["Type"] == "Text":
            csv_writer.writerow({"Text#":row["Text#"], "Title":row["Title"], "Authors":row["Authors"]})