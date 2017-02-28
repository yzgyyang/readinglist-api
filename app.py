#!venv/bin/python
from app import app
from flask import Flask, jsonify, url_for, make_response, request, abort
from app.models import db, Users

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/register', methods = ['POST'])
def register_user():
    email = request.json.get('email')
    password = request.json.get('password')
    if email is None or password is None:
        abort(400) # missing arguments
    if Users.query.filter_by(email=email).first() is not None:
        abort(400) # existing user
    user = Users(email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'email': user.email}), 201) # {'location': url_for('get_user', id=user.id)}

if __name__ == '__main__':
    app.run(debug=True)
