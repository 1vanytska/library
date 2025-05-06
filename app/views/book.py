from fastapi import APIRouter, Depends, HTTPException, status
from app.db import books_collection
from app.models.book_model import BookModel
from app.schemas.book_schema import BookCreateSchema
from pydantic_mongo import PydanticObjectId
from app.auth import get_current_user

router = APIRouter()

@router.get("/books")
async def get_books(current_user: str = Depends(get_current_user)):
    books = await books_collection.find().to_list(1000)
    return [BookModel(**{**book, "id": str(book["_id"])}) for book in books]

@router.get("/books/{book_id}")
async def get_book(book_id: str, current_user: str = Depends(get_current_user)):
    try:
        book = await books_collection.find_one({"_id": PydanticObjectId(book_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid book ID format")

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookModel(**{**book, "id": str(book["_id"])})

@router.post("/books", status_code=status.HTTP_201_CREATED)
async def add_book(book: BookCreateSchema, current_user: str = Depends(get_current_user)):
    book_data = book.model_dump(exclude_unset=True)
    result = await books_collection.insert_one(book_data)
    new_book = await books_collection.find_one({"_id": result.inserted_id})
    return BookModel(**{**new_book, "id": str(new_book["_id"])})

@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: str, current_user: str = Depends(get_current_user)):
    try:
        result = await books_collection.delete_one({"_id": PydanticObjectId(book_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid book ID format")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}
