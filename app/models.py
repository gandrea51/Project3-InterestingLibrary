from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))    
    genre = db.Column(db.String(1))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256))
    role = db.Column(db.String(1))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(40), nullable=False)
    classification = db.Column(db.String(10), nullable=False)
    position = db.Column(db.String(5), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    necklace = db.Column(db.String(255))
    publisher = db.Column(db.String(255), nullable=False)
    note = db.Column(db.Text)
    copy = db.Column(db.Integer, nullable=False)
    bview = db.Column(db.Integer, nullable=False)
    bdownload = db.Column(db.Integer, nullable=False)
    bmonth = db.Column(db.String(2), nullable=False)
    magazine = db.Column(db.String(2), nullable=False)
    available = db.Column(db.String(2), nullable=False)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_start = db.Column(db.Date, nullable=False)
    date_end = db.Column(db.Date, nullable=False)
    ended = db.Column(db.String(2), nullable=False)
    returned = db.Column(db.String(2), nullable=False)
    extended = db.Column(db.String(2), nullable=False)
    book_id = db.Column(db.BigInteger, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)

    book = db.relationship('Book', backref=db.backref('loans', lazy=True))
    user = db.relationship('User', backref=db.backref('loans', lazy=True))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(60), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_write = db.Column(db.Date, nullable=False)
    readit = db.Column(db.String(2), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    place = db.Column(db.String(255), nullable=False)
    date_start = db.Column(db.Date, nullable=False)
    date_end = db.Column(db.Date, nullable=False)
