#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_httpauth import HTTPBasicAuth

from data_provider import *
from settings import SECRETS_DIR, app_host, app_port, app_debug
from resource import get_unique_str, is_index
from secrets import keys

# define global variables
app = Flask(__name__)
app.secret_key = keys.secret_key
auth = HTTPBasicAuth()


if __name__ == '__main__':
    app.debug = app_debug
    app.run(host=app_host, port=app_port)
