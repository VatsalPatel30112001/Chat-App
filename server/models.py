from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime, Boolean

from database import db

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    messages = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient", cascade="all, delete-orphan")
    groups = relationship("Group", secondary="user_groups", back_populates="members")

user_groups = Table('user_groups', db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

class Group(db.Model):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    group_name = Column(String, nullable=False, unique=True)

    members = relationship("User", secondary="user_groups", back_populates="groups")
    messages = relationship("Message", back_populates="group", cascade="all, delete-orphan")

class Message(db.Model):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    is_file = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sender_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=True)
    recipient_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages")
    group = relationship("Group", back_populates="messages")
