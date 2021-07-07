from datetime import datetime
from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        String,
                        Boolean,
                        DateTime,
                        Date,
                        )

from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class UserAdmin(Base):
    __tablename__ = 'admin_users'
    id = Column(Integer, primary_key=True)
    email = Column(String(48), unique=True, nullable=False)
    first_name = Column(String(32), nullable=True)
    last_name = Column(String(32), nullable=True)
    password = Column(String(128), nullable=False)
    last_logon = Column(DateTime)

    def __repr__(self):
        return f'<Admin User {self.first_name} {self.last_name}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_user_information(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'last_logon': self.last_logon
        }


class Register(Base):
    __tablename__ = 'registers'

    id = Column(Integer, primary_key=True)
    email = Column(String(48), unique=True, nullable=False)
    token = Column(String(128), nullable=False)
    token_expiration_date = Column(DateTime, nullable=False)

    def __repr__(self):
        return f'<Register {self.email}>'


class User(Base):
    __tablename__ = 'users'

    telegram_id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=True)
    email = Column(String(48), unique=True, nullable=True)
    external_id = Column(Integer, unique=True, nullable=True)
    first_name = Column(String(32), nullable=True)
    last_name = Column(String(32), nullable=True)
    has_mailing = Column(Boolean, default=True)
    date_registration = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return f'<User {self.telegram_id}>'

    def get_user_information(self):
        return {
            'telegram_id': self.telegram_id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'external_id': self.external_id,
            'has_mailing': self.has_mailing,
            'date_registration': self.date_registration,
        }


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    name_organization = Column(String)
    deadline = Column(Date)
    category_id = Column(Integer, ForeignKey('categories.id'))
    bonus = Column(Integer)
    location = Column(String)
    link = Column(String)
    description = Column(String)
    archive = Column(Boolean)
    created_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime)


    def __repr__(self):
        return f'<Task {self.title}>'


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    archive = Column(Boolean())
    users = relationship('User', secondary='users_categories', backref=backref('categories'))
    tasks = relationship('Task', backref=backref('categories'))

    def __repr__(self):
        return f'<Category {self.name}>'


class Statistics(Base):
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    command = Column(String(100))
    added_date = Column(DateTime)

    def __repr__(self):
        return f'<Command {self.command}>'


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    message = Column(String(4096), nullable=False)
    was_sent = Column(Boolean, default=False)
    sent_date = Column(DateTime)
    sent_by = Column(String(48), nullable=False)

    def __repr__(self):
        return f'<Notification {self.message[0:10]}>'


class Users_Categories(Base):
    __tablename__ = 'users_categories'
    telegram_id = Column(Integer,
                         ForeignKey('users.telegram_id'),
                         primary_key=True)
    category_id = Column(Integer,
                         ForeignKey('categories.id'),
                         primary_key=True)


class ReasonCanceling(Base):
    __tablename__ = 'reasons_canceling'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    reason_canceling = Column(String(48), nullable=False)
    added_date = Column(DateTime, default=datetime.now())
