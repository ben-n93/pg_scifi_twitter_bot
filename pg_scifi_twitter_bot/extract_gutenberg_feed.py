""" Module for capturing and uploading the latest CSV data from Project 
Guntenberg's data feed."""

import csv
from io import StringIO
import sqlite3

import requests


def extract_data():
    """Extract catalog data from Project Gutenberg and upload to database."""
    database = "/Users/benjaminnour/Documents/Python/books.db"
    SQL = """
    INSERT INTO books_catalog (book_id, title, authors)
    VALUES (?, ?, ?)
    """
    URL = "https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"

    response = requests.get(URL, stream=True, timeout=240)
    content = response.content.decode("utf-8")
    csv_file = StringIO(content)
    csv_reader = csv.reader(csv_file)
    sf_books = [
        row for row in csv_reader if row[1] == "Text" and "Science Fiction" in row[8]
    ]
    processed_sf_books = []
    for book in sf_books:
        processed_book = []
        for index, field in enumerate(book):
            if index in (0, 3, 5):
                field = field.replace("\n", " ")
                field = field.replace("\r", "")
                processed_book.append(field)
        processed_sf_books.append(processed_book)

    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.executemany(SQL, processed_sf_books)
        conn.commit()
