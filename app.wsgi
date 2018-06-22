#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging

activate_this = '/var/www/feature-request-app/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/feature-request-app/")


from app import app as application
application.secret_key = 'FlaskApplicationSecretKey'