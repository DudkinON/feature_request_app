#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice
from string import ascii_uppercase as uppercase, digits


def get_unique_str(amount):
    """
    Return a unique string

    :param amount: (int)
    :return string:
    """
    return ''.join(choice(uppercase + digits) for x in xrange(amount))
