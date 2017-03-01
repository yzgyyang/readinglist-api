from app import app
from app import db
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, index=True)
    password_hash = db.Column(db.String(128))
    
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    
    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = Users.query.get(data['id'])
        return user


class Lists(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    isprivate = db.Column(db.Boolean)


class Books(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String)
    title = db.Column(db.String)
    author = db.Column(db.String)
    category = db.Column(db.String)
    coverurl = db.Column(db.String)
    summary = db.Column(db.String)


class Relationships(db.Model):
    __tablename__ = 'relationships'

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer)
    book_id = db.Column(db.Integer)

