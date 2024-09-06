import os

from utils import logger, slackbot

APP_STATIC_DOMAIN = os.getenv("APP_STATIC_DOMAIN", "http://localhost:5000")


def inform(message, logger_name="general"):
    """
    Sends an information message to the specified logger and to Slack.
    Default logger name is "general".
    """
    logger.log_inform(message, logger_name)
    slackbot.message_channel(message)


def warn(message):
    """
    Sends a warning message to the warning log and to Slack.
    """
    logger.log_warning(message)
    slackbot.message_channel(
        f"Warning issued, see 'Warnings' log for details: {APP_STATIC_DOMAIN}/logs/warnings\n"
    )


def error(message):
    """
    Sends an error message to the error log and to Slack.
    """
    logger.log_error(message)
    slackbot.message_channel(
        f"Error issued, see 'Errors' log for details: {APP_STATIC_DOMAIN}/logs/errors\n"
    )
