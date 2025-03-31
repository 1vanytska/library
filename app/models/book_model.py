import itertools
from ..storage.book_storage import books

class Book:
    _id_counter = itertools.count(max(book["id"] for book in books) + 1 if books else 1)

    def __init__(self, title: str, author: str):
        self.id = next(Book._id_counter)
        self.title = title
        self.author = author

    def to_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author}
