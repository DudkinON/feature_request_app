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
from resource import get_unique_str, is_index
from secrets import keys

# define global variables
app = Flask(__name__)
app.secret_key = keys.secret_key
auth = HTTPBasicAuth()


def login_required(f):
    """
    Checking the user is logged in

    :param f: function
    :return: function if user legged in else send error in JSON format
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
    :return: function if csrf tokens are match else send error in JSON format
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


if __name__ == '__main__':
    app.debug = app_debug
    app.run(host=app_host, port=app_port)
