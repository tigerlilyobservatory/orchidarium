"""
This module is responsible for the healthcheck API.
"""


from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


__all__ = ['app']


from orchidarium.api.health import create_healthcheck_api


create_healthcheck_api(app)