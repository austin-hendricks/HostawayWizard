from flask import Blueprint, request, jsonify
from workers import jobs

hostaway_routes_bp = Blueprint("hostaway", __name__)


@hostaway_routes_bp.route("/hostaway/webhook", methods=["POST"])
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
