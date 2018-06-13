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
