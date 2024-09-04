from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from db import db
import models
from utils import notifier


def create_conversation_message(data):
    """Creates a new conversationMessage in the database"""
    message_id = data["data"]["id"]

    # Create or update the conversation message
    conversation_id = data["data"]["conversationId"]
    reservation_id = data["data"].get("reservationId")

    # Ensure the conversation exists
    conversation = db.session.get(models.Conversation, conversation_id)
    if not conversation:
        conversation = models.Conversation(
            id=conversation_id, reservation_id=reservation_id
        )
        db.session.add(conversation)
        db.session.commit()

    # Get a list of valid columns for the conversationMessage model
    valid_columns = {
        column.name for column in models.ConversationMessage.__table__.columns
    }

    # Filter conversationMessage data to include only valid fields
    filtered_conversationMessage_data = {
        key: value for key, value in data["data"].items() if key in valid_columns
    }

    try:
        # Create the conversation message
        conversation_message = models.ConversationMessage(
            **filtered_conversationMessage_data
        )
        db.session.add(conversation_message)
        db.session.commit()
        notifier.inform(f"ConversationMessage received with ID: {message_id}")
    except IntegrityError as ie:
        db.session.rollback()
        if isinstance(ie.orig, UniqueViolation):
            notifier.warn(
                f"Duplicate conversationMessage received. Duplicated ID: {message_id}"
            )
        else:
            raise  # Re-raise the exception if it's not a unique constraint violation
