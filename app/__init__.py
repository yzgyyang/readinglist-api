from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from healthcheck import HealthCheck

app = Flask(__name__)

# wrap the flask app and give a heathcheck url
health = HealthCheck(app, "/healthcheck")

app.config.from_object('config')
# app.debug = True
db = SQLAlchemy(app)
db.init_app(app)

from app import models
