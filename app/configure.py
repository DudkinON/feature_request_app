#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import path
from settings import SAME_THREAD, CONNECT_SETTINGS
from sqlalchemy.ext.declarative import declarative_base
from settings import POSTGRES, DB_FILE_NAME

Base = declarative_base()
cur_dir = path.dirname(path.abspath(__file__))
SQLite = 'sqlite:///%s%s'

if not SAME_THREAD:
    cst = '?check_same_thread=False'
else:
    cst = '?check_same_thread=True'

if POSTGRES:
    DB_SETTINGS = CONNECT_SETTINGS
else:
    DB_SETTINGS = SQLite % (path.join(cur_dir, DB_FILE_NAME), cst)
