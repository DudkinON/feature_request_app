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
