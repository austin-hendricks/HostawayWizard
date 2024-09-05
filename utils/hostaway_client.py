import os
import time
import requests

from utils import logger, validator

# Hostaway API credentials and base URL
HOSTAWAY_API_KEY = os.getenv("HOSTAWAY_API_ACCESS_TOKEN")
HOSTAWAY_BASE_URL = os.getenv("HOSTAWAY_API_BASE_URL")


def get_headers():
    """Returns the authorization headers required for Hostaway API requests."""
    if not HOSTAWAY_API_KEY:
        logger.log_error(
            "Hostaway access token not found. Please set the HOSTAWAY_API_ACCESS_TOKEN environment variable.",
            logger="hostaway",
        )
        return None

    return {"Authorization": f"Bearer {HOSTAWAY_API_KEY}", "Cache-control": "no-cache"}


def get_reservation(reservation_id, retries=3, backoff_factor=1):
    """Fetches a reservation from the Hostaway Public API with retry logic."""
    headers = get_headers()
    if headers is None:
        return None

    for attempt in range(retries):
        try:
            response = requests.get(
                f"{HOSTAWAY_BASE_URL}/reservations/{reservation_id}", headers=headers
            )
            response.raise_for_status()
            reservation = response.json()["result"]
            isValid, msg = validator.validate_hostaway_payload_against_model(
                reservation, "reservation"
            )
            if not isValid:
                logger.log_error(
                    "Invalid reservation fetched from Hostaway API: " + msg,
                    logger="hostaway",
                )
                return None

            logger.log_inform(
                f"Reservation {reservation_id} fetched from Hostaway API",
                logger="hostaway",
            )
            return reservation

        except requests.exceptions.RequestException as e:
            logger.log_error(
                f"Attempt {attempt + 1} of {retries}: Error fetching reservation {reservation_id} from Hostaway API: {e}",
                logger="hostaway",
                bypass_standard=True,
            )

            if attempt < retries - 1:  # Check if we have retries left
                time.sleep(backoff_factor * (2**attempt))  # Exponential backoff
            else:
                return None
