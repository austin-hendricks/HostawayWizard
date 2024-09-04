import os
import requests
from utils import logger

# Retrieve Slack bot token and channel ID from environment variables at the module level
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_WEBHOOK_CHANNEL_ID = os.getenv("SLACK_WEBHOOK_CHANNEL_ID")


def message_channel(message, channel_id=SLACK_WEBHOOK_CHANNEL_ID):
    """
    Sends a message to the specified Slack channel using the Slack Web API.
    """

    if not SLACK_BOT_TOKEN:
        logger.log_error(
            "Slack bot token not found. Please set the SLACK_BOT_TOKEN environment variable."
        )
        return

    if not channel_id:
        logger.log_error(
            "Slack channel ID not found. Please set the SLACK_WEBHOOK_CHANNEL_ID environment variable."
        )
        return

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
    }
    data = {"channel": channel_id, "text": message}

    # Send the message to Slack
    response = requests.post(url, headers=headers, json=data)

    # Log the response from Slack
    if response.status_code == 200 and response.json().get("ok"):
        logger.log_inform(f"Message sent to Slack channel {channel_id}")
    else:
        logger.log_error(f"Failed to send message: {response.text}")
