import re
import bleach

from utils import logger, slack


def handle_slack_command(command, request):
    """Handles Slack slash commands."""

    if command == "speak":
        __slash_speak(request)


def __slash_speak(request):
    """Handles the /speak command"""
    # Extract and sanitize the payload from the Slack command
    user_text = request.form.get("text", "")
    channel_id = request.form.get("channel_id")

    # Ensure the channel_id is valid
    if not re.match(r"^\S{1,256}$", channel_id):
        logger.log_error("Invalid channel ID received from Slack command.")
        return

    # Sanitize user input using bleach
    sanitized_text = bleach.clean(user_text)

    # Further validation checks on the sanitized input
    if len(sanitized_text) > 200:  # Limit to a reasonable length
        logger.log_error(f"Input text is too long: {sanitized_text}")
        slack.message_channel("Limit input to 200 characters.", channel_id=channel_id)
        return

    if not sanitized_text:  # Check if text is empty after sanitization
        logger.log_error("Empty or invalid input received from Slack command.")
        slack.message_channel("Please provide a valid input.", channel_id=channel_id)
        return

    # Log the incoming slash command details
    logger.logging.getLogger("general").info(
        f"Received /speak command with sanitized text: '{sanitized_text}' in channel: {channel_id}"
    )

    # Use the Slack API to send a message to the channel
    slack.message_channel(
        f'"{sanitized_text}" is such a silly thing to say!', channel_id=channel_id
    )
