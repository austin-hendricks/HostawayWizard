import os
import pytest
from unittest.mock import MagicMock
from utils import slackbot


# Helper function to reset environment variables
def reset_env_vars():
    os.environ["SLACK_BOT_TOKEN"] = "test-token"
    os.environ["SLACK_WEBHOOK_CHANNEL_ID"] = "test-channel-id"


# Fixture to reset environment variables before each test
@pytest.fixture(autouse=True)
def setup_env_vars():
    reset_env_vars()
    yield
    reset_env_vars()


def test_message_channel_successful_send(mocker):
    """Test successful message sending to Slack channel."""
    mock_post = mocker.patch("requests.post")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}
    mock_post.return_value = mock_response

    slackbot.message_channel("Hello, Slack!")

    mock_post.assert_called_once_with(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token",
        },
        json={"channel": "test-channel-id", "text": "Hello, Slack!"},
    )


def test_message_channel_missing_token(mocker):
    """Test handling when SLACK_BOT_TOKEN is missing."""
    mocker.patch.dict(os.environ, {"SLACK_BOT_TOKEN": ""})
    mock_log_error = mocker.patch("utils.logger.log_error")

    slackbot.message_channel("Hello, Slack!")

    mock_log_error.assert_called_once_with(
        "Slack bot token not found. Please set the SLACK_BOT_TOKEN environment variable.",
        logger="slack",
    )


def test_message_channel_missing_channel_id(mocker):
    """Test handling when SLACK_WEBHOOK_CHANNEL_ID is missing."""
    mocker.patch.dict(os.environ, {"SLACK_WEBHOOK_CHANNEL_ID": ""})
    mock_log_error = mocker.patch("utils.logger.log_error")

    slackbot.message_channel("Hello, Slack!")

    mock_log_error.assert_called_once_with(
        "Slack channel ID not found. Please set the SLACK_WEBHOOK_CHANNEL_ID environment variable or provide a valid channel ID.",
        logger="slack",
    )


def test_message_channel_rate_limit_handling(mocker):
    """Test handling of Slack rate limit (HTTP 429)."""
    mock_post = mocker.patch("requests.post")
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "1"}
    mock_post.return_value = mock_response

    mock_log_warning = mocker.patch("utils.logger.log_warning")
    mock_log_error = mocker.patch("utils.logger.log_error")

    # Call the function and check behavior
    slackbot.message_channel("Hello, Slack!")

    # Assert warnings and retries
    assert mock_log_warning.call_count == 3  # 3 retries
    mock_log_warning.assert_called_with(
        "Rate limit hit. Retrying after 1 seconds (Attempt 3/3).",
        logger="slack",
        bypass_standard=True,
    )

    # Assert that an error is logged after max retries
    mock_log_error.assert_called_with(
        "Max retries reached. Failed to send message due to rate limiting.",
        logger="slack",
    )


def test_message_channel_rate_limiter(mocker):
    """Test that the rate limiter is being called correctly."""
    mock_wait_until_can_proceed = mocker.patch.object(
        slackbot.slack_rate_limiter, "wait_until_can_proceed"
    )

    mock_post = mocker.patch("requests.post")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}
    mock_post.return_value = mock_response

    slackbot.message_channel("Hello, Slack!")

    # Ensure rate limiter wait is called before sending message
    mock_wait_until_can_proceed.assert_called_once()
