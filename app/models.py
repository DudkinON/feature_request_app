#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Date, DateTime
from sqlalchemy.orm import sessionmaker
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

from argon2.exceptions import VerifyMismatchError
from argon2 import PasswordHasher
from resource import get_unique_str
from settings import CONNECT_SETTINGS, POSTGRES

Base = declarative_base()
secret_key = get_unique_str(32)
ph = PasswordHasher()


# create session
if POSTGRES:
    engine = create_engine(CONNECT_SETTINGS)
else:
    engine = create_engine('sqlite:///request.db?check_same_thread=False')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
query = session.query


class User(Base):

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(60))
    last_name = Column(String(60))
    email = Column(String(45))
    hash = Column(String(250))
    is_active = Column(Boolean, default=True)
    status = Column(Integer, default=3)
    role = Column(String(10), default='user')

    def hash_password(self, password):
        """
        Get a password string and hashing it

        :param password: (str)
        :return void:
        """
        self.hash = ph.hash(password)

    def verify_password(self, password):

        try:
            return ph.verify(self.hash, password)
        except VerifyMismatchError:
            return False


# create an engine
if POSTGRES:
    engine = create_engine(CONNECT_SETTINGS)
Base.metadata.create_all(engine)
