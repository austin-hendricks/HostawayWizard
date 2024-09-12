import os
import time
import requests
from utils import logger
from utils.rate_limiter import RateLimiter

MAX_RETRIES = 3  # Define a maximum number of retries

# Initialize the rate limiter for Slack messages (1 message per second)
slack_rate_limiter = RateLimiter(rate_limit_per_second=1)


def __get_slack_config():
    """
    Fetches the Slack bot token and channel ID from environment variables.
    Returns a tuple (SLACK_BOT_TOKEN, SLACK_WEBHOOK_CHANNEL_ID).
    """
    slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
    slack_webhook_channel_id = os.getenv("SLACK_WEBHOOK_CHANNEL_ID")
    return slack_bot_token, slack_webhook_channel_id


def message_channel(message, channel_id=None, retry_count=0):
    """
    Sends a message to the specified Slack channel using the Slack Web API.
    """

    # Fetch the Slack configuration dynamically
    slack_bot_token, slack_webhook_channel_id = __get_slack_config()

    # Use the channel_id argument if provided, otherwise use the environment variable
    channel_id = channel_id or slack_webhook_channel_id

    if not slack_bot_token:
        logger.log_error(
            "Slack bot token not found. Please set the SLACK_BOT_TOKEN environment variable.",
            logger="slack",
        )
        return

    if not channel_id:
        logger.log_error(
            "Slack channel ID not found. Please set the SLACK_WEBHOOK_CHANNEL_ID environment variable or provide a valid channel ID.",
            logger="slack",
        )
        return

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {slack_bot_token}",
    }
    data = {"channel": channel_id, "text": message}

    # Check if the rate limiter allows sending the message
    slack_rate_limiter.wait_until_can_proceed()

    try:
        # Send the message to Slack
        response = requests.post(url, headers=headers, json=data)

        # Handle rate limit error (HTTP 429)
        if response.status_code == 429:
            if retry_count < MAX_RETRIES:
                retry_after = int(response.headers.get("Retry-After", 1))
                logger.log_warning(
                    f"Rate limit hit. Retrying after {retry_after} seconds (Attempt {retry_count + 1}/{MAX_RETRIES}).",
                    logger="slack",
                    bypass_standard=True,
                )
                time.sleep(retry_after)
                return message_channel(
                    message, channel_id, retry_count + 1
                )  # Retry sending the message
            else:
                logger.log_error(
                    "Max retries reached. Failed to send message due to rate limiting.",
                    logger="slack",
                )
                return

        # Log the response from Slack
        if response.status_code == 200 and response.json().get("ok"):
            logger.log_inform(
                f"Message sent to Slack channel {channel_id}", logger="slack"
            )
        else:
            logger.log_error(f"Failed to send message: {response.text}", logger="slack")

    except requests.exceptions.RequestException as e:
        logger.log_error(f"Error sending message to Slack: {e}", logger="slack")
