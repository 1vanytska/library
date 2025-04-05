from flask import Blueprint, jsonify, request
from app.models.book_model import Book
from app.schemas.book_schema import BookSchema
from app import db

book_schema = BookSchema()
books_schema = BookSchema(many=True)

book_bp = Blueprint('book_bp', __name__)

@book_bp.route('/', methods=['GET'])
def get_books():
    limit = int(request.args.get('limit', 10))
    cursor = request.args.get('cursor', None)
    query = Book.query.order_by(Book.id)
    if cursor:
        query = query.filter(Book.id > cursor)

    books = query.limit(limit).all()
    books_data = [{"id": book.id, "title": book.title, "author": book.author} for book in books]
    next_cursor = books[-1].id if books else None

    return jsonify({
        'books': books_data,
        'next_cursor': next_cursor
    })

@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book_schema.dump(book))

@book_bp.route('/', methods=['POST'])
def add_book():
    data = request.get_json()

    errors = book_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    book = Book(title=data["title"], author=data["author"])
    db.session.add(book)
    db.session.commit()

    return jsonify(book_schema.dump(book)), 201

@book_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({"message": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    
    return jsonify({"message": f"Book with ID {book_id} has been deleted"}), 200
