"""
This module is responsible for the healthcheck API.
"""


import sys

from flask import Flask
from flask_cors import CORS


cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None  # type: ignore

app = Flask(__name__)
CORS(app)


__all__ = ['app']


from orchidarium.api.health import create_healthcheck_api


create_healthcheck_api(app)