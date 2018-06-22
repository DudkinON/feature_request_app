#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import *

if __name__ == '__main__':
    app.debug = app_debug
    app.run(host=app_host, port=app_port)
