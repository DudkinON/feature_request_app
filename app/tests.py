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

    def test_18_remove_product_area(self):
        """
        Test for removing the product area. Sends requests to
        back-end with empty data, invalid product area id,
        and product area id which does not exit. In response
        checks status code, and existing error message.

        Then sends request with valid product area id, and in
        response checks the status code, response data is list,
        the id of removed product area not exist in the list.

        :return void:
        """
        # test case for empty data
        product_area = {}
        r = self.post('/areas/delete', product_area)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for empty product area id
        product_area = {'id': []}
        r = self.post('/areas/delete', product_area)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for product area id not existing
        product_area = {'id': 9999999}
        r = self.post('/areas/delete', product_area)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for valid data
        product_area = {'id': storage.get_product_area()['id']}
        r = self.post('/areas/delete', product_area)
        self.assertEquals(r.status_code, 200)
        self.assertTrue(isinstance(r.json(), list))
        product_area_id = None
        for area in r.json():
            if int(area['id']) == int(storage.get_product_area()['id']):
                product_area_id = area['id']
        self.assertFalse(bool(product_area_id))

    def test_19_remove_client(self):
        """
        Test for removing client. Sends request to the back-end
        with empty data, invalid client id, and checks the
        response for the status code and existing error
        message. Then sends request with valid client id

        :return void:
        """
        # test case for empty data
        client = {}
        r = self.post('/clients/delete', data=client)
        self.assertEqual(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for invalid client id
        client = {'id': []}
        r = self.post('/clients/delete', data=client)
        self.assertEqual(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for client id not existing
        client = {'id': 0}
        r = self.post('/clients/delete', data=client)
        self.assertEqual(r.status_code, 200)
        self.assertTrue('error' in r.json())

        # test case for valid client id
        client_ids = [int(cl['id']) for cl in storage.get_client()]
        for client_id in client_ids:
            client = {'id': client_id}
            r = self.post('/clients/delete', data=client)
            self.assertEqual(r.status_code, 200)
            self.assertFalse('error' in r.json())

        # make sure that all clients were removed
        for client in r.json():
            self.assertFalse(int(client['id']) in client_ids)

    def test_20_remove_user_profile(self):
        """
        Test for removing user from database. Sends query
        with user credentials to back-end, and checks
        in response data status code, info message.

        :return void:
        """
        # remove user
        r = self.post('/profile/remove', data={})
        self.assertEquals(r.status_code, 200)
        self.assertTrue('info' in r.json())
        req_session.auth = (CREDENTIALS['email'],
                            CREDENTIALS['password'])

        # make sure that user was removed
        r = self.post('/token', data={})
        self.assertEquals(r.status_code, 401)

        # reset storage
        storage.set_client(None)
        storage.set_product_area(None)
        storage.set_token(None)
        storage.set_user(None)
        storage.set_cookies(None)
        storage.set_csrf(None)
        storage.set_request(None)


class TestFunctions(TestCase):
    """
    Tests for resource.py
    """
    def test_01_get_unique_str(self):
        """
        Test for get_unique_str function. Checks that
        function returns a string, and length of the
        string equals parameter amount that was pass
        to the function.

        :return void:
        """

        amount = 34

        # test get_unique_string function
        result = get_unique_str(amount)
        self.assertTrue(isinstance(result, basestring))
        self.assertTrue(len(result) == amount)

        # make sure that the function return unique string
        self.assertNotEquals(get_unique_str(amount), get_unique_str(amount))

    def test_02_is_index(self):
        """
        Test for is_index function. Check function with
        invalid data like string, list, dictionary, tuple,
        None, False, or 0 (that cannot be an index).

        Then test function with valid data like an
        integer or an integer in string format.

        :return void:
        """
        self.assertFalse(is_index('a'))
        self.assertFalse(is_index([1]))
        self.assertFalse(is_index({1: 1}))
        self.assertFalse(is_index((0,)))
        self.assertFalse(is_index(None))
        self.assertFalse(is_index(False))
        self.assertFalse(is_index(0))
        self.assertTrue(is_index(1))
        self.assertTrue(is_index("1"))

    def test_03_convert_date(self):
        """
        Test for convert_date function.

        :return void:
        """
        import datetime as date_type
        self.assertTrue(isinstance(convert_date('04/04/2000'), date_type.date))
        self.assertEquals(str(convert_date('04/04/2000')), '2000-04-04')

    def test_04_validator(self):
        """
        Test for validator function. Checks function with
        data types like: string, list, dict, tuple. First
        test with wrong length, second test with invalid
        data type, third test with valid data.

        :return void:
        """

        # test case for too short string
        self.assertFalse(validator('abcd', basestring, 5))

        # test case invalid string
        self.assertFalse(validator([1, 2, 3, 4], basestring, 3))

        # test case valid string
        self.assertTrue(validator('abcd', basestring, 3))

        # test case for too short list
        self.assertFalse(validator([1, 2, 3, 4], list, 5))

        # test case invalid list
        self.assertFalse(validator((1, 2, 3, 4), list, 3))

        # test case valid list
        self.assertTrue(validator([1, 2, 3, 4], list, 3))

        # test case for too short dictionary
        self.assertFalse(validator({'a': 'a', 'b': 'b'}, dict, 5))

        # test case invalid dictionary
        self.assertFalse(validator("{'a': 'a', 'b': 'b'}", dict, 1))

        # test case valid dictionary
        self.assertTrue(validator({'a': 'a', 'b': 'b'}, dict, 1))

        # test case for too short tuple
        self.assertFalse(validator((1, 2, 3, 4), tuple, 5))

        # test case invalid tuple
        self.assertFalse(validator([1, 2, 3, 4], tuple, 5))

        # test case valid tuple
        self.assertTrue(validator((1, 2, 3, 4), tuple, 3))


class TestDatabaseFunctions(TestCase):
    """
    Tests for database functions from data_provider.py
    """

    def test_01_create_user(self):
        """
        Test for create_user function. Checks in returning
        data that user was saved, and data is a dictionary.


        :return void:
        """
        user = create_user(email=CREDENTIALS['email'],
                           password=CREDENTIALS['password'],
                           first_name=CREDENTIALS['first_name'],
                           last_name=CREDENTIALS['last_name']
                           ).serialize

        # test result
        self.assertTrue(isinstance(user, dict))
        self.assertEquals(user['email'], CREDENTIALS['email'])
        self.assertEquals(user['first_name'], CREDENTIALS['first_name'])
        self.assertEquals(user['last_name'], CREDENTIALS['last_name'])

        # save user
        storage.set_user(user)

    def test_02_get_user_by_id(self):
        """
        Test for get_user_by_id function. Checks returning data
        that user is not None, user from database equal with
        user from the storage.

        Additionally test the function with invalid user id.

        :return void:
        """
        # retrieve user from storage and pass uid to get_user_by_id function
        user = get_user_by_id(storage.get_user()['uid']).serialize

        # test result
        self.assertTrue(bool(user))
        self.assertEquals(user, storage.get_user())
        self.assertFalse(get_user_by_id(0))

    def test_03_get_user_by_email(self):
        """
        Test for get_user_by_email function.

        :return void:
        """
        user = get_user_by_email(storage.get_user()['email']).serialize

        # test result
        self.assertTrue(bool(user))
        self.assertEquals(user, storage.get_user())
        self.assertFalse(get_user_by_id(0))

    def test_04_update_user(self):
        """
        Tests for updating user. Pass new user info to the
        function, and makes sure that all info was saved
        correctly.

        :return void:
        """
        # update user info
        user = {
            'uid': storage.get_user()['uid'],
            'password': 'new_password',
            'email': 'new@email.com',
            'first_name': 'John',
            'last_name': 'Doe'
        }

        # get result
        new_user_info = update_user(user)

        # serialize result
        serialize_user = new_user_info.serialize

        # data test
        self.assertEquals(serialize_user['email'], user['email'])
        self.assertEquals(serialize_user['first_name'], user['first_name'])
        self.assertEquals(serialize_user['last_name'], user['last_name'])
        self.assertTrue(new_user_info.verify_password(user['password']))

        # save user
        storage.set_user(serialize_user)

    def test_05_remove_user(self):
        """
        Test to make sure user was removed.

        :return void:
        """

        # remove user
        remove_user(storage.get_user()['uid'])

        # make sure that user was removed
        self.assertFalse(get_user_by_id(storage.get_user()['uid']))

    def test_06_create_client(self):
        """
        Tests create_client function, creates a client,
        and check that client was saved, creates another
        client and saves result.

        :return void:
        """

        # create a client
        client = create_client("Client name").serialize

        # test result
        self.assertEquals(client['name'], "Client name")

        # create another client and save result
        clients = list()
        clients.append(client)
        clients.append(create_client("new Client").serialize)
        storage.set_client(clients)

    def test_07_get_clients(self):
        """
        Test for get_client function. Calls function, tests
        if list has at least one result.

        :return void:
        """
        client_list = storage.get_client()

        self.assertTrue(isinstance(client_list, list))
        self.assertTrue(len(client_list) > 0)

    def test_08_update_client(self):
        """
        Test for update_client function, changes client
        name and passes name to the function. Then, checks
        that result type is a list, retrieves, client from
        the result and saves clients.

        :return void:
        """

        first_client = dict(storage.get_client()[0])
        second_client = storage.get_client()[1]
        first_client['name'] = "updated Client name"
        client_list = update_client(first_client)

        self.assertTrue(isinstance(client_list, list))

        # retrieve client from result
        new_client = None
        for item in client_list:
            if int(item['id']) == first_client['id']:
                new_client = item

        self.assertEquals(new_client['name'], first_client['name'])

        # save clients
        clients = list()
        clients.append(first_client)
        clients.append(second_client)
        storage.set_client(clients)

    def test_09_client_exist(self):
        """
        Test for client_exist function.

        :return void:
        """
        self.assertFalse(client_exist(0))
        self.assertTrue(int(storage.get_client()[0]['id']))

    def test_10_create_product_area(self):
        """
        Test for create_product_area function. Pass the
        function product area name and checks that the
        product area was saved.

        :return void:
        """

        product_area = create_product_area("new product area").serialize
        self.assertEquals(product_area['name'], "new product area")
        storage.set_product_area(product_area)

    def test_11_get_product_areas(self):
        """
        Test for get_product_areas function. Call
        get_product_area function and makes sure that
        result is a list with at least one element.

        :return void:
        """

        product_areas = get_product_areas()
        self.assertTrue(isinstance(product_areas, list))
        self.assertTrue(len(product_areas) > 0)

        temp_product_area = None
        for product_area in product_areas:
            if product_area['name'] == storage.get_product_area()['name']:
                temp_product_area = product_area

        self.assertTrue(temp_product_area)

    def test_12_product_area_exist(self):
        """
        Test for product_are_exist function. Check two
        cases: one with valid data, one with invalid data.
        Checks that function returns valid boolean response.

        :return void:
        """

        self.assertTrue(product_area_exist(storage.get_product_area()['id']))
        self.assertFalse(product_area_exist(0))

    def test_13_update_product_area(self):
        """
        Test for update_product_area function. Changes
        product area name and passes to the function and
        makes sure that result is a list with at least one
        element. Then, checks that product area name was
        updated and saves product area to the storage.

        :return void:
        """

        product_area = storage.get_product_area()
        product_area['name'] = "updated product area"
        product_areas_list = update_product_area(product_area)
        self.assertTrue(isinstance(product_areas_list, list))
        self.assertTrue(len(product_areas_list) > 0)
        temp_product_area = None
        for item in product_areas_list:
            if item['name'] == product_area['name']:
                temp_product_area = item

        self.assertTrue(bool(temp_product_area))
        self.assertEquals(temp_product_area['name'], product_area['name'])

        storage.set_product_area(temp_product_area)

    def test_14_get_requests(self):
        """
        Test get_requests function. Get list of product
        areas, and checks that result is a list that has
        at least one element.

        :return void:
        """
        product_areas_list = get_requests()
        self.assertTrue(isinstance(product_areas_list, list))
        self.assertTrue(len(product_areas_list) > 0)

    def test_15_create_request(self):
        """
        Test for create_request function. Defines request
        data, and passes this data to the function. Then
        retrieve the request from the list and tests for
        returned request. Creates two more requests for
        the next functions and saves them.

        :return void:
        """

        # define request data
        request = {
            'title': 'new request',
            'description': 'description of new request',
            'client': storage.get_client()[0]['id'],
            'client_priority': 2,
            'target_date': date(2018, 06, 16),
            'product_area': storage.get_product_area()['id']
        }

        # get result
        requests_list = create_request(request)

        # retrieve the request from the list
        temp_request = None
        for item in requests_list:
            if item['title'] == request['title']:
                temp_request = item

        # tests for returned request
        self.assertTrue(bool(temp_request))
        self.assertEquals(temp_request['title'], request['title'])
        self.assertEquals(temp_request['description'], request['description'])
        self.assertEquals(temp_request['client']['name'],
                          storage.get_client()[0]['name'])
        self.assertEquals(temp_request['client_priority'],
                          request['client_priority'])
        self.assertEquals(temp_request['product_area'],
                          storage.get_product_area())

        # create two more requests
        second_request = {
            'title': 'second request',
            'description': 'description of second request',
            'client': storage.get_client()[0]['id'],
            'client_priority': 1,
            'target_date': date(2018, 06, 16),
            'product_area': storage.get_product_area()['id']
        }
        create_request(second_request)
        third_request = {
            'title': 'third request',
            'description': 'description of third request',
            'client': storage.get_client()[1]['id'],
            'client_priority': 1,
            'target_date': date(2018, 06, 16),
            'product_area': storage.get_product_area()['id']
        }
        requests_list = create_request(third_request)

        first_request = None

        # retrieve requests from the requests list
        for item in requests_list:
            if item['title'] == temp_request['title']:
                first_request = item
            if item['title'] == second_request['title']:
                second_request = item
            if item['title'] == third_request['title']:
                third_request = item

        # tests for requests
        self.assertEquals(first_request['client_priority'], 2)
        self.assertEquals(second_request['client_priority'], 1)
        self.assertEquals(third_request['client_priority'], 1)

        # save requests in the storage
        requests = list()
        requests.append(first_request)
        requests.append(second_request)
        requests.append(third_request)
        storage.set_request(requests)

    def test_16_update_request(self):
        """
        Test for update_request function. Retrieves request
        from the storage and updates information for the first
        request, and passes to the function. Then, gets list
        for requests and makes sure data was updated.

        :return void:
        """
        # get requests
        first_request = storage.get_request()[0]
        second_request = storage.get_request()[1]
        third_request = storage.get_request()[2]

        # update request data
        request = {
            'id': int(first_request['id']),
            'title': 'updated request title',
            'description': 'updated description',
            'client': storage.get_client()[1]['id'],
            'client_priority': 3,
            'target_date': date(year=2018, month=6, day=26),
            'product_area': storage.get_product_area()['id']
        }

        # get requests
        requests = update_request(request)

        # retrieve requests from the requests list
        for item in requests:
            if item['id'] == request['id']:
                first_request = item
            if item['id'] == second_request['id']:
                second_request = item
            if item['id'] == third_request['id']:
                third_request = item

        self.assertTrue(bool(first_request))
        self.assertEquals(first_request['title'], request['title'])
        self.assertEquals(first_request['description'], request['description'])
        self.assertEquals(first_request['client']['id'], request['client'])
        self.assertEquals(first_request['client_priority'],
                          request['client_priority'])
        self.assertEquals(first_request['product_area'],
                          storage.get_product_area())

        # make sure that update function change client priority
        self.assertEquals(first_request['client_priority'], 3)
        self.assertEquals(second_request['client_priority'], 1)
        self.assertEquals(third_request['client_priority'], 1)

    def test_17_client_priority_is_taken(self):
        """
        Test for client_priority_is_taken function. Passes valid
        and invalid to check if data exists or not.

        :return void:
        """
        data = {
            'client': storage.get_client()[0]['id'],
            'client_priority': 1
        }
        self.assertTrue(client_priority_is_taken(data))
        data['client_priority'] = 2
        self.assertFalse(client_priority_is_taken(data))

    def test_18_update_client_priorities(self):
        """
        Test for update_client_priorities function. Checks
        that client priority is taken, updates client priority,
        makes sure that client priority is free.

        :return void:
        """
        # prepare data
        data = {
            'client': storage.get_client()[0]['id'],
            'client_priority': 1
        }

        # make sure that client priority is taken
        self.assertTrue(client_priority_is_taken(data))

        # update client priority
        update_client_priorities(data)

        # make sure that client priority is free
        self.assertFalse(client_priority_is_taken(data))
