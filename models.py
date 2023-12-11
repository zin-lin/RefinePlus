from flask_sqlalchemy import *
from uuid import uuid4
from sqlalchemy.orm import relationship

# This is a database instance
db = SQLAlchemy()


# get unique id
def get_uid():
    return uuid4().hex


# class :: table :: User
class User(db.Model):
    __tableName__ = "user"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uid)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.Text, nullable=False)
    def get_email(self):
        return self.email


# class :: table :: UserDetails
class UserDetails(db.Model):
    __tableName__ = "user_details"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uid)
    uid = db.Column(db.String(150), db.ForeignKey('user.id'), unique=True)
    name = db.Column(db.String(150))
    profession = db.Column(db.String(150), unique=True)
    profile_pic = db.Column(db.String(300))
    api = db.Column(db.Integer)


# class :: table :: Book
class Book(db.Model):
    __tableName__ = "book"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uid)
    uid = db.Column(db.String(150), db.ForeignKey('user.id'), index = True)
    title = db.Column(db.String(150))
    cover_img = db.Column(db.String(500))

# class :: table :: projects
class Project(db.Model):
    __tableName__ = "project"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uid)
    uid = db.Column(db.String(150), db.ForeignKey('user.id'), index = True)
    title = db.Column(db.String(150))
    filename = db.Column(db.String(500))


