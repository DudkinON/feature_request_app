#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Date
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
        """
        Password verification

        :param password:
        :return bool:
        """
        try:
            return ph.verify(self.hash, password)
        except VerifyMismatchError:
            return False

    def generate_auth_token(self):
        """
        Generate authentication token

        :return string: (token)
        """
        s = Serializer(secret_key)
        return s.dumps({'uid': self.id})

    @staticmethod
    def verify_auth_token(token):
        """
        Try to load token, success return user id false return None

        :param token:
        :return mix:
        """
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        uid = data['uid']
        return uid

    @property
    def serialize(self):
        """
        Return serialized user info

        :return dict:
        """
        return {
            'uid': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'status': self.status,
            'role': self.role
        }


class ProductArea(Base):

    __tablename__ = 'product_area'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))

    @property
    def serialize(self):
        """
        Return client info

        :return dict:
        """
        return {
            'id': self.id,
            'name': self.name
        }


class Priority(Base):

    __tablename__ = 'priority'
    id = Column('id', Integer, primary_key=True)


class Client(Base):

    __tablename__ = 'client'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50))

    @property
    def count_requests(self):
        """
        Count requests by client

        :return integer:
        """
        amount = len(query(Request.id).filter_by(client=self.id).all())
        return amount + 1

    @property
    def serialize(self):
        """
        Return client info

        :return dict:
        """
        return {
            'id': self.id,
            'name': self.name,
            'client_priority': self.count_requests
        }


class Request(Base):
    __tablename__ = 'request'
    id = Column('id', Integer, primary_key=True)
    title = Column('title', String(80))
    description = Column('description', String(250))
    client = Column('client', ForeignKey("client.id"), nullable=False)
    client_priority = Column('client_priority', ForeignKey("priority.id"))
    target_date = Column('target_date', Date)
    product_area = Column('product_area', ForeignKey("product_area.id"))
    is_active = Column('is_active', Boolean, default=True)

    @property
    def get_client(self):
        """
        Returns request's client

        :return:
        """
        client = query(Client).filter_by(id=self.client).first()
        return client.serialize if client else None

    @property
    def get_product_area(self):

        area = query(ProductArea).filter_by(id=self.product_area).first()
        return area.serialize


# create an engine
if POSTGRES:
    engine = create_engine(CONNECT_SETTINGS)
Base.metadata.create_all(engine)
