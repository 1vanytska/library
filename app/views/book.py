from flask import Blueprint, jsonify, request, url_for
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
    direction = request.args.get('direction', 'next')

    query = Book.query
    order = Book.id.asc()

    if cursor:
        try:
            cursor = int(cursor)
            if direction == 'next':
                query = query.filter(Book.id > cursor)
                order = Book.id.asc()
            elif direction == 'prev':
                query = query.filter(Book.id < cursor)
                order = Book.id.desc()
        except ValueError:
            return jsonify({"error": "Invalid cursor value"}), 400

    books = query.order_by(order).limit(limit).all()

    if direction == 'prev':
        books = list(reversed(books))

    books_data = books_schema.dump(books)
    total_books = Book.query.count()

    next_cursor = books[-1].id if books else None
    prev_cursor = books[0].id if books else None

    next_url = (
        url_for('book_bp.get_books', limit=limit, cursor=next_cursor, direction='next', _external=True)
        if next_cursor and len(books) == limit and direction != 'prev' else None
    )

    prev_url = (
        url_for('book_bp.get_books', limit=limit, cursor=prev_cursor, direction='prev', _external=True)
        if prev_cursor and direction != 'next' else None
    )

    return jsonify({
        'total': total_books,
        'limit': limit,
        'cursor': cursor,
        'next': next_url,
        'previous': prev_url,
        'books': books_data
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
