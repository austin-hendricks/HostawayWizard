from flask import Blueprint, request, jsonify
from workers import jobs

slack_bp = Blueprint("slack", __name__)


@slack_bp.route("/slack/slash/<command>", methods=["POST"])
def receive_slack_command(command):
    # Send payload to Slack Slash Command job queue
    jobs.slack_command_queue.put((command, request.form))

    # Respond back to Slack immediately
    return jsonify({"response_type": "ephemeral", "text": "Message is being sent!"})
