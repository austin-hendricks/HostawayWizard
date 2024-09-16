from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

from db import db, db_session, initialize as initialize_db
from config import Config
from utils import logger
from workers import (
    hostaway_webhook_processor,
    slack_command_processor,
    reservation_sync_worker,
)

# Import blueprints
from blueprints.home import home_bp
from blueprints.hostaway_routes import hostaway_routes_bp
from blueprints.slack_routes import slack_routes_bp
from blueprints.log_routes import log_routes_bp


def create_app(config_class=Config):
    """Application factory function to create and configure a Flask app."""
    app = Flask(__name__)

    # Configure the app
    app.config.from_object(config_class)

    # Initialize the database and other extensions
    initialize_db(app)
    Migrate(app, db)

    # Setup Logging
    logger.setup_logging()

    # Register blueprints / routes
    register_routes(app)

    # Start worker threads for asynchronous data processing
    start_worker_threads(app)

    # Register teardown function
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """
        Clean up the session at the end of each request or when the application context is torn down.
        """
        db_session.remove()  # Remove the session to ensure it is cleaned up

    return app


def register_routes(app):
    """Register all routes and endpoints with the given Flask app."""

    app.register_blueprint(home_bp)
    app.register_blueprint(hostaway_routes_bp)
    app.register_blueprint(slack_routes_bp)
    app.register_blueprint(log_routes_bp)


def start_worker_threads(app):
    """Start worker threads for asynchronous data processing."""
    hostaway_webhook_processor.start_worker(app)
    slack_command_processor.start_worker(app)
    reservation_sync_worker.start_worker(app)


if __name__ == "__main__":
    # Create the Flask app using the factory function
    app = create_app()
    # Run the Flask app on port 5000
    app.run(host="0.0.0.0", port=5000)
