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


@app.before_request
def before_request():
    """
    Update global user

    :return void:
    """
    if 'uid' in login_session:
        g.user = get_user_by_id(login_session['uid'])
    else:
        g.user = None


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
        user = get_user_by_email(_login.lower())
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
    login_session['uid'] = int(g.user.id)
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
            client_secrets = ''.join([SECRETS_DIR,
                                      '/client_secrets.json'])
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
    if 'user' in g:
        usr['uid'] = g.user.id
    elif 'uid' in login_session:
        usr['uid'] = login_session['uid']

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
    """
    Remove user from database

    :return String: (JSON)
    """
    user = dict(g.user.serialize)
    g.user = None
    remove_user(user['uid'])

    # clean login session
    if 'uid' in login_session:
        del login_session['uid']

    if 'provider' in login_session:
        del login_session['provider']

    return jsonify({'info': 'Profile was removed'})


@app.route('/clients/new', methods=['POST'])
@csrf_protection
@auth.login_required
def new_client():
    """
    Validate input data, if it invalid sends message
    to front-end. Create a new client in database

    :return String: (JSON)
    """
    # get JSON data
    data = request.get_json()

    if not data.get("name"):
        return jsonify({'error': 'Name of client is empty'}), 200

    if isinstance(data.get('name'), (int, long)):
        return jsonify({'error': 'Client cannot to be an integer'})

    if len(data.get("name")) < 3:
        return jsonify({'error': 'Client name is too short'})

    create_client(name=clean(data.get("name")))

    return jsonify(get_clients()), 200


@app.route('/clients/edit', methods=['POST'])
@csrf_protection
@auth.login_required
def update_client_info():
    """
    Get json from front-end, clean data, update a client record in
    database and return list of clients in JSON format

    :return: string (JSON)
    """

    # get JSON data
    data = request.get_json()

    # validate client name
    if not validator(data.get("name"), basestring, 3):
        return jsonify({'error': "Client name is invalid"})

    # clean input data
    if is_index(data.get('id')):
        data['id'] = int(data.get('id'))
    else:
        return jsonify({'error': 'The id of client is not integer'}), 200

    data['name'] = clean(data.get('name'))

    # check client exist
    if client_exist(data['id']):
        # return list of clients
        return jsonify(update_client(data)), 200
    else:
        return jsonify({'error': "Can't find this client"}), 200


@app.route('/clients/delete', methods=['POST'])
@csrf_protection
@auth.login_required
def delete_client():
    """
    Remove a client from database

    :return: string (JSON)
    """
    # get JSON data
    data = request.get_json()

    # clean input data
    if is_index(data.get('id')):
        data['id'] = int(data.get('id'))
    else:
        return jsonify({'error': "Cannot define client id"}), 200

    # check client exist
    if not client_exist(data['id']):
        return jsonify({'error': "The client does not exist"}), 200

    # check that every request does not use current client
    if check_client_relation(data['id']):
        msg = "This client is currently being used in this requests"
        return jsonify({'error': msg}), 200

    return jsonify(remove_client(data['id'])), 200


@app.route('/clients')
@csrf_protection
@auth.login_required
def get_all_clients():
    """
    Return all request in JSON

    :return String: (JSON)
    """
    return jsonify(get_clients()), 200


@app.route('/areas/new', methods=['POST'])
@csrf_protection
@auth.login_required
def new_product_area():
    """
    Get data from the back-end and validate and clean
    the name of the product area. If data is invalid,
    return error to front-end, else create a new
    product area

    :return string: (JSON)
    """
    # get JSON data
    data = request.get_json()

    # check input data
    if not data.get("name"):
        return jsonify({'error': 'Name of product area is empty'}), 200

    if len(data.get("name")) < 3:
        return jsonify({'error': 'Product area name is too short'})

    if isinstance(data.get('name'), (int, long)):
        return jsonify({'error': 'Product area can not be an integer'})

    # create product area
    create_product_area(name=clean(data.get("name")))

    # return list of areas
    return jsonify(get_product_areas()), 200


@app.route('/areas/edit', methods=['POST'])
@csrf_protection
@auth.login_required
def update_product_area_info():
    """
    Get json from front-end, clean data, update a product
    area record in database and return list of product
    areas in JSON format

    :return: string (JSON)
    """

    # get JSON data
    data = request.get_json()

    # clean input data
    if not validator(data.get("name"), basestring, 3):
        return jsonify({'error': 'Product area name is invalid'}), 200
    if not is_index(data.get('id')):
        msg = 'The id of product area is not an integer'
        return jsonify({'error': msg}), 200
    data['id'] = int(data.get('id'))
    data['name'] = clean(data.get('name'))

    # check product area exist
    if not product_area_exist(data['id']):
        return jsonify({'error': "Can't find this product area"}), 200

    # return list of clients
    return jsonify(update_product_area(data)), 200


