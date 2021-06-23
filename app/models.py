from datetime import datetime
from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        String,
                        Boolean,
                        DateTime,
                        Date,
                        )

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class UserAdmin(Base):
    __tablename__ = 'admin_user'
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
    __tablename__ = 'register'

    id = Column(Integer, primary_key=True)
    email = Column(String(48), unique=True, nullable=False)
    token = Column(String(128), nullable=False)
    token_expiration_date = Column(DateTime, nullable=False)

    def __repr__(self):
        return f'<Register {self.email}>'


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=True)
    email = Column(String(48), unique=True, nullable=True)
    telegram_id = Column(String(15), unique=True, nullable=False)
    first_name = Column(String(32), nullable=True)
    last_name = Column(String(32), nullable=True)
    has_mailing = Column(Boolean, default=True)
    date_registration = Column(DateTime, default=datetime.today().date())

    def __repr__(self):
        return f'<User {self.username}>'

    def get_user_information(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'telegram_id': self.telegram_id,
            'has_mailing': self.has_mailing,
            'last_logon': self.last_logon

        }


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    name_organization = Column(String)
    deadline = Column(Date)
    category_id = Column(Integer, ForeignKey('category.id'))
    bonus = Column(Integer)
    location = Column(String)
    link = Column(String)
    description = Column(String)
    archive = Column(Boolean)

    def __repr__(self):
        return f'<Task {self.title}>'


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    task = relationship('Task', backref='category')
    archive = Column(Boolean())

    def __repr__(self):
        return f'<Category {self.name}>'


class Statistics(Base):
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(15), ForeignKey('user.telegram_id'))
    command = Column(String(100))
    added_date = Column(Date)

    def __repr__(self):
        return f'<Command {self.command}>'


class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    message = Column(String(4096), nullable=False)
    was_sent = Column(Boolean, default=False)
    sent_date = Column(DateTime)
