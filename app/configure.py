#!/usr/bin/env python
# -*- coding: utf-8 -*-

from settings import SAME_THREAD, DB_FILE_NAME, CONNECT_SETTINGS, POSTGRES

SQLite_CONF = 'sqlite:///%s' % DB_FILE_NAME

if not SAME_THREAD:
    SQLite_CONF += '?check_same_thread=False'
else:
    SQLite_CONF += '?check_same_thread=True'

if POSTGRES:
    DB_SETTINGS = CONNECT_SETTINGS
else:
    DB_SETTINGS = SQLite_CONF