@app.route('/areas/delete', methods=['POST'])
@csrf_protection
@auth.login_required
def delete_product_area():
    """
    Remove product area from database

    :return: string (JSON)
    """
    # get JSON data
    data = request.get_json()

    # clean input data
    if is_index(data.get('id')):
        data['id'] = int(data.get('id'))
    else:
        msg = 'The id of product area is not an integer'
        return jsonify({'error': msg}), 200

    # check product area exist
    if not product_area_exist(data['id']):
        return jsonify({'error': "The product area does not exist"}), 200

    # check that current product area id isn't being used already in request
    if check_product_area_relation(data['id']):
        msg = "This product area is currently being used in a request(s)"
        return jsonify({'error': msg}), 200

    return jsonify(remove_product_area(data['id'])), 200


@app.route('/areas')
@csrf_protection
@auth.login_required
def get_all_product_areas():
    """
    Return all requests in JSON format

    :return String: (JSON)
    """
    return jsonify(get_product_areas()), 200


@app.route('/requests/new', methods=['POST'])
@csrf_protection
@auth.login_required
@check_request
def new_request():
    """
    Get the request data from the front-end end and process the
    data.

    If data does exist, clean each value from danger characters
    then if client priority is taken update each request in the
    database and save a new request with the current value of
    client priority.

    Returns or list of requests or error message in JSON format

    :return object or string:
    """
    # get user request
    user_request = g.user_request

    # check that client priority is not taken
    if client_priority_is_taken(user_request):
        # else shift all requests where client priority >= current priority
        update_client_priorities(user_request)

    # clean RAM
    del g.user_request

    # send list of requests to front-end
    return jsonify(create_request(user_request)), 200


@app.route('/requests/edit', methods=['POST'])
@csrf_protection
@auth.login_required
@check_request
def update_request_info():
    """
    Update the given request and return list of requests

    :return String: (JSON)
    """
    request_id = request.get_json().get('id')
    user_request = g.user_request

    if not is_index(request_id):
        return jsonify({'error': "Cannot read request id"}), 200

    user_request['id'] = int(request_id)

    if not request_exist(request_id):
        return jsonify({'error': "Cannot find the request"}), 200

    if client_priority_is_taken(user_request):
        update_client_priorities(user_request)

    # clean RAM
    del g.user_request

    return jsonify(update_request(user_request)), 200


@app.route('/requests/delete', methods=['POST'])
@csrf_protection
@auth.login_required
def remove_request_info():
    """
    Remove request from database

    :return String: (JSON)
    """

    # get data
    data = request.get_json()

    if not data:
        return jsonify({'error': "Server does not get any data"}), 200

    if not data.get('id'):
        return jsonify({'error': "Server does not get request info"}), 200

    if not is_index(data.get('id')):
        return jsonify({'error': "Id of request invalid"}), 200

    if not request_exist(data.get('id')):
        return jsonify({'error': 'Cannot find the request'}), 200

    return jsonify(remove_request(data.get("id"))), 200


@app.route('/requests/complete', methods=['POST'])
@csrf_protection
@auth.login_required
def complete_the_request():
    """
    Mark the request as complete

    :return String: (JSON)
    """
    # get data
    data = request.get_json()

    if not data:
        return jsonify({'error': "Server does not get any data"}), 200

    if not data.get('id'):
        return jsonify({'error': "Server does not get request id"}), 200

    if not is_index(data.get('id')):
        return jsonify({'error': "Invalid request id"}), 200

    request_id = int(data.get('id'))

    if not request_exist(request_id):
        return jsonify({'error': "Cannot find the request"}), 200

    return jsonify(completed_request(request_id)), 200


@app.route('/requests')
@csrf_protection
@auth.login_required
def get_all_requests():
    """
    Return all request in JSON format

    :return String: (JSON)
    """
    return jsonify(get_requests()), 200


@app.route('/requests/get/completed')
@csrf_protection
@auth.login_required
def get_all_completed_requests():
    """
    Return all completed requests in JSON format

    :return String: (JSON)
    """
    return jsonify(get_completed_requests()), 200


if __name__ == '__main__':
    app.debug = app_debug
    app.run(host=app_host, port=app_port)
