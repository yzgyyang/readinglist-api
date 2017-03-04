#!venv/bin/python
from app import app
from flask import Flask, jsonify, url_for, make_response, request, abort, g
from app.models import db, Users, Lists, Books, Relationships
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import or_, and_

app = Flask(__name__)


# HTTPBasicAuth
auth = HTTPBasicAuth()


# Attributes for a book
book_attr = ('id', 'isbn', 'title', 'author', 'category', 'coverurl', 'summary')


@auth.verify_password
def verify_password(email_or_token, password):
    # first try to authenticate by token
    user = Users.verify_auth_token(email_or_token)
    if not user:
        # try to authenticate with email/password
        user = Users.query.filter_by(email=email_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/')
def index():
    return "Hello, World!"


# Register
@app.route('/register', methods=['POST'])
def register_user():
    email = request.json.get('email')
    password = request.json.get('password')

    if email is None or password is None:
        return jsonify({'error': 'missing arguments'}), 400
    if Users.query.filter_by(email=email).first() is not None:
        abort(400) # existing user
    
    user = Users(email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'user_id': user.id}), 201


# User login
@app.route('/user')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii'), 
                    'home': url_for('get_user', user_id=g.user.id)}), 200


# Read all lists of a user
@app.route('/user/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    verify_current_user(user_id)

    lists = Lists.query.filter_by(user_id=user_id)
    user_info = {'owner': {'user_id': user_id}}
    lists_info = []

    for l in lists:
        list_info = {}
        list_info['list_id'] = l.id
        list_info['address'] = url_for('get_list', list_id=l.id)
        list_info['isprivate'] = l.isprivate
        lists_info.append(list_info)
    user_info['lists'] = lists_info

    return jsonify(user_info), 200


# Create a new list
@app.route('/user/<int:user_id>', methods=['POST'])
@auth.login_required
def create_list(user_id):
    verify_current_user(user_id)

    isprivate = request.json.get('isprivate')
    if isprivate is None:
        return jsonify({'error': 'Missing a parameter.'}), 400
    
    new_list = Lists(user_id=user_id, isprivate=isprivate)
    db.session.add(new_list)
    db.session.commit()

    return jsonify({'list_id': new_list.id, 
                    'address': url_for('get_list', list_id=new_list.id), 
                    'isprivate': isprivate}), 201


# Delete a list and all of the contents
@app.route('/user/<int:user_id>', methods=['DELETE'])
@auth.login_required
def delete_list(user_id):
    verify_current_user(user_id)

    list_id = request.json.get('list_id')
    cur_list = Lists.query.filter_by(id=list_id).first()
    if not cur_list:
        return jsonify({'error': 'List does not exist.'}), 400
    db.session.delete(cur_list)
    relations = Relationships.query.filter_by(list_id=list_id).all()

    for relation in relations:
        if Relationships.query.filter_by(relation.book_id).count() == 1:
            book = Books.query.filter_by(id=relation.book_id).first()
            db.session.delete(book)
        db.session.delete(relation)
    db.session.commit()

    return jsonify({'status': 'List successfully deleted.'}), 201


# Show all books in a list
@app.route('/list/<int:list_id>', methods=['GET'])
@auth.login_required
def get_list(list_id):
    cur_list = Lists.query.filter_by(id=list_id).first()
    if not cur_list:
        return jsonify({'error': 'List does not exist.'}), 400
    if cur_list.isprivate:
        verify_current_user(cur_list.user_id)
    
    relations = Relationships.query.filter_by(list_id=cur_list.id).all()
    list_info = {'list_info': {'list_id': list_id,
                               'user_id': cur_list.user_id,
                               'isprivate': cur_list.isprivate}}
    books_info = []

    for relation in relations:
        book = Books.query.filter_by(id=relation.book_id).first()
        book_info = {}
        book_info['book_id'] = book.id
        book_info['title'] = book.title
        book_info['author'] = book.author
        books_info.append(book_info)
    list_info['books'] = books_info
    
    return jsonify(list_info), 200


# Add a book to the list
@app.route('/list/<int:list_id>', methods=['POST'])
@auth.login_required
def add_book(list_id):
    cur_list = Lists.query.filter_by(id=list_id).first()
    verify_current_user(cur_list.user_id)

    book = Books.query.filter_by(isbn=request.json.get('isbn')).first()
    if not book:
        book = Books(isbn=request.json.get('isbn'),
                     title=request.json.get('title'),
                     author=request.json.get('author'),
                     category=request.json.get('category'),
                     coverurl=request.json.get('coverurl'),
                     summary=request.json.get('summary'))
        db.session.add(book)
        db.session.commit()
    relation = Relationships(list_id=list_id,
                             book_id=book.id)
    db.session.add(relation)
    db.session.commit()
    return jsonify({'book_id': book.id}), 201


# Delete a book from a list
@app.route('/list/<int:list_id>', methods=['DELETE'])
@auth.login_required
def delete_book(list_id):
    cur_list = Lists.query.filter_by(id=list_id).first()
    verify_current_user(cur_list.user_id)
    book_id = request.json.get('book_id')

    relation = Relationships.query.filter(and_(Relationships.list_id == list_id,
                                          Relationships.book_id == book_id)).first()
    if not relation:
        return jsonify({'error': 'Book does not exist.'}), 400
    db.session.delete(relation)
    db.session.commit()

    # if the book is not in any other lists, delete it
    if Relationships.query.filter_by(book_id=book_id).count() == 0:
        relations = Relationships.query.filter_by(book_id=book_id).all()
        for relation in relations:
            db.session.delete(relation)
        db.session.commit()
    return jsonify({'status': 'Book successfully deleted.'}), 201


# Return info of a book
@app.route('/book/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Books.query.filter_by(id=book_id).first()
    if not book:
        return jsonify({'error': 'Book does not exist.'}), 400

    book_info = {}
    book_info['book_id'] = book.id
    book_info['isbn'] = book.isbn
    book_info['title'] = book.title
    book_info['author'] = book.author
    book_info['category'] = book.category
    book_info['coverurl'] = book.coverurl
    book_info['summary'] = book.summary

    return jsonify(book_info), 200


# Unregistered anonymus user discovery
@app.route('/discovery', methods=['GET'])
def discover():
    lists = Lists.query.filter_by(isprivate=False)
    lists_info = []
    for l in lists:
        list_info = {}
        list_info['list_id'] = l.id
        list_info['address'] = url_for('discover_list', list_id=l.id)
        list_info['isprivate'] = l.isprivate
        lists_info.append(list_info)
    
    return jsonify({'top_lists': lists_info}), 200


# Unregistered anonymus user discovery book
@app.route('/discovery/<list_id>', methods=['GET'])
def discover_list(list_id):
    cur_list = Lists.query.filter_by(id=list_id).first()
    if not cur_list:
        return jsonify({'error': 'List does not exist.'}), 400

    relations = Relationships.query.filter_by(list_id=cur_list.id).all()
    list_info = {'list_info': {'list_id': list_id}}
    books_info = []

    for relation in relations:
        book = Books.query.filter_by(id=relation.book_id).first()
        book_info = {}
        book_info['book_id'] = book.id
        book_info['title'] = book.title
        book_info['author'] = book.author
        books_info.append(book_info)

    list_info['books'] = books_info
    return jsonify(list_info), 200


# Verify the current user
def verify_current_user(id):
    user = Users.query.get(id)

    if not user:
        return jsonify({'error': 'User does not exist.'}), 400
    if user.id != g.user.id:
        return jsonify({'error': 'Wrong user, permission denied.'}), 403


if __name__ == '__main__':
    app.run(debug=True)
