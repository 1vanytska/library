from fastapi import APIRouter, HTTPException, status
from ..schemas.book_schema import BookSchema
from ..models.book_model import Book
from ..storage.book_storage import books

router = APIRouter()

@router.get("/books")
async def get_books():
    return books

@router.get("/books/{book_id}")
async def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@router.post("/books", status_code=status.HTTP_201_CREATED)
async def add_book(book: BookSchema):
    new_book = Book(title=book.title, author=book.author)
    book_dict = new_book.to_dict()
    books.append(book_dict)
    return book_dict

@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return {"message": "Book deleted"}
    raise HTTPException(status_code=404, detail="Book not found")
