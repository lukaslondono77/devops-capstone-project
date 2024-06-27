
"""
Package: service
Package for the application models and services routes
This module creates and configures  the flask app and sets up the loggin
and SQL database
"""
import sys
from flask import Flask
from service import config
from service.common import log_handlers
from flask_talisman import Talisman
from flask_cors import CORS

# Create Flask application
app = Flask(__name__)
app.config.from_object(config)
talisman = Talisman(app)
CORS(app)

# Import the routes after the Flask app is created
# pylint: disable=wrong-import-position, cyclic-import, wrong-import-order
from service import routers, models  # noqa: F401 E402
