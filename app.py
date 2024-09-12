import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

import db as database
from db import db, db_session
from config import Config
from utils import logger, notifier
from workers import (
    jobs,
    hostaway_webhook_processor,
    slack_command_processor,
    reservation_sync_worker,
)


app = Flask(__name__)

# Configure the SQLAlchemy connection string
app.config.from_object(Config)

# Initialize SQLAlchemy
database.initialize(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Setup Logging
logger.setup_logging()

# Start Worker threads for asynchronous data processing
hostaway_webhook_processor.start_worker(app)
slack_command_processor.start_worker(app)
reservation_sync_worker.start_worker(app)


@app.route("/")
def home():
    return "<h1>HostawayWizard is the Future!</h1>"


# Webhook endpoint to receive Hostaway events
@app.route("/hostaway/webhook", methods=["POST"])
def receive_hostaway_webhook():
    if not request.is_json:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid request. Expected a JSON payload.",
                }
            ),
            400,
        )

    # Send payload to Hostaway Webhook job queue
    jobs.hostaway_webhook_queue.put(request.json)

    # Return a success response to Hostaway
    return (
        jsonify(
            {
                "status": "success",
                "message": "Webhook data received successfully",
            }
        ),
        200,
    )


@app.route("/slack/slash/<command>", methods=["POST"])
def receive_slack_command(command):
    # Send payload to Slack Slash Command job queue
    jobs.slack_command_queue.put((command, request.form))

    # Respond back to Slack immediately
    return jsonify({"response_type": "ephemeral", "text": "Message is being sent!"})


@app.route("/logs/<log_type>", methods=["GET"])
def get_log(log_type):
    """
    Serve the specified log file content.
    """
    log_file_path = f"logs/{log_type}.log"

    # Check if the log file exists
    if not os.path.exists(log_file_path):
        return (
            jsonify(
                {"status": "error", "message": f"Log file '{log_type}.log' not found"}
            ),
            404,
        )

    try:
        # Read the log file
        with open(log_file_path, "r") as log_file:
            log_content = log_file.read()

        # Return the log content as a plain text response
        return Response(log_content, mimetype="text/plain")

    except Exception as e:
        notifier.error(f"Error serving log file: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to read log file: {log_file_path}",
                }
            ),
            500,
        )


@app.teardown_appcontext
def shutdown_session(exception=None):
    """
    Clean up the session at the end of each request or when the application context is torn down.
    """
    db_session.remove()  # Remove the session to ensure it is cleaned up


if __name__ == "__main__":
    # Run the Flask app on port 5000
    app.run(host="0.0.0.0", port=5000)
