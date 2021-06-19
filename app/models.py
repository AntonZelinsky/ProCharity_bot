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


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=False)
    email = Column(String(48), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    telegram_id = Column(Integer())
    first_name = Column(String(32), nullable=True)
    last_name = Column(String(32), nullable=True)
    is_superuser = Column(Boolean, default=False)
    mailing = Column(Boolean, default=True)
    last_logon = Column(DateTime)
    task = relationship('Task', backref='user')

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
            'is_superuser': self.is_superuser,
            'first_name': self.first_name,
            'laast_name': self.last_name,
            'telegram_id': self.telegram_id,
            'mailing': self.mailing,
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
    user_id = Column(Integer, ForeignKey('user.id'))
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
