#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice
from string import ascii_uppercase as uppercase, digits
from datetime import date
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


def convert_date(date_string):
    """
    Convert string format 'mm/dd/yyyy' to date

    :param date_string: string
    :return mix:
    """
    date_string = date_string.strip()
    match = re.match('\d{2}/\d{2}/\d{4}', date_string)

    if not match:
        return None

    if len(str(match.group())) == 10:
        month, day, year = map(int, date_string.split("/"))
        return date(year, month, day)
    return None


def validator(data, inst, length=None):
    """
    Check that data is not empty, data is an instance
    of the inst parameter, and if indexing parameter
    length, checks that data length longer than
    parameter length.

    :param data: any
    :param inst: type of data
    :param length: integer
    :return boolean:
    """
    if not data:
        return False

    if not isinstance(data, inst):
        return False

    if length:
        return False if len(data) < length else True

    return True
