from utils import validator, logger, slackbot


def handle_command(command, request_data):
    """Handles Slack slash commands."""

    # Validate the request and extract sanitized user text
    isValid, text = validator.validate_and_sanitize_slack_input(request_data)
    if not isValid:
        logger.log_error(text, logger="slack")
        slackbot.message_channel(text, channel_id=request_data["channel_id"])
        return

    # Dispatch the slash command to the appropriate function
    if command == "speak":
        __slash_speak(request_data["channel_id"], text)


def __slash_speak(channel_id, sanitised_user_text):
    """Handles the /speak command"""

    # Log the incoming slash command details
    logger.log_inform(
        f"Received /speak command in channel {channel_id} with sanitized text: '{sanitised_user_text}'",
        logger="slack",
    )

    # Use the Slack API to send a message to the channel
    slackbot.message_channel(
        f'"{sanitised_user_text}" is such a silly thing to say!', channel_id=channel_id
    )
