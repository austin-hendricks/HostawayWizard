import os

import logging
from logging.handlers import RotatingFileHandler

APP_STATIC_DOMAIN = os.getenv("APP_STATIC_DOMAIN", "http://localhost:5000")


def setup_logging():
    """Initializes the logging system."""

    # Standard loggers
    __initialize_logger("general", level=logging.INFO)
    __initialize_logger("errors", level=logging.ERROR)
    __initialize_logger("warnings", level=logging.WARNING)

    # Hostaway loggers
    __initialize_logger("hostaway", level=logging.INFO)
    __initialize_logger("hostaway_data_sync", level=logging.INFO)

    # Slack loggers
    __initialize_logger("slack", level=logging.INFO)


def log_inform(message, logger="general"):
    logging.getLogger(logger).info(message)


def log_warning(message, logger="general", bypass_standard=False):
    if bypass_standard:
        logging.getLogger(logger).warning(message)
    else:
        logging.getLogger(logger).info(
            f"Warning issued, see 'Warnings' log for details: {APP_STATIC_DOMAIN}/logs/warnings"
        )
        logging.getLogger("warnings").warning(message)


def log_error(message, logger="general", bypass_standard=False):
    if bypass_standard:
        logging.getLogger(logger).error(message)
    else:
        logging.getLogger(logger).info(
            f"Error issued, see 'Errors' log for details: {APP_STATIC_DOMAIN}/logs/errors"
        )
        logging.getLogger("errors").error(message)


def __initialize_logger(logger_reference, fname=None, level=logging.INFO):
    """Initializes a new logger with the specified name and level."""

    if fname is None:
        fname = logger_reference

    log_handler = RotatingFileHandler(
        f"logs/{fname}.log", maxBytes=100000, backupCount=5
    )
    log_handler.setLevel(level)
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(log_formatter)

    logging.getLogger(logger_reference).addHandler(log_handler)
    logging.getLogger(logger_reference).setLevel(level)
