#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import path
from settings import SAME_THREAD, DB_FILE_NAME, CONNECT_SETTINGS, POSTGRES
from secrets.keys import secret_key


cur_dir = path.dirname(path.abspath(__file__))
SQLite = 'sqlite:///%s%s'

if not SAME_THREAD:
    cst = '?check_same_thread=False'
else:
    cst = '?check_same_thread=True'

if POSTGRES:
    DB_SETTINGS = CONNECT_SETTINGS
else:
    DB_SETTINGS = SQLite


class SQLiteConfig(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = secret_key
    SQLALCHEMY_DATABASE_URI = SQLite % (path.join(cur_dir, DB_FILE_NAME), cst)
    SQLALCHEMY_ECHO = False


class SQLiteConfigTest(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = secret_key
    SQLALCHEMY_DATABASE_URI = SQLite % (path.join(cur_dir, 'test.db'), cst)
    SQLALCHEMY_ECHO = False


class PostgreSQLConfig(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = secret_key
    PostgreSQL_DATABASE = CONNECT_SETTINGS
    SQLALCHEMY_ECHO = False
