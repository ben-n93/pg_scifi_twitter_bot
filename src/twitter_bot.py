""" Module for choosing a science-fiction book to be posted to Twitter.

Extended Summary
----------------
This script chooses a random science fiction from Project Gutenberg's
collection of public domain works to be posted to Twitter.

There is also as check to see if all the sci-fi books in Project
Guntenberg's collection has already been posted to Twitter, in
which case the IDs log is cleared so that previously posted
about books can be tweeted about again.

"""

import os 
import csv
import random

import tweepy 

from book import Book

IDS_CSV = "data/IDs_log.csv"
SF_CATALOG = "data/sf_catalog.csv"
HEADERS = ["Text#", "Title"]

CONSUMER_KEY = os.environ["PG_TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["PG_TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["PG_TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["PG_TWITTER_ACCESS_TOKEN_SECRET"]
BEARER_TOKEN = os.environ["PG_TWITTER_BEARER_TOKEN"]

client = tweepy.Client(BEARER_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Pick random book to be posted to Twitter.
with open(SF_CATALOG) as sf_csv, open(IDS_CSV, "r") as IDs_csv:
    sf_csv_reader = csv.DictReader(sf_csv)
    sf_rows = [row for row in sf_csv_reader]
    sf_rows_count = len(sf_rows)

    IDs_csv_reader = csv.DictReader(IDs_csv)
    IDs_rows = [row for row in IDs_csv_reader]
    IDs_rows_count = len(IDs_rows)

# Check to see if the Twitterbot has gone through all books in the SF catalog.
if sf_rows_count == IDs_rows_count:
    os.remove(IDS_CSV)
    with open(IDS_CSV, "w") as f:
        csv_writer = csv.DictWriter(f, HEADERS)
        csv_writer.writeheader()
        csv_writer.writerow({"Text#":"0", "Title":"0"})

random_pick = sf_rows[random.randint(0, sf_rows_count)]

# Check to make sure the book chosen hasn't already been posted previously.
flag = False
while flag == False:
    with open(IDS_CSV, "r") as f:
        csv_reader = csv.DictReader(f)
        text_rows = [row['Text#'] for row in csv_reader]
        title_rows = [row['Title'] for row in csv_reader]
    if random_pick["Text#"] in text_rows or random_pick["Title"] in title_rows:
        random_pick = sf_rows[random.randint(0, rows_count)]
        continue
    else:
        flag = True
        book_pick = Book(random_pick["Text#"], random_pick["Title"],random_pick["Authors"])
        with open(IDS_CSV, 'a') as f:
            csv_writer = csv.DictWriter(f, HEADERS)
            csv_writer.writerow({"Text#":book_pick.text_ID, "Title":book_pick.title})

# Post to Twitter.
authors_string = " and ".join(book_pick.authors)
client.create_tweet(text=f"Check out {book_pick.title} by {authors_string}. #ebook #sciencefiction {book_pick.URL}")
