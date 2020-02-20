from datetime import datetime
from flask_login import UserMixin
from sqlalchemy_utils import UUIDType
from app import db, login_manager
import uuid

class UserQuestion(db.Model):
    __tablename__ = 'users_questions'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    answer_body = db.Column(db.String(256))
    user = db.relationship('User')
    question = db.relationship('Question')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    screen_name = db.Column(db.String(128), nullable=False, unique=True)
    username = db.Column(db.String(128))
    description = db.Column(db.String(1024))
    user_image_url = db.Column(db.String(1024))
    date_published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    twitter_id = db.Column(db.String(128), nullable=False, unique=True)
    profile_msg = db.Column(db.String(1024))

    questions = db.relationship(
        'Question',
        secondary=UserQuestion.__tablename__,
        back_populates='users',
    )
    user_question = db.relationship('UserQuestion')
    def __repr__(self):
        return '<User %r>' % self.username

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    send_id = db.Column(db.Integer)
    recieve_id = db.Column(db.Integer)
    body = db.Column(db.String(256))
    date_published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    users = db.relationship(
        'User',
        secondary=UserQuestion.__tablename__,
        back_populates='questions',
    )
    user_question = db.relationship('UserQuestion')
    def __repr__(self):
        return '<Question %r>' % self.body

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
