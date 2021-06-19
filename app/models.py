from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        String,
                        Boolean,
                        DateTime,
                        Date
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

    def __repr__(self):
        return f'<User {self.first_name} {self.last_name}>'


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=True)
    email = Column(String(48), unique=True, nullable=True)
    password = Column(String(128), unique=True, nullable=True)
    telegram_id = Column(Integer())
    first_name = Column(String(32), nullable=True)
    last_name = Column(String(32), nullable=True)
    has_mailing = Column(Boolean, default=True)
    last_logon = Column(DateTime)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

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
    task_api_id = Column(Integer)
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
    category_api_id = Column(Integer)
    name = Column(String(100))
    task = relationship('Task', backref='category')
    archive = Column(Boolean())

    def __repr__(self):
        return f'<Category {self.name}>'
