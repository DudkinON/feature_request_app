#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from app.secrets.keys import database

app_host = '0.0.0.0'
app_port = 5000
app_debug = True

BASE_DIR = path.dirname(path.realpath(__file__))
SECRETS_DIR = ''.join([BASE_DIR, '/secrets'])

# use database PostgreSQL if False will use SQLite
POSTGRES = False

CONNECT_SETTINGS = 'postgresql://%s:%s@%s/%s' % database

# SQLite configuration
DB_FILE_NAME = 'request.db'  # define SQLite database file name

SAME_THREAD = False  # set SQLite for checking same thread

# Test settings

HOST = 'http://%s:%s' % (app_host, app_port)
CREDENTIALS = {'email': 'test@test.com',
               'first_name': 'test',
               'last_name': 'test',
               'password': 'test'}
