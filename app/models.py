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

# create an engine
if POSTGRES:
    engine = create_engine(CONNECT_SETTINGS)
Base.metadata.create_all(engine)
