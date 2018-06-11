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

    def set_csrf(self, csrf_token):
        """
        Setter for csrf token

        :param csrf_token: string
        :return void:
        """
        self.csrf = csrf_token

    def set_token(self, token):
        """
        Setter for auth token

        :param token: string
        :return void:
        """
        self.token = token

    def set_cookies(self, cookies):
        """
        Setter for cookies

        :param cookies: dictionary
        :return void:
        """
        self.cookies = cookies

    def get_uid(self):
        """
        Getter for user id

        :return integer:
        """
        return self.uid

    def get_csrf(self):
        """
        Getter for csrf token

        :return string:
        """
        return self.csrf

    def get_token(self):
        """
        Getter for auth token

        :return string:
        """
        return self.token

    def get_cookies(self):
        """
        Getter for cookies dictionary

        :return dict:
        """
        return self.cookies
