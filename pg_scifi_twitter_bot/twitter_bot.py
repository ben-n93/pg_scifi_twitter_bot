"""Choose and post a science-fiction book to Twitter.

This script chooses a random science fiction from Project Gutenberg's
collection of public domain works to be posted to Twitter.
"""

import os
import csv
import io
import random
import re
import sqlite3

import requests

import tweepy

DATABASE = "books.db"
PATTERN = "\[(Illustrator|Editor|Translator|Contributor)\]"

# SQL queries.
ELIGIBLE_BOOKS = """
SELECT 
BC.*
FROM books_catalog bc 
	LEFT JOIN books_posted bp 
	ON bc.BOOK_ID = bp.BOOK_ID
	OR BC.TITLE = BP.TITLE 
WHERE BP.BOOK_ID IS NULL
"""

BOOKS_REMAINING = """
SELECT (SELECT COUNT(*) FROM books_catalog) - 
(SELECT COUNT(*) FROM books_posted) AS DIFFERENCE
"""

UPLOAD_DATA = """
INSERT INTO books_catalog (book_id, title, authors)
VALUES (?, ?, ?)
"""

# Twitter credentials.
CONSUMER_KEY = os.environ["PG_TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["PG_TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["PG_TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["PG_TWITTER_ACCESS_TOKEN_SECRET"]
BEARER_TOKEN = os.environ["PG_TWITTER_BEARER_TOKEN"]


def clean_authors(authors):
    """Clean the authors string into a more
    readable string."""
    # Remove years from authors' names and split.
    authors = [
        re.sub(", [0-9]{4}-[0-9]{4}|[0-9]{4}-", "", author) for author in authors.split(";")
    ]
    # Clean each individual authors' name.
    cleaned_authors = []
    for author in authors:
        if (match := re.search(PATTERN, author)) is not None:
            new_author = re.sub(PATTERN, "", author)
            new_author = [word.strip() for word in new_author.split(",") if word != " "]
            new_author.reverse()
            new_author.append(match.group())
            new_author = " ".join(new_author)
            cleaned_authors.append(new_author)
        else:
            new_author = [word.strip() for word in author.split(",") if word != " "]
            new_author.reverse()
            new_author = " ".join(new_author)
            cleaned_authors.append(new_author)
    # Create final string of authors' names.
    cleaned_authors = " and ".join(cleaned_authors)
    return cleaned_authors


def extract_data():
    """Extract catalog data from Project Gutenberg."""
    URL = "https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"

    response = requests.get(URL, stream=True, timeout=240)
    content = response.content.decode("utf-8")
    csv_file = io.StringIO(content)
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

    return processed_sf_books


def post_tweet():
    """Pick a book and post to Twitter."""
    # Check to see if Twitter Bot has posted all avaliable books.
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(BOOKS_REMAINING)
        if cursor.fetchall()[0][0] == 0:
            cursor.execute("DELETE FROM books_catalog;")
            cursor.execute("DELETE FROM books_posted;")
            processed_sf_books = extract_data()
            cursor.executemany(
                UPLOAD_DATA,
                processed_sf_books,
            )
        # Pick random book to be posted to Twitter.
        potential_picks = cursor.execute(ELIGIBLE_BOOKS).fetchall()
        pick = potential_picks[random.randint(0, len(potential_picks))]
        url = f"https://www.gutenberg.org/ebooks/{pick[0]}"
        authors = clean_authors(pick[2])

        # Post to Twitter.
        client = tweepy.Client(
            BEARER_TOKEN,
            CONSUMER_KEY,
            CONSUMER_SECRET,
            ACCESS_TOKEN,
            ACCESS_TOKEN_SECRET,
        )
        client.create_tweet(
            text=f"Check out {pick[1]} by {authors} #ebook #sciencefiction {url}"
        )

        # Log posted book.
        cursor.execute(
            "INSERT INTO books_posted (book_id, title) VALUES (?, ?)",
            (pick[0], pick[1]),
        )


if __name__ == "__main__":
    post_tweet()
