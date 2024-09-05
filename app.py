import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

from db import db
from config import Config
from utils import logger, notifier, validator
from workers import jobs, webhook_processor
from handlers import slack_command_handler


app = Flask(__name__)

# Configure the SQLAlchemy connection string
app.config.from_object(Config)

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Setup Logging
logger.setup_logging()

# Start Worker thread to process Hostaway webhooks
webhook_processor.start_worker(app)


@app.route("/")
def home():
    return "<h1>HostawayWizard is the Future!</h1>"


# Webhook endpoint to receive Hostaway events
@app.route("/hostaway/webhook", methods=["POST"])
def receive_hostaway_webhook():
    try:
        # Extract the webhook payload
        data = request.json

        # Log the webhook event
        notifier.inform(f"Data received from Hostaway webhook!")

        # Validate the webhook payload
        isValid, msg = validator.validate_webhook_payload(data)
        if not isValid:
            return jsonify({"status": "error", "message": msg}), 400

        # Send payload to Hostaway Webhook job queue
        jobs.hostaway_webhook_queue.put(data)

        # Return a success response
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Webhook received successfully",
                }
            ),
            200,
        )

    except Exception as e:
        # Handle any errors that occur
        notifier.error(
            f"Returned 500 - Unexpected error receiving Hostaway webhook: {str(e)}"
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/slack/slash/<command>", methods=["POST"])
def receive_slack_command(command):
    # Handle the slash command
    slack_command_handler.handle_slack_command(command, request)

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


if __name__ == "__main__":
    # Run the Flask app on port 5000
    app.run(host="0.0.0.0", port=5000)
