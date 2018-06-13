#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, g, make_response, request, Response, \
    render_template as render, session as login_session
from httplib2 import Http
from flask_httpauth import HTTPBasicAuth
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from json import dumps, loads
from requests import get as r_get
from functools import wraps
from bleach import clean

from data_provider import *
from settings import SECRETS_DIR, app_host, app_port, app_debug
from resource import get_unique_str, is_index, convert_date, validator
from secrets import keys

# define global variables
app = Flask(__name__)
app.secret_key = keys.secret_key
auth = HTTPBasicAuth()


def login_required(f):
    """
    Checking to see if the user is logged in

    :param f: function
    :return: function if user logged in else send error in JSON format
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        # login detection
        if 'uid' in login_session:
            return f(*args, **kwargs)
        else:
            message = 'You are not allowed to access there'
            return jsonify({'error', message}), 200

    return decorated_function


def csrf_protection(f):
    """
    CSRF protection

    :param f: function
    :return: function if csrf tokens are matched else send error in JSON format
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        # CSRF protection
        if not request.args.get('csrf') == login_session.get('csrf_token'):
            return jsonify({'error': 'The attack of CSRF was prevented'}), 200
        else:
            return f(*args, **kwargs)

    return decorated_function


# TODO: Verification of password
@auth.verify_password
def verify_password(_login, password):
    """
    Verification of password

    :param _login: string
    :param password: string
    :return bool:
    """

    # Try to see if it's a token first
    user_id = User.verify_auth_token(_login)
    if user_id:
        user = get_user_by_id(user_id)
    else:
        # if not try to find a user by email
        user = get_user_by_email(_login)
        if not user:
            return False
        else:
            if not user.verify_password(password):
                return False
    g.user = user
    return True


def check_request(f):
    """
    Check validity of fields and clean data from the front-end
    if date is not valid return error to front-end else save
    cleaned data to global variable g and return decorated
    function

    :param f: function
    :return mix:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        # get JSON data
        data = request.get_json()

        user_request = dict()

        def field_validation(field):
            """
            Checks the field on existing, not too short and not an integer.

            :param field: string
            :return object:
            """
            if not data.get(field):
                return jsonify(
                    {'error': '%s is empty' % field.capitalize()}), 200

            if len(data.get(field)) < 3:
                return jsonify(
                    {'error': '%s is too short' % field.capitalize()})

            if isinstance(data.get(field), (int, long)):
                msg = "$s can not be an integer" % field.capitalize()
                return jsonify({'error': msg})

        # validate fields
        field_validation("title")
        field_validation("description")
        field_validation("target_date")

        # define fields
        user_request["title"] = clean(data.get("title"))
        user_request["description"] = clean(data.get("description"))
        user_request["client"] = None
        user_request["product_area"] = None
        user_request["client_priority"] = None
        user_request["target_date"] = convert_date(data.get("target_date"))

        if user_request["target_date"] is None:
            return jsonify({'error': "The date has the wrong format"}), 200

        client = data.get("client")
        if client and is_index(client.get("client_priority")):
            user_request['client_priority'] = int(
                client.get("client_priority"))
        else:
            return jsonify(
                {'error': "Client priority has to be an integer"}), 200

        if client and is_index(client.get("id")):
            user_request["client"] = int(client.get("id"))
        else:
            return jsonify({'error': "Client id has to be an integer"})

        product_area = data.get("product_area")

        if product_area and is_index(product_area.get('id')):
            user_request["product_area"] = int(product_area.get('id'))
        else:
            return jsonify(
                {'error': "Product area id has to be an integer"}), 200

        if not client_exist(user_request["client"]):
            return jsonify({'error': "The client is not found"}), 200

        if not product_area_exist(user_request["product_area"]):
            return jsonify({'error': "The product area is not found"}), 200

        g.user_request = user_request

        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def front_end():
    """
    Front-end template

    :return: a rendered HTML template
    """
    csrf_token = get_unique_str(36)
    login_session['csrf_token'] = csrf_token
    return render("index.html", csrf=csrf_token)


# TODO: User registration
@app.route('/registration', methods=['POST'])
@csrf_protection
def registration():
    """
    Get data from front-end and validate and clean data
    If data is invalid, send error to front-end, else
    create a new user

    :return string: JSON format
    """
    # get JSON data
    data = request.get_json()

    # Check that data values are not integers
    if isinstance(data.get('email'), (int, long)):
        return jsonify({'error': 'Email cannot to be an integer'})

    if isinstance(data.get('first_name'), (int, long)):
        return jsonify({'error': 'First name cannot be an integer'})

    if isinstance(data.get('last_name'), (int, long)):
        return jsonify({'error': 'Last name cannot be an integer'})

    if isinstance(data.get('password'), (int, long)):
        return jsonify({'error': 'Password cannot be an integer'})

    # prepare data
    usr = dict()
    usr['email'] = clean(data.get('email'))
    usr['first_name'] = clean(data.get('first_name'))
    usr['last_name'] = clean(data.get('last_name'))
    usr['password'] = data.get('password')

    # Check email is not register
    if get_user_by_email(usr['email']):
        return jsonify({'error': 'Sorry, this email is taken'})

    # create a new user
    user = create_user(email=usr['email'],
                       password=usr['password'],
                       first_name=usr['first_name'],
                       last_name=usr['last_name'])

    # Add user to the session
    login_session['uid'] = user.id

    # Add user to global
    g.user = user

    # generate a token
    token = g.user.generate_auth_token().decode('ascii')

    # send data to front-end
    return jsonify({'token': token, 'user': g.user.serialize}), 200


@app.route('/token', methods=['POST'])
@auth.login_required
def get_auth_token():

    token = g.user.generate_auth_token().decode('ascii')
    return jsonify({'token': token, 'user': g.user.serialize}), 200

if __name__ == '__main__':
    app.debug = app_debug
    app.run(host=app_host, port=app_port)
