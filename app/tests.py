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
        product area which does not exist, and checks response
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

    def test_13_update_request(self):
        """
        Tests for update_user function. Sends to the
        function  requests with invalid data, and check
        results for status code, existing error message.

        Then sends the request with valid and checks that
        in result status code equal 200, error message not
        in result, result is a list. After, retrieve the
        response from the list, and make sure that data
        were updated correctly.

        :return void:
        """
        # retrieve requests from the storage
        first_request = storage.get_request()[0]
        second_request = storage.get_request()[1]
        third_request = storage.get_request()[2]

        # test case for empty data
        client = {
            'id': first_request['client']['id'],
            'name': first_request['client']['name'],
            'client_priority': first_request['client_priority']
        }
        request = {
            'id': first_request['id'],
            'title': first_request['title'],
            'description': first_request['description'],
            'client': client,
            'target_date': first_request['target_date'],
            'product_area': first_request['product_area']
        }

        # test case for empty title
        self.post_request('/requests/edit', request, 'title', "")

        # test case for empty description
        self.post_request('/requests/edit', request, 'description', "")

        # test case for empty target date
        self.post_request('/requests/edit', request, 'target_date', "")

        # test case for empty client
        self.post_request('/requests/edit', request, 'client', "")

        # test case for empty product area
        self.post_request('/requests/edit', request, 'product_area', "")

        # test case for invalid title
        self.post_request('/requests/edit', request, 'title', [])

        # test case for invalid description
        self.post_request('/requests/edit', request, 'description', [])

        # test case for invalid target date
        self.post_request('/requests/edit', request, 'target_date', [])

        # test case for invalid client
        self.post_request('/requests/edit', request, 'client', [])

        # test case for invalid product area
        self.post_request('/requests/edit', request, 'product_area', [])

        # test case valid data
        client = {
            'id': storage.get_client()[1]['id'],
            'name': storage.get_client()[1]['name'],
            'client_priority': 1
        }
        request = {
            'id': first_request['id'],
            'title': "first request updated",
            'description': "description for first request updated",
            'client': client,
            'target_date': "06/25/2018",
            'product_area': first_request['product_area']
        }
        r = self.post('/requests/edit', request)

        # check status code, no error in response, and data type
        self.assertEquals(r.status_code, 200)
        self.assertFalse('error' in r.json())
        self.assertTrue(isinstance(r.json(), list))

        # retrieve requests form the response
        for item in r.json():
            if int(item['id']) == int(first_request['id']):
                first_request = item

            if int(item['id']) == int(second_request['id']):
                second_request = item

            if int(item['id']) == int(third_request['id']):
                third_request = item

        # convert data
        dt = datetime.strptime(first_request['target_date'],
                               '%a, %d %b %Y %X GMT')
        if dt.month < 10:
            month = "0%s" % dt.month
        else:
            month = dt.month
        data = "%s/%s/%s" % (month, dt.day, dt.year)

        # make sure that request was updated
        self.assertEquals(first_request['title'], request['title'])
        self.assertEquals(first_request['description'], request['description'])
        self.assertEquals(first_request['client']['id'],
                          request['client']['id'])
        self.assertEquals(data, request['target_date'])
        self.assertEquals(first_request['product_area']['id'],
                          request['product_area']['id'])

        # make sure that requests have correct client priority
        self.assertEquals(first_request['client_priority'], 1)
        self.assertEquals(second_request['client_priority'], 1)
        self.assertEquals(third_request['client_priority'], 2)

        # save requests
        requests = [first_request, second_request, third_request]
        storage.set_request(requests)

    def test_14_complete_request(self):
        """
        Tests for complete_request function. Checks the
        response of the function with empty data, empty
        request id, invalid request id and with not
        existing request id. Then, checks that server
        marked the request as completed

        :return viod:
        """
        # test case for empty data
        r = self.post('/requests/complete', {})
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for empty request id
        r = self.post('/requests/complete', {'id': ''})
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for invalid type of request id
        r = self.post('/requests/complete', {'id': []})
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for request id which does not exist
        r = self.post('/requests/complete', {'id': 0})
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for valid data
        request_id = storage.get_request()[0]['id']
        r = self.post('/requests/complete', {'id': request_id})
        self.assertEquals(r.status_code, 200)
        self.assertFalse('error' in r.json())
        self.assertTrue(isinstance(r.json(), list))

        # check that server mark the request as completed
        for item in r.json():
            self.assertFalse(int(item['id']) == request_id)

    def test_15_get_complete_requests(self):
        """
        Tests for get completed request. Send GET request
        to the server, and checks that status code equals
        200, and response data is a list.

        Then try to retrieve the request form the list,
        and makes sure that request in the list.

        :return void:
        """
        r = self.get('/requests/get/completed')
        self.assertEquals(r.status_code, 200)
        self.assertTrue(isinstance(r.json(), list))

        # try find the completed request
        _completed_request = None
        for item in r.json():
            if int(item['id']) == int(storage.get_request()[0]['id']):
                _completed_request = item

        self.assertTrue(bool(_completed_request))

    def test_16_get_requests(self):
        """
        Tests for requests path. Sends GET request for
        the back-end and, checks that status code is 200,
        returned data is a list, and in the list at
        least one record.

        :return void:
        """
        r = self.get('/requests')
        self.assertEquals(r.status_code, 200)
        self.assertTrue(isinstance(r.json(), list))
        self.assertTrue(len(r.json()) > 1)

    def test_17_remove_requests(self):
        """
        Tests for removal of request path. Sends post
        request with empty and invalid data and checks
        that the server returns status code 200 and
        an error in the response.

        Later, the same thing is done with valid data
        and makes sure that the request was removed.

        :return void:
        """
        # retrieve requests from the storage
        requests = storage.get_request()

        req_ids = [int(req['id']) for req in requests]

        # test case empty data
        r = self.post('/requests/delete', {})
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case request id not exist
        r = self.post('/requests/delete', {'id': ''})
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case request id not exist
        r = self.post('/requests/delete', {'id': 0})
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # remove requests
        for request in requests:
            r = self.post('/requests/delete', request)
            self.assertEquals(r.status_code, 200)
            self.assertFalse('error' in r.json())
            self.assertTrue(isinstance(r.json(), list))

        # make sure that request was removed
        all_requests = self.get('/requests')
        for request in all_requests.json():
            self.assertFalse(int(request['id']) in req_ids)
