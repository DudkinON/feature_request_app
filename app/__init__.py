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

        if not bool(data):
            return jsonify({'error': "Server does not get any data"}), 200

        user_request = dict()

        def field_validation(field):
            """
            Checks the field on existing, not too short and is a string.

            :param field: string
            :return object:
            """
            if not data.get(field):
                return False

            if len(data.get(field)) < 3:
                return False

            if not isinstance(data.get(field), basestring):
                return False

            return True

        # validate fields
        if not field_validation("title"):
            return jsonify({'error': "Invalid title"}), 200
        if not field_validation("description"):
            return jsonify({'error': "Invalid description"}), 200
        if not field_validation("target_date"):
            return jsonify({'error': "Invalid target date"}), 200

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
    """
    Return auth token

    :return string: JSON
    """
    token = g.user.generate_auth_token().decode('ascii')
    return jsonify({'token': token, 'user': g.user.serialize}), 200


# TODO: Sign in with provider
@app.route('/oauth/<provider>', methods=['POST'])
@csrf_protection
def login(provider):
    """
        Connect with third-party providers and authorize a user.
        If third-party provider returned a user data to back-end
        get the user info from the database, if the user does not
        exist create a new user.

        If a third-party provider returns an error, sends a
        message with error description

        If the third-party provider does not exist, sends a
        message with error description


    :param provider: A string title of provider
    :return: a user info if authorization success else error message
    """
    # Parse the auth code
    data = request.get_json()

    if provider == 'google':
        # Exchange for a token
        try:
            client_secrets = ''.join([SECRETS_DIR, '/client_secrets.json'])
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets(client_secrets, scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(data.get("code"))
        except FlowExchangeError:
            return jsonify({'error': 'Authorization failed'}), 200

        # Check that the access token is valid.
        access_token = credentials.access_token
        gurl = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        url = (gurl % access_token)
        h = Http()
        result = loads(h.request(url, 'GET')[1])

        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        # Get user info
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = r_get(user_info_url, params=params)

        data = answer.json()

        # see if user exists, if it doesn't make a new one
        user = get_user_by_email(email=data['email'])
        if not user:
            user = create_user(email=data.get('email'),
                               first_name=data.get('given_name'),
                               last_name=data.get('family_name'),
                               password=get_unique_str(8))

        g.user = user
        login_session['uid'] = user.id
        login_session['provider'] = provider

        # Make token
        token = g.user.generate_auth_token()

        # Send back token to the client
        return jsonify({'token': token.decode('ascii'),
                        'user': g.user.serialize}), 200

    else:
        return jsonify({'error': 'Unknown provider'}), 200


@app.route('/logout', methods=['POST'])
@csrf_protection
@auth.login_required
def user_logout():
    """
    Logged out user, remove session, and send logout message
    back to front-end

    :return:
    """

    if 'uid' in login_session:
        del login_session['uid']

    if 'provider' in login_session:
        del login_session['provider']

    if not g.user:
        return jsonify({'error': "You are already logged out"}), 200

    g.user = None
    return jsonify({'info': "You are now logged out"}), 200


@app.route('/profile/update', methods=['POST'])
@csrf_protection
@auth.login_required
def update_user_profile():
    """
    Update a user profile

    :return: success or error message in JSON format
    """

    # get JSON data
    data = request.get_json()

    user = get_user_by_email(data.get('email'))
    if user and data.get('email') != g.user.email:
        return jsonify({'error': 'This email is already registered'})

    # get user info
    user = data.get('user')

    usr = dict()
    usr['uid'] = g.user.id
    if user:
        usr['email'] = user.get('email')
        usr['first_name'] = user.get('first_name')
        usr['last_name'] = user.get('last_name')

    usr['password'] = data.get('password')
    user = update_user(usr)

    # add user to global
    g.user = user
    return jsonify(user.serialize), 200


@app.route('/profile/remove', methods=['POST'])
@csrf_protection
@auth.login_required
def remove_user_profile():

    remove_user(g.user.id)
    g.user = None

    # clean login session
    if 'uid' in login_session:
        del login_session['uid']

    if 'provider' in login_session:
        del login_session['provider']

    return jsonify({'info': 'Profile was removed'})

if __name__ == '__main__':
    app.debug = app_debug
    app.run(host=app_host, port=app_port)
