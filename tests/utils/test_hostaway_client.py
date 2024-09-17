import pytest
import time
from unittest.mock import MagicMock
from utils.hostaway_client import (
    get_reservation,
    get_reservations,
    hostaway_rate_limiter,
)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Fixture to reset the rate limiter before each test."""
    hostaway_rate_limiter.last_check = 0
    yield
    hostaway_rate_limiter.last_check = 0


def test_get_reservation_rate_limiting(mocker):
    """Test that rate limiting is correctly applied when fetching a reservation."""
    mock_headers = mocker.patch("utils.hostaway_client.get_headers")
    mock_headers.return_value = "Bearer test-token"

    mock_get = mocker.patch("utils.hostaway_client.requests.get")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": {"id": 1, "name": "Test Reservation"}}
    mock_get.return_value = mock_response

    mock_validate = mocker.patch(
        "utils.hostaway_client.validator.validate_hostaway_payload_against_model"
    )
    mock_validate.return_value = (True, None)

    # First call should succeed immediately
    get_reservation(1)
    assert mock_get.call_count == 1, "First API call should be made immediately"

    # Second call should be delayed by rate limiter
    start_time = time.time()
    get_reservation(1)
    end_time = time.time()
    assert mock_get.call_count == 2, "Second API call should be made after delay"

    # Check that the delay was at least the minimum required by the rate limiter
    assert end_time - start_time >= (
        1 / hostaway_rate_limiter.rate_limit
    ), "Rate limiter did not enforce the correct delay"


def test_get_reservations_rate_limiting(mocker):
    """Test that rate limiting is correctly applied when fetching all reservations."""
    mock_headers = mocker.patch("utils.hostaway_client.get_headers")
    mock_headers.return_value = "Bearer test-token"

    mock_get = mocker.patch("utils.hostaway_client.requests.get")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": [{"id": i} for i in range(1, 16)]}
    mock_get.return_value = mock_response

    # Call the function to fetch reservations
    get_reservations(limit=5)
    assert mock_get.call_count == 1, "First API call should be made immediately"

    # Make another API call and ensure rate limiting applies
    start_time = time.time()
    get_reservations(limit=5)
    end_time = time.time()

    assert (
        mock_get.call_count == 2
    ), "Second API call should be made after rate limiter delay"
    assert end_time - start_time >= (
        1 / hostaway_rate_limiter.rate_limit
    ), "Rate limiter did not enforce the correct delay"


def test_rate_limiter_behavior():
    """Direct test for rate limiter behavior without making API calls."""
    # First request should be allowed immediately
    assert hostaway_rate_limiter.can_proceed() is True

    # Second request should be blocked immediately after the first
    assert hostaway_rate_limiter.can_proceed() is False

    # Wait for enough time to pass and check again
    time.sleep(1 / hostaway_rate_limiter.rate_limit)
    assert hostaway_rate_limiter.can_proceed() is True
