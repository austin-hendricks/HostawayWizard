import os
import re
import bleach
from sqlalchemy.types import Integer, String, Boolean
from sqlalchemy import inspect

import models

HOSTAWAY_ACCOUNT_ID = os.getenv("HOSTAWAY_ACCOUNT_ID")

# Define valid events for each object type
VALID_HOSTAWAY_EVENTS = {
    "task": ["task.created", "task.updated"],
    "conversationMessage": ["message.received"],
    "reservation": ["reservation.created", "reservation.updated"],
}


def validate_and_sanitize_slack_input(request_data):
    """
    Validates and sanitizes Slack input.
    Returns a tuple of (success[bool], message[str]).
    If success is False, message is an error message.
    If success is True, message is the sanitized user input.
    """

    user_text = request_data.get("text", "")
    channel_id = request_data.get("channel_id")

    # Validate channel ID and presence of user input
    if not user_text:
        return False, "Empty user input. Please provide a valid input."
    if not channel_id or not re.match(r"^\S{1,256}$", channel_id):
        return False, "Invalid channel ID"

    # Sanitize user input using bleach
    sanitized_text = bleach.clean(user_text)

    # Further validation checks on the sanitized input
    if len(sanitized_text) > 200:  # Limit to a reasonable length
        return False, "Input text is too long. Limit to 200 characters."
    if not sanitized_text:  # Check if text is empty after sanitization
        return False, "Empty or invalid input. Please provide a valid input."

    return True, sanitized_text


def validate_hostaway_webhook_payload(payload):
    """
    Validates a Hostaway webhook payload.
    Returns a tuple of (success[bool], message[str]).
    """
    # Validate structure
    if not payload:
        return False, "Invalid data format"
    if "object" not in payload:
        return False, "Invalid data format"
    if "event" not in payload:
        return False, "Invalid data format"
    if "accountId" not in payload:
        return False, "Invalid data format"
    if "data" not in payload:
        return False, "Invalid data format"
    if "id" not in payload["data"]:
        return False, "Invalid data format"
    if not isinstance(payload["data"], dict):
        return False, "Invalid data format"

    # Validate content
    if str(payload["accountId"]) != str(HOSTAWAY_ACCOUNT_ID):
        return (False, "Invalid account ID")
    if payload["object"] not in VALID_HOSTAWAY_EVENTS:
        return False, f"Invalid object type: {payload['object']}"
    if payload["event"] not in VALID_HOSTAWAY_EVENTS[payload["object"]]:
        return False, f"Invalid event for {payload['object']}: {payload['event']}"

    # Validate data against models
    isValidAgainstModel, msg = __validate_hostaway_payload_against_model(
        payload["data"], payload["object"]
    )
    if not isValidAgainstModel:
        return False, msg

    return True, "Valid payload"


def __validate_hostaway_payload_against_model(data, object_type):
    """
    Validates that the data dictionary has the correct types and required fields
    according to the SQLAlchemy model.
    """
    if object_type == "conversationMessage":
        model = models.ConversationMessage
    elif object_type == "task":
        model = models.Task
    elif object_type == "reservation":
        model = models.Reservation
    else:
        return False, f"Invalid object type: {object_type}"

    inspector = inspect(model)

    for column in inspector.columns:
        column_name = column.name
        column_type = column.type
        is_nullable = column.nullable

        # Check if the column is required but not present in the data
        if (
            not is_nullable
            and column_name not in data
            and column_name not in ["created_at", "updated_at"]
        ):
            return False, f"Missing required field: {column_name}"

        # If the column is present, validate its type
        if column_name in data:
            value = data[column_name]

            # Validate based on the SQLAlchemy column type
            if value is not None:
                if isinstance(column_type, Integer) and not isinstance(value, int):
                    return (
                        False,
                        f"Incorrect type for {object_type} field {column_name}: expected int, got {type(value).__name__}",
                    )
                elif isinstance(column_type, String) and not isinstance(value, str):
                    return (
                        False,
                        f"Incorrect type for {object_type} field {column_name}: expected str, got {type(value).__name__}",
                    )
                elif isinstance(column_type, Boolean) and not isinstance(
                    value, int
                ):  # Hostaway API v1 returns 0 or 1 for all boolean fields
                    if value not in [0, 1]:
                        return (
                            False,
                            f"Incorrect type for {object_type} field {column_name}: expected bool, got {type(value).__name__}",
                        )

    return True, "Valid data"
