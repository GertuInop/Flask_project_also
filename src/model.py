from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Artical(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    text = db.Column(db.String(2500), nullable=False)
    is_deleted = db.Column(db.Boolean, default = False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(60), nullable=False)

    name = db.Column(db.String(80), nullable=False)
    second_name = db.Column(db.String(80), nullable=True)
    town = db.Column(db.String(80), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.Integer, nullable=True)
    is_deleted = db.Column(db.Boolean, default = False)

    def __repr__(self):
        return f'<User {self.username}>'