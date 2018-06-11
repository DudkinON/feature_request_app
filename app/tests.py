#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from settings import HOST, CREDENTIALS
from requests import Session
from re import search
from json import dumps


req_session = Session()


class Storage(object):
    """
    Provide storage for data like uid, csrf, token, and cookies
    """

    def __init__(self):
        self.uid = None
        self.csrf = None
        self.token = None
        self.cookies = None

    def set_uid(self, uid):
        """
        Setter for user id

        :param uid: integer
        :return void:
        """
        self.uid = uid
