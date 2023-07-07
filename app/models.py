from email.policy import default
from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        String,
                        Boolean,
                        Date,
                        BigInteger
                        )
from sqlalchemy.sql import expression, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import TIMESTAMP
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class AdminUser(Base):
    __tablename__ = 'admin_users'
    id = Column(Integer, primary_key=True)
    email = Column(String(48), unique=True, nullable=False)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    password = Column(String(128), nullable=False)
    last_logon = Column(TIMESTAMP)

    def __repr__(self):
        return f'<Admin User {self.first_name} {self.last_name}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class AdminTokenRequest(Base):
    __tablename__ = 'admin_token_requests'

    id = Column(Integer, primary_key=True)
    email = Column(String(48), unique=True, nullable=False)
    token = Column(String(128), nullable=False)
    token_expiration_date = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return f'<Register {self.email}>'


class User(Base):
    __tablename__ = 'users'

    telegram_id = Column(BigInteger, primary_key=True)
    username = Column(String(32), unique=True, nullable=True)
    email = Column(String(48), unique=True, nullable=True)
    external_id = Column(Integer, unique=True, nullable=True)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    has_mailing = Column(Boolean, default=False)
    date_registration = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    external_signup_date = Column(TIMESTAMP, nullable=True)
    banned = Column(Boolean, server_default=expression.false(), nullable=False)

    def __repr__(self):
        return f'<User {self.telegram_id}>'


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
    created_date = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_date = Column(TIMESTAMP, server_default=func.current_timestamp(),
                          nullable=False, onupdate=func.current_timestamp())

    def __repr__(self):
        return f'<Task {self.title}>'


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    archive = Column(Boolean())
    users = relationship('User', secondary='users_categories', backref=backref('categories'))
    tasks = relationship('Task', backref=backref('categories'))
    parent_id = Column(Integer, ForeignKey('categories.id'))
    children = relationship('Category',
                            uselist=True,
                            backref=backref('parent', remote_side=[id]),
                            lazy='subquery',
                            join_depth=1)

    def __repr__(self):
        return f'<Category {self.name}>'


class Statistics(Base):
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    command = Column(String(100))
    added_date = Column(TIMESTAMP, default=func.current_timestamp(), nullable=False)

    def __repr__(self):
        return f'<Command {self.command}>'


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    message = Column(String(4096), nullable=False)
    was_sent = Column(Boolean, default=False)
    sent_date = Column(TIMESTAMP)
    sent_by = Column(String(48), nullable=True)

    def __repr__(self):
        return f'<Notification {self.message[0:10]}>'


class Users_Categories(Base):
    __tablename__ = 'users_categories'
    telegram_id = Column(BigInteger,
                         ForeignKey('users.telegram_id'),
                         primary_key=True)
    category_id = Column(Integer,
                         ForeignKey('categories.id'),
                         primary_key=True)


class ReasonCanceling(Base):
    __tablename__ = 'reasons_canceling'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    reason_canceling = Column(String(48), nullable=False)
    added_date = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_date = Column(TIMESTAMP, server_default=func.current_timestamp(),
                          nullable=False, onupdate=func.current_timestamp())
    archive = Column(Boolean, server_default=expression.false(), nullable=False)


class ExternalSiteUser(Base):
    __tablename__ = 'external_site_users'
    external_id = Column(Integer, primary_key=True)
    external_id_hash = Column(String(256), nullable=False)
    email = Column(String(48), nullable=False)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    specializations = Column(String(), nullable=True)
    created_date = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_date = Column(TIMESTAMP, server_default=func.current_timestamp(),
                          nullable=False, onupdate=func.current_timestamp())
    source = Column(String())

    def __repr__(self):
        return f'<SiteUser {self.email}>'
