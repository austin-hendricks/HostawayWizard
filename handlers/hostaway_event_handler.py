from services import task_service, reservation_service, message_service


def handle_event(object_type, event_type, data):
    """Handles Hostaway events"""

    if object_type == "task":
        __handle_task_event(event_type, data)

    elif object_type == "reservation":
        __handle_reservation_event(event_type, data)

    elif object_type == "conversationMessage":
        __handle_conversation_message_event(data)


def __handle_task_event(event_type, data):
    """Handles task events (task.created and task.updated)"""

    if event_type == "task.created":
        # Create a new task entry
        task_service.create_task(data)

    elif event_type == "task.updated":
        # Handle task updates and create a revision entry
        task_service.update_task(data)


def __handle_reservation_event(event_type, data):
    """Handles reservation events (reservation.created and reservation.updated)"""

    if event_type == "reservation.created":
        # Create a new reservation entry
        reservation_service.create_reservation(data)

    elif event_type == "reservation.updated":
        # Handle reservation updates and create a revision entry
        reservation_service.update_reservation(data)


def __handle_conversation_message_event(data):
    """Handles conversationMessage events (message.received)"""
    message_service.create_conversation_message(data)
