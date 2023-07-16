"""This file contains database models to retrieve data"""
from sqlalchemy import Integer, String, Column, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from dao import BaseModel
# --------------------------------------------------------------------------


class UserPost(BaseModel):
    """This class represents a user_post database spreadsheet"""
    __tablename__ = 'user_post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    post_id = Column(
        Integer, ForeignKey('post.id', ondelete='CASCADE'), nullable=True)


class User(BaseModel):
    """This class represents a user database spreadsheet"""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50))
    email = Column(String(30))
    avatar = Column(String(255), nullable=True)
    name = Column(String(50), nullable=True)
    surname = Column(String(50), nullable=True)
    age = Column(Integer, nullable=True)
    password = Column(String(50))
    liked_posts = relationship(
        'Post', back_populates='favorites', sync_backref=True,
        secondary='user_post', lazy='joined')
    created_posts = relationship(
        'Post', passive_deletes=True, lazy='joined'
    )


class Post(BaseModel):
    """This class represents a post database spreadsheet"""
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text)
    image = Column(String(255), nullable=True)
    favorites = relationship(
        'User', secondary='user_post', back_populates='liked_posts',
        sync_backref=True, lazy='joined')
    owner_id = Column(Integer, ForeignKey('user.id', ondelete='SET NULL'))
    created_at = Column(DateTime, default=now())
    updated_at = Column(DateTime, default=now())


