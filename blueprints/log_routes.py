import os
from flask import Blueprint, jsonify, Response
from utils import notifier

log_routes_bp = Blueprint("logs", __name__)


@log_routes_bp.route("/logs/<log_type>", methods=["GET"])
def get_log(log_type):
    """
    Serve the specified log file content.
    """
    log_file_path = f"logs/{log_type}.log"

    # Check if the log file exists
    if not os.path.exists(log_file_path):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Log file '{log_type}.log' not found",
                }
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
