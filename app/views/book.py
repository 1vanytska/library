from flask import Blueprint, jsonify, request, url_for
from app.models.book_model import Book
from app.schemas.book_schema import BookSchema
from app import db

book_schema = BookSchema()
books_schema = BookSchema(many=True)

book_bp = Blueprint('book_bp', __name__)

@book_bp.route('/', methods=['GET'])
def get_books():
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)

    total_books = Book.query.count()
    books = Book.query.limit(limit).offset(offset).all()

    def build_url(new_offset):
        return url_for('book_bp.get_books', limit=limit, offset=new_offset, _external=True)

    next_url = build_url(offset + limit) if offset + limit < total_books else None
    prev_url = build_url(offset - limit) if offset - limit >= 0 else None

    return jsonify({
        "total": total_books,
        "limit": limit,
        "offset": offset,
        "next": next_url,
        "previous": prev_url,
        "books": books_schema.dump(books)
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
