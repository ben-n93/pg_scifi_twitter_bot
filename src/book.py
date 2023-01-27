"""Book class module."""

class Book:
    """A book from the Project Guntenberg collection."""
    
    def __init__(self, text_ID, title, authors):
        """ Constructor method.
        
        Parameters
        ----------
        text_ID : str
             A unique ID used in the Project Guntenberg archive.
        title : str
                Title of the book.
        authors : str
                Authors (including illustrators) of the book.
         
        Attributes
        ----------
        URL : str
            The Project Guntenberg URL of the book.
        
        """
        self.text_ID = str(text_ID)
        self.title = title
        self.URL = f"https://www.gutenberg.org/ebooks/{text_ID}"

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
