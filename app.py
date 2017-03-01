#!venv/bin/python
from app import app
from flask import Flask, jsonify, url_for, make_response, request, abort, g
from app.models import db, Users
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)


# HTTPBasicAuth
auth = HTTPBasicAuth()

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
    return (jsonify({'email': user.email}), 201, {'location': url_for('get_user', id=user.id)})

@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

@app.route('/user/<int:id>')
@auth.login_required
def get_user(id):
    user = Users.query.get(id)
    if not user:
        abort(400)
    return jsonify({'email': user.email})

if __name__ == '__main__':
    app.run(debug=True)
