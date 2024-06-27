import sys
from flask import Flask
from service import config
from service.common import log_handlers
from flask_talisman import Talisman  # Import Talisman

# Create Flask application
app = Flask(__name__)
app.config.from_object(config)

# Import the routes After the Flask app is created
from service import routes, models

# Import error handlers and CLI commands
from service.common import error_handlers, cli_commands

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    models.init_db(app)  # make our database tables
except Exception as error:
    app.logger.critical("%s: Cannot continue", error)
    sys.exit(4)

# Initialize Talisman with the Flask app
talisman = Talisman(app)

app.logger.info("Service initialized!")
