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

    def set_request(self, request):
        """
        Setter for request

        :param request: dictionary
        :return void:
        """
        self.request = request

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

    def get_client(self):
        """
        Getter for client dictionary

        :return dict:
        """
        return self.client

    def get_product_area(self):
        """
        Getter for product area dictionary

        :return dict:
        """
        return self.product_area

    def get_request(self):
        """
        Getter for request dictionary

        :return dict:
        """
        return self.request


# create storage
storage = Storage()


class TestApp(TestCase):

    def setUp(self):
        # configure tests class
        self.credentials = CREDENTIALS
        self.url = HOST + '%s?csrf=%s'
        self.headers = {'content-type': 'application/json'}

    def post(self, url, data):
        """
        Execute POST query with given URL and data, then
        returns result

        :param url: string
        :param data: dictionary
        :return object:
        """
        return req_session.post(
            self.url % (url, storage.get_csrf()),
            cookies=storage.get_cookies(),
            data=dumps(data),
            headers=self.headers)

    def get(self, url):
        """
        Execute GET request with given URL, then return data

        :param url: string
        :return object:
        """
        return req_session.get(self.url % (url, storage.get_csrf()))

    @staticmethod
    def save_cookies():
        """
        Saves cookie in the storage

        :return void:
        """
        cookies = req_session.cookies.get_dict()
        storage.set_cookies(cookies)

    def test_01_front_end(self):
        """
        Test for front_end function. Test status code
        and content type. Get csrf token and cookies
        from the request and save them, for following
        test function.

        :return void:
        """
        # execute request
        r = req_session.get(HOST)

        # retrieve and save csrf token from the page
        content_type = 'text/html; charset=utf-8'
        pattern = r'\sdata-csrf-token=\"([A-Z\d]{36})\"'
        csrf = search(pattern, r.text).group(1)
        storage.set_csrf(csrf)

        # save cookies
        self.save_cookies()

        # tests
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.headers['Content-Type'], content_type)

    def test_02_registration(self):
        """
        Emulation of user registration. Uses stored csrf
        token and cookies to imitate user behavior.
        Sends post request to app with user registration
        data and checks returned user info.

        :return void:
        """
        # execute request
        r = self.post('/registration', self.credentials)

        # save data
        data = r.json()
        token = data['token']
        user = data['user']
        storage.set_token(token)
        storage.set_uid(user['uid'])
        self.save_cookies()

        # tests
        self.assertEquals(user['email'], self.credentials['email'])
        self.assertEquals(user['first_name'], self.credentials['first_name'])
        self.assertEquals(user['last_name'], self.credentials['last_name'])
        self.assertEquals(user['role'], 'user')
        self.assertEquals(user['status'], 3)
