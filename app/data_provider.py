#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import User, ProductArea, Client, Request, session

query = session.query


def get_user_by_id(uid):
    """
    Returns user by user id

    :param uid: integer
    :return return: object
    """
    return query(User).filter_by(id=uid).first() or None


def get_user_by_email(email):
    """
    Returns user object

    :param email: string
    :return: object
    """
    return query(User).filter_by(email=email).first() or None


def create_user(email, password, first_name, last_name):
    """
    Creates a new user

    :param email: string
    :param password: string
    :param first_name: string
    :param last_name: string
    :return object:
    """
    user = User(email=email, first_name=first_name, last_name=last_name)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return user


def update_user(usr):
    """
    Update user and return new data

    :param usr: dictionary
    :return object:
    """

    user = session.query(User).filter_by(id=usr['uid']).first()
    if usr['password']:
        user.hash_password(usr['password'])
    if usr['email']:
        user.email = usr['email']
    if usr['first_name']:
        user.first_name = usr['first_name']
    if usr['last_name']:
        user.last_name = usr['last_name']

    session.commit()
    return user
