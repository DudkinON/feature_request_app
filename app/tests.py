#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from settings import HOST, CREDENTIALS
from requests import Session
from re import search
from json import dumps
from datetime import datetime, date
from resource import get_unique_str, is_index, convert_date, validator
from data_provider import *

req_session = Session()


class Storage(object):
    """
    Provide storage for data like uid, csrf, token, cookies etc
    """

    def __init__(self):
        self.user = None
        self.csrf = None
        self.token = None
        self.cookies = None
        self.client = None
        self.product_area = None
        self.request = None

    def set_user(self, user):
        """
        Setter for user id

        :param user: integer
        :return void:
        """
        self.user = user

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

    def get_user(self):
        """
        Getter for user id

        :return integer:
        """
        return self.user

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
        storage.set_user(user)
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

    def test_08_get_all_clients(self):
        """
        Test for getting all clients. Sends request to back-end
        and check status code that response data is a list, and
        the list have at least one record.

        :return void:
        """
        r = self.get('/clients')
        self.assertEquals(r.status_code, 200)
        self.assertTrue(isinstance(r.json(), list))
        self.assertTrue(len(r.json()) > 0)

    def test_09_new_product_area(self):
        """
        Test for creating a new product area. Sends requests
        to the back-end with empty data, empty or invalid
        product area name, and checks response for status
        code, and existing error message. Then sends
        response with valid data and checks response for
        status code, that response data is a list, and
        in the list exist the product area.

        :return void:
        """
        # test case for empty data
        product_area = {}
        r = self.post('/areas/new', product_area)
        self.assertEqual(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for empty product area name
        product_area = {'name': ''}
        r = self.post('/areas/new', product_area)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for product area having wrong format
        product_area = {'name': []}
        r = self.post('/areas/new', product_area)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for product area with valid name
        product_area = {'name': "Valid product area"}
        r = self.post('/areas/new', product_area)
        product_area_name = None
        for area in r.json():
            if area['name'] == "Valid product area":
                storage.set_product_area(area)
                product_area_name = area['name']
        self.assertEquals(r.status_code, 200)
        self.assertTrue(isinstance(r.json(), list))
        self.assertTrue(bool(product_area_name))

    def test_10_update_product_area_info(self):
        """
        Test for updating the product area. Sends a requests
        to the back-end with empty data, empty product
        area name, invalid product area name, id of
        product area witch not exist, and checks response
        for the status code, and existing error message
        in response data.
        Then sends request with valid name, id of
        product area, and checks response data for status
        code, the data is a list, a new name of product area
        in the list.

        :return void:
        """
        # test case for empty data
        product_area = {}
        r = self.post('/areas/edit', product_area)
        self.assertEqual(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for empty product area name
        product_area = {'name': ''}
        r = self.post('/areas/edit', product_area)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for product area having wrong format
        product_area = {'name': []}
        r = self.post('/areas/edit', product_area)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for product area not existing
        product_area = {'name': "Valid product area name", 'id': 9999999}
        r = self.post('/areas/edit', product_area)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for product area with valid name
        pa_id = storage.get_product_area()['id']
        product_area = {'name': "New product area", 'id': pa_id}
        r = self.post('/areas/edit', data=product_area)
        product_area_name = None

        for area in r.json():
            if area['name'] == "New product area":
                storage.set_product_area(area)
                product_area_name = area['name']

        self.assertEquals(r.status_code, 200)
        self.assertTrue(isinstance(r.json(), list))
        self.assertTrue(bool(product_area_name))

    def test_11_get_all_product_areas(self):
        """
        Test for getting list of product areas.

        :return void:
        """
        r = self.get('/areas')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(isinstance(r.json(), list))
        self.assertTrue(len(r.json()) > 0)

    def test_12_new_request(self):
        """
        Test for creating new requests. Sends to the
        back-end requests with invalid data, and checks
        that status code is 200, end app returns an error
        message.

        Then sends request with valid data and check each
        element was save correctly.

        Then sends another request with the client priority 1,
        and make sure that in the response data second request
        has client priority 1, and the first request was updated
        and client priority of the first request equals 2.

        Then create a new client and a new request with the new
        client, and checks that the requests have correct
        client priorities, checks that new request was saved
        with the new client as well.

        :return void:
        """
        # define client prototype
        client = {
            'id': storage.get_client()['id'],
            'name': storage.get_client()['name'],
            'client_priority': 1
        }

        # define request prototype
        request = {
            'title': "new request",
            'description': "description",
            'target_date': "06/14/2018",
            'client': client,
            'product_area': storage.get_product_area()
        }

        # test case for empty data
        r = self.post('/requests/new', {})
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for empty title
        self.post_request('/requests/new', request, 'title', "")

        # test case for empty description
        self.post_request('/requests/new', request, 'description', "")

        # test case for empty target date
        self.post_request('/requests/new', request, 'target_date', "")

        # test case for empty client
        self.post_request('/requests/new', request, 'client', "")

        # test case for empty product area
        self.post_request('/requests/new', request, 'product_area', "")

        # test case for invalid title
        self.post_request('/requests/new', request, 'title', [])

        # test case for invalid description
        self.post_request('/requests/new', request, 'description', [])

        # test case for invalid target date
        self.post_request('/requests/new', request, 'target_date', [])

        # test case for invalid client
        self.post_request('/requests/new', request, 'client', [])

        # test case for invalid product area
        self.post_request('/requests/new', request, 'product_area', [])

        # test case valid data
        r = self.post('/requests/new', request)

        self.assertEquals(r.status_code, 200)
        self.assertTrue(isinstance(r.json(), list))

        resp_request = None
        for req in r.json():
            if req['title'] == request['title']:
                storage.set_request([req])
                resp_request = req
        self.assertEquals(resp_request['title'], request['title'])
        self.assertEquals(resp_request['description'], request['description'])
        self.assertEquals(int(resp_request['client']['id']),
                          int(request['client']['id']))
        self.assertEquals(int(resp_request['client_priority']),
                          int(request['client']['client_priority']))
        self.assertEquals(int(resp_request['product_area']['id']),
                          int(request['product_area']['id']))

        # create the second request with client priority 1
        request = {
            'title': "second request",
            'description': "description of second request",
            'target_date': "06/14/2018",
            'client': client,
            'product_area': storage.get_product_area()
        }
        r = self.post('/requests/new', request)
        self.assertEquals(r.status_code, 200)

        # save first request
        for req in r.json():
            if req['title'] == "new request":
                storage.set_request([req])

        # append second request
        for req in r.json():
            if req['title'] == "second request":
                saved_requests = storage.get_request()
                saved_requests.append(req)
                storage.set_request(saved_requests)

        # test case conflict client priority
        self.assertEquals(storage.get_request()[0]['client_priority'], 2)
        self.assertEquals(storage.get_request()[1]['client_priority'], 1)

        # test case with new client
        new_client = {'name': 'new client'}  # create a new client
        r = self.post('/clients/new', new_client)
        self.assertEquals(r.status_code, 200)
        self.assertTrue(isinstance(r.json(), list))
        self.assertFalse('error' in r.json())

        # retrieve the new client from response
        for item in r.json():
            if item['name'] == 'new client':
                clients = list()
                clients.append(storage.get_client())
                clients.append(item)
                storage.set_client(clients)

        # check that the client was save successfully
        self.assertTrue(isinstance(storage.get_client(), list))
        self.assertTrue(len(storage.get_client()) > 1)
        self.assertTrue(storage.get_client()[1]['name'] == 'new client')

        # create another request
        new_client = {
            'id': storage.get_client()[1]['id'],
            'name': storage.get_client()[1]['name'],
            'client_priority': storage.get_client()[1]['client_priority']
        }
        request = {
            'title': "first request of new client",
            'description': "description of second request",
            'target_date': "06/14/2018",
            'client': new_client,
            'product_area': storage.get_product_area()
        }
        r = self.post('/requests/new', request)

        self.assertEquals(r.status_code, 200)
        self.assertFalse('error' in r.json())
        self.assertTrue(isinstance(r.json(), list))

        # retrieve the requests from the response
        first_request = storage.get_request()[0]
        second_request = storage.get_request()[1]
        for item in r.json():
            if item['title'] == first_request['title']:
                requests = [item]
                storage.set_request(requests)

        for item in r.json():
            if item['title'] == second_request['title']:
                requests = storage.get_request()
                requests.append(item)
                storage.set_request(requests)

        for item in r.json():
            if item['title'] == request['title']:
                requests = storage.get_request()
                requests.append(item)
                storage.set_request(requests)

        # check that request was retrieved successfully
        self.assertTrue(len(storage.get_request()) > 2)
        self.assertTrue(storage.get_request()[2]['title'] == request['title'])

        # check that saved requests have correct client priorities
        first_request = storage.get_request()[0]
        second_request = storage.get_request()[1]
        third_request = storage.get_request()[2]
        self.assertTrue(first_request['client_priority'] == 2)
        self.assertTrue(second_request['client_priority'] == 1)
        self.assertTrue(third_request['client_priority'] == 1)

        # check that third request have correct client
        self.assertTrue(third_request['client']['name'] == 'new client')

        # save requests
        requests = [first_request, second_request, third_request]
        storage.set_request(requests)
