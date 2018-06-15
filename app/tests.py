#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from settings import HOST, CREDENTIALS
from requests import Session
from re import search
from json import dumps
from datetime import datetime

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

    def post_request(self, url, request, key, value):
        """
        Sends request with invalid date, and check response
        for status code, end existing error message in
        response data

        :param url: string
        :param request: dict
        :param key: string
        :param value: any
        :return void:
        """
        prepare_request = dict(request)
        prepare_request[key] = value
        r = self.post(url, prepare_request)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

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

    def test_03_user_logout(self):
        """
        Test user_logout function. Checks status code and
        message type. Then sends the request again to check
        that user is logged out.

        :return void:
        """

        # define credentials
        req_session.auth = (storage.get_token(), '')

        # execute request to logout the user
        r = self.post('/logout', data={})

        # tests
        self.assertEquals(r.status_code, 200)
        self.assertTrue('info' in r.json())

        # check that user is logged out
        r = self.post('/logout', data={})

        # tests
        self.assertEquals(r.status_code, 200)
        self.assertTrue('info' in r.json())

    def test_04_get_auth_token(self):
        """
        Test user authorization. Check status code, and
        user data, token in returned data.

        :return void:
        """
        req_session.auth = (CREDENTIALS['email'], CREDENTIALS['password'])
        r = self.post('/token', data={})

        # save data
        data = r.json()
        self.save_cookies()
        storage.set_token(data['token'])

        # tests
        self.assertEquals(r.status_code, 200)
        self.assertTrue('user' in data)
        self.assertTrue('token' in data)

    def test_05_update_user_profile(self):
        """
        Test update user information. Sends new first name,
        last name, email, and password, then checks respond
        updated data each field. Then sends old data for
        recovered user info, and checks status code.

        :return void:
        """
        req_session.auth = (storage.get_token(), '')
        usr = dict()
        usr['first_name'] = 'John'
        usr['last_name'] = 'Doe'
        usr['email'] = 'john@doe.com'
        password = 'johndoe'
        r = self.post('/profile/update', {'user': usr, 'password': password})
        user = r.json()

        # tests
        self.assertEquals(r.status_code, 200)
        self.assertEquals(user['first_name'], 'John')
        self.assertEquals(user['last_name'], 'Doe')
        self.assertEquals(user['email'], 'john@doe.com')

        # recovering user data
        data = {'user': CREDENTIALS, 'password': CREDENTIALS['password']}
        r = self.post('/profile/update', data=data)
        self.assertEquals(r.status_code, 200)

    def test_06_new_client(self):
        """
        Testing create a new request. Sends request with
        invalid client name in checks behavior of back-end,
        then sends request with valid client name, and
        try to find the client name in returned data.

        :return void:
        """
        # test case for empty data for the request
        client = {}
        r = self.post('/clients/new', client)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for too short client name
        client = {'name': ''}
        r = self.post('/clients/new', client)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for client name as an integer
        client = {'name': 2}
        r = self.post('/clients/new', client)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for valid client name
        client = {'name': 'Test client'}
        r = self.post('/clients/new', client)
        clients = r.json()
        name = None
        for client in clients:
            if client['name'] == 'Test client':
                storage.set_client(client)
                name = client['name']
        self.assertEquals(r.status_code, 200)
        self.assertEquals(name, 'Test client')

    def test_07_update_client_info(self):
        """
        Test update client info. Sends requests with invalid
        data like empty data, empty client name, client name
        is not string, client not exist and check response
        for status code and existing error message. Then sends
        valid data and checks response that client name was
        updated.

        :return void:
        """
        # test case for empty data for the request
        client = {}

        r = self.post('/clients/edit', client)

        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for too short client name
        client = {'name': ''}
        r = self.post('/clients/edit', client)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for client name an integer
        client = {'name': 2}
        r = self.post('/clients/edit', client)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for client not existing
        client = {'name': "Valid client", 'id': 9999999}
        r = self.post('/clients/edit', client)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for valid data
        client = {'name': "Valid client", 'id': storage.get_client()['id']}
        r = self.post('/clients/edit', client)
        name = None
        for client in r.json():
            if client['name'] == "Valid client":
                storage.set_client(client)
                name = client['name']
        self.assertEquals(r.status_code, 200)
        self.assertEquals(name, "Valid client")
