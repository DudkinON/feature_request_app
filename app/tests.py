#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from settings import HOST, CREDENTIALS
from requests import Session
from re import search
from json import dumps


req_session = Session()


class Storage(object):
    pass
