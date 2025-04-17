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
            elif direction == 'prev':
                query = query.filter(Book.id < cursor)
                order = Book.id.desc()
        except ValueError:
            return jsonify({"error": "Invalid cursor value"}), 400

    books = query.order_by(order).limit(limit + 1).all()

    if direction == 'prev':
        books = list(reversed(books))

    has_more = len(books) > limit
    books = books[:limit]

    books_data = books_schema.dump(books)

    total_count = Book.query.count()

    next_url = None
    prev_url = None

    if books:
        first_id = books[0].id
        last_id = books[-1].id

        if direction == 'next' and has_more:
            next_url = url_for('book_bp.get_books', limit=limit, cursor=last_id, direction='next', _external=True)

        if direction == 'next' and cursor:
            prev_url = url_for('book_bp.get_books', limit=limit, cursor=first_id, direction='prev', _external=True)

        if direction == 'prev':
            next_url = url_for('book_bp.get_books', limit=limit, cursor=last_id, direction='next', _external=True)
            if has_more:
                prev_url = url_for('book_bp.get_books', limit=limit, cursor=first_id, direction='prev', _external=True)

    return jsonify({
        'limit': limit,
        'cursor': cursor,
        'next': next_url,
        'previous': prev_url,
        'total_count': total_count,
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
