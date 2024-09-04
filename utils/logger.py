import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    # Setup logging configurations
    # General logger for basic updates
    general_handler = RotatingFileHandler(
        "logs/general.log", maxBytes=100000, backupCount=5
    )
    general_handler.setLevel(logging.INFO)
    general_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    general_handler.setFormatter(general_formatter)

    # Logger for warnings
    warning_handler = RotatingFileHandler(
        "logs/warnings.log", maxBytes=100000, backupCount=5
    )
    warning_handler.setLevel(logging.WARNING)
    warning_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    warning_handler.setFormatter(warning_formatter)

    # Logger for errors
    error_handler = RotatingFileHandler(
        "logs/errors.log", maxBytes=100000, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    error_handler.setFormatter(error_formatter)

    # Logger for tasks
    task_handler = RotatingFileHandler(
        "logs/hostaway_tasks.log", maxBytes=100000, backupCount=5
    )
    task_handler.setLevel(logging.INFO)
    task_formatter = logging.Formatter("%(asctime)s - %(message)s")
    task_handler.setFormatter(task_formatter)

    # Logger for messages
    message_handler = RotatingFileHandler(
        "logs/hostaway_conversation_messages.log", maxBytes=100000, backupCount=5
    )
    message_handler.setLevel(logging.INFO)
    message_formatter = logging.Formatter("%(asctime)s - %(message)s")
    message_handler.setFormatter(message_formatter)

    # Logger for reservations
    reservation_handler = RotatingFileHandler(
        "logs/hostaway_reservations.log", maxBytes=100000, backupCount=5
    )
    reservation_handler.setLevel(logging.INFO)
    reservation_formatter = logging.Formatter("%(asctime)s - %(message)s")
    reservation_handler.setFormatter(reservation_formatter)

    # Assign handlers to specific loggers
    logging.getLogger("general").addHandler(general_handler)
    logging.getLogger("warning").addHandler(warning_handler)
    logging.getLogger("error").addHandler(error_handler)
    logging.getLogger("task").addHandler(task_handler)
    logging.getLogger("conversationMessage").addHandler(message_handler)
    logging.getLogger("reservation").addHandler(reservation_handler)

    # Set the level for all loggers
    logging.getLogger("general").setLevel(logging.INFO)
    logging.getLogger("warning").setLevel(logging.WARNING)
    logging.getLogger("error").setLevel(logging.ERROR)
    logging.getLogger("task").setLevel(logging.INFO)
    logging.getLogger("conversationMessage").setLevel(logging.INFO)
    logging.getLogger("reservation").setLevel(logging.INFO)


def log_inform(message, logger="general"):
    logging.getLogger(logger).info(message)


def log_warning(message):
    logging.getLogger("general").info(
        "Warning issued, see 'Warnings' log for details: https://gibbon-game-eagle.ngrok-free.app/logs/warnings"
    )
    logging.getLogger("warning").warning(message)


def log_error(message):
    logging.getLogger("general").info(
        "Error issued, see 'Errors' log for details: https://gibbon-game-eagle.ngrok-free.app/logs/errors"
    )
    logging.getLogger("error").error(message)
