from services import task_service, reservation_service, message_service
from utils import notifier, validator, hostaway_client
from db import db
import models


def handle_event(object_type, event_type, data):
    """Handles Hostaway events"""
    # Log the webhook event
    notifier.inform(f"Data received from Hostaway webhook!")

    # Validate the webhook payload
    isValid, msg = validator.validate_hostaway_webhook_payload(data)
    if not isValid:
        notifier.error(msg)
        return

    # Extract the Hostaway data object for dispatching
    obj = data["data"]

    # Dispatch the event to the appropriate handler function
    if object_type == "task":
        __handle_task_event(event_type, obj)

    elif object_type == "reservation":
        __handle_reservation_event(event_type, obj)

    elif object_type == "conversationMessage":
        __handle_conversation_message_event(obj)


def __handle_task_event(event_type, task_obj):
    """Handles task events (task.created and task.updated)"""

    if event_type == "task.created":
        # Create a new task entry
        task_service.create_task(task_obj)

    elif event_type == "task.updated":
        # Handle task updates and create a revision entry
        task_service.update_task(task_obj)


def __handle_reservation_event(event_type, reservation_obj):
    """Handles reservation events (reservation.created and reservation.updated)"""

    if event_type == "reservation.created":
        # Create a new reservation entry
        reservation_service.create_reservation(reservation_obj)

    elif event_type == "reservation.updated":
        # Handle reservation updates and create a revision entry
        reservation_service.update_reservation(reservation_obj)


def __handle_conversation_message_event(message_obj):
    """Handles conversationMessage events (message.received)"""
    # Ensure referenced reservation exists in the database
    reservation_id = message_obj["reservationId"]
    reservation = db.session.get(models.Reservation, reservation_id)
    if not reservation:
        notifier.inform(
            f"Conversation message received for missing reservation {reservation_id}. Polling Hostaway API for reservation data...",
        )
        # Reservation not found, try to fetch it from Hostaway API
        reservation_data = hostaway_client.get_reservation(reservation_id)
        if reservation_data:
            # Ingest the fetched reservation into the database
            reservation_service.create_reservation(reservation_data)
        else:
            notifier.inform(
                f"Failed to retrieve reservation {reservation_id} from Hostaway API."
            )

    message_service.create_conversation_message(message_obj)
