from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json
from werkzeug.security import generate_password_hash
from dataclasses import dataclass

USERS_PATH = "default_users.json"
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    has_private_profile = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return dict(username=self.username)

    def get_id(self):
        return str(self.id)

    def create_default_users():
        with open(USERS_PATH, 'r') as f:
            data = json.load(f)

        for user in data:
            if not User.query.filter_by(username=user['username']).first():
                new_user = User(username=user['username'], password=user['password'])
                new_user.password = generate_password_hash(new_user.password)
                db.session.add(new_user)
        db.session.commit()


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return dict(title=self.title, content=self.content, is_completed=self.is_completed)
