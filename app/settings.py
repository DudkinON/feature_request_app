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

CONNECT_SETTINGS = 'postgresql://%s:%s@%s/%s' % (database.get('user'),
                                                 database.get('password'),
                                                 database.get('host'),
                                                 database.get('database'))

# SQLite configuration
DB_FILE_NAME = 'request.db'  # define SQLite database file name

SAME_THREAD = False  # set SQLite for checking same thread

# Test settings

HOST = 'http://127.0.0.1:5000'
CREDENTIALS = {'email': 'test@test.com',
               'first_name': 'test',
               'last_name': 'test',
               'password': 'test'}
