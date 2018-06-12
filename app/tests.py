#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from settings import HOST, CREDENTIALS
from requests import Session
from re import search
from json import dumps


req_session = Session()


class Storage(object):
    """
    Provide storage for data like uid, csrf, token, cookies etc
    """

    def __init__(self):
        self.uid = None
        self.csrf = None
        self.token = None
        self.cookies = None
        self.client = None
        self.product_area = None
        self.request = None

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

    def set_client(self, client):
        """
        Setter for client

        :param client: dictionary
        :return void:
        """
        self.client = client

    def set_product_area(self, product_area):
        """
        Setter for product_area

        :param product_area: dictionary
        :return void:
        """
        self.product_area = product_area

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


# create storage
storage = Storage()


class TestApp(TestCase):

    def setUp(self):
        # configure tests class
        self.credentials = CREDENTIALS
        self.url = HOST + '%s?csrf=%s'
        self.headers = {'content-type': 'application/json'}

    def test_1_front_end(self):
        """
        Test for front_end function. Test status code
        and content type. Get csrf token and cookies
        from the request and save them, for following
        test function.

        :return void:
        """
        r = req_session.get(HOST)
        content_type = 'text/html; charset=utf-8'
        pattern = r'\sdata-csrf-token=\"([A-Z\d]{36})\"'
        csrf = search(pattern, r.text).group(1)
        cookies = req_session.cookies.get_dict()
        storage.set_csrf(csrf)
        storage.set_cookies(cookies)
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.headers['Content-Type'], content_type)
