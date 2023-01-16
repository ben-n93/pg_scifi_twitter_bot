"""Book class module."""

class Book:
    "A book from the Project Guntenberg collection."
    def __init__(self, ID, title, authors):
        self.ID = str(ID) # To write to CSV file.
        self.title = title

        # Cleaning authors raw data.
        individual_authors = authors.split(";")
        cleaned_authors = []
        for author in individual_authors:
            author_words = author.split(" ")
            new_author_words = []
            for word in author_words:
                try:
                    int(word[0])
                except ValueError:
                    if word != "[Illustrator]":
                        new_word = word.replace(",", "")
                        new_author_words.insert(-1, new_word)
                    else:
                        new_author_words.append(word)
                except IndexError:
                    pass
            cleaned_author = " ".join(new_author_words)
            cleaned_authors.append(cleaned_author)
        self.authors = cleaned_authors
        self.URL = f"https://www.gutenberg.org/ebooks/{ID}"