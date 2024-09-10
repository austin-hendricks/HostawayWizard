import os
import time
import requests

from utils import logger, validator

# Hostaway API credentials and base URL
HOSTAWAY_API_KEY = os.getenv("HOSTAWAY_API_ACCESS_TOKEN")
HOSTAWAY_BASE_URL = os.getenv("HOSTAWAY_API_BASE_URL")

HOSTAWAY_MAX_RESERVATION_LIST_SIZE = 500


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


def get_reservations(
    limit=1000,
    offset=0,
    order="",
    channelId="",
    listingId="",
    arrivalStartDate="",
    arrivalEndDate="",
    departureStartDate="",
    departureEndDate="",
    hasUnreadConversationMessages="",
    retries=3,
    backoff_factor=1,
):
    """Fetches all reservations from the Hostaway Public API. Matching the given parameters."""
    headers = get_headers()
    if headers is None:
        return None

    for attempt in range(retries):
        try:
            response = requests.get(
                f"{HOSTAWAY_BASE_URL}/reservations?limit={limit}&offset={offset}&order={order}&channelId={channelId}&listingId={listingId}&arrivalStartDate={arrivalStartDate}&arrivalEndDate={arrivalEndDate}&departureStartDate={departureStartDate}&departureEndDate={departureEndDate}&hasUnreadConversationMessages={hasUnreadConversationMessages}",
                headers=headers,
            )
            response.raise_for_status()

            resultingArray = response.json().get("result", [])

            # Paginate if necessary (Hostaway max response size is 500)
            lengthOfResponseArray = len(resultingArray)
            while (
                limit > HOSTAWAY_MAX_RESERVATION_LIST_SIZE
                and lengthOfResponseArray == HOSTAWAY_MAX_RESERVATION_LIST_SIZE
            ):
                offset += HOSTAWAY_MAX_RESERVATION_LIST_SIZE
                next_response = requests.get(
                    f"{HOSTAWAY_BASE_URL}/reservations?limit={limit}&offset={offset}&order={order}&channelId={channelId}&listingId={listingId}&arrivalStartDate={arrivalStartDate}&arrivalEndDate={arrivalEndDate}&departureStartDate={departureStartDate}&departureEndDate={departureEndDate}&hasUnreadConversationMessages={hasUnreadConversationMessages}",
                    headers=headers,
                )
                next_response.raise_for_status()
                next_resultingArray = next_response.json().get("result", [])
                resultingArray.extend(next_resultingArray)
                lengthOfResponseArray = len(next_resultingArray)

            logger.log_inform(
                f"List of {len(resultingArray)} reservations fetched from Hostaway API",
                logger="hostaway",
            )

            return resultingArray

        except requests.exceptions.RequestException as e:
            logger.log_error(
                f"Attempt {attempt + 1} of {retries}: Error fetching all reservations from Hostaway API: {e}",
                logger="hostaway",
                bypass_standard=True,
            )

            if attempt < retries - 1:  # Check if we have retries left
                time.sleep(backoff_factor * (2**attempt))  # Exponential backoff
            else:
                return None
