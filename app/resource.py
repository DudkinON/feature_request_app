#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice
from string import ascii_uppercase as uppercase, digits
from datetime import date, datetime
import re


def get_unique_str(amount):
    """
    Return a unique string

    :param amount: (int)
    :return string:
    """
    return ''.join(choice(uppercase + digits) for x in xrange(amount))


def is_index(index):
    """
    Check that value is an integer and more than 0

    :param index: integer
    :return: boolean
    """
    if isinstance(index, (int, long)):
        return index > 0

    if not isinstance(index, basestring):
        return False

    try:
        return True if int(index) > 0 else False
    except ValueError:
        return False
