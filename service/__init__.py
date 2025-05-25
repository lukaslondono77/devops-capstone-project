"""
Package: service
Package for the Account service
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

# Create Flask application
app = Flask(__name__, static_folder='../static')
CORS(app)  # Enable CORS for all routes

app.config['SECRET_KEY'] = 'secret-for-dev'
app.config['LOGGING_LEVEL'] = 'INFO'

# Set up logging for production
print('Setting up logging for {}...'.format(__name__))
app.logger.info('Logging established')

# Initialize the database
from service import models
models.init_db(app)

# Import routes last to avoid circular import
from service import routes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
