""" Module for capturing the latest CSV data from Project Guntenberg's data feed.
"""

import csv

import requests

IDS_CSV = "data/IDs_log.csv"
SF_CATALOG = "data/sf_catalog.csv"
PG_CATALOG = "data/pg_catalog.csv"

def extract_data():
    """Extract catalog data from Project Gutenberg.
    """
    # Access Project Guntenberg CSV feed and write catalog to CSV file.
    URL = "https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"
    
    with open(PG_CATALOG, 'wb') as f:
        content = requests.get(URL, stream=True, timeout=240)
        for line in content.iter_lines():
            f.write(line+'\n'.encode())
    
    # Create CSV file of science fiction books.
    with open(PG_CATALOG) as input_file, open(SF_CATALOG, 'w') as output_file:
        field_names = ['Text#', 'Title', 'Authors']
        csv_reader = csv.DictReader(input_file)
        csv_writer = csv.DictWriter(output_file, field_names)
        csv_writer.writeheader()
        for row in csv_reader:
            if "Science Fiction" in row["Bookshelves"] and row["Type"] == "Text":
                csv_writer.writerow({"Text#":row["Text#"], "Title":row["Title"], 
                "Authors":row["Authors"]})

if __name__ == "__main__":
    extract_data()
