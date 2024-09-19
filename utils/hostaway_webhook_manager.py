import os
import requests

from utils import logger, notifier

# Load environment variables
HOSTAWAY_API_KEY = os.getenv("HOSTAWAY_API_ACCESS_TOKEN")
ALERT_EMAIL = os.getenv("HOSTAWAY_API_ALERTING_EMAIL_ADDRESS")
WEBHOOK_RECEIVING_ENDPOINT = os.getenv("APP_STATIC_DOMAIN") + "/hostaway/webhook"
HOSTAWAY_WEBHOOK_API_URL = "https://api.hostaway.com/v1/webhooks/unifiedWebhooks"


# Global variable to store webhook ID(s)
REGISTERED_WEBHOOK_IDS = []


def get_headers(post=False):
    """Returns the authorization headers required for Hostaway API requests."""
    if not HOSTAWAY_API_KEY:
        logger.log_error(
            "Hostaway access token not found. Please set the HOSTAWAY_API_ACCESS_TOKEN environment variable.",
            logger="hostaway",
        )
        return None

    if post:
        return {
            "Cache-control": "no-cache",
            "Content-type": "application/json",
            "Authorization": f"Bearer {HOSTAWAY_API_KEY}",
        }

    return {"Cache-control": "no-cache", "Authorization": f"Bearer {HOSTAWAY_API_KEY}"}


def register_unified_webhook():
    """Register a unified webhook with Hostaway."""
    global REGISTERED_WEBHOOK_IDS

    data = {
        "isEnabled": 1,
        "url": WEBHOOK_RECEIVING_ENDPOINT,
        "login": None,
        "password": None,
        "alertingEmailAddress": ALERT_EMAIL,
    }

    try:
        response = requests.post(
            HOSTAWAY_WEBHOOK_API_URL,
            headers=get_headers(post=True),
            json=data,
        )
        response.raise_for_status()
        result = response.json()
        new_webhook_id = result["result"]["id"]
        REGISTERED_WEBHOOK_IDS.append(new_webhook_id)
        logger.log_inform(
            f"Unified webhook registered successfully with ID: {new_webhook_id}"
        )

    except requests.exceptions.RequestException as e:
        notifier.error(f"Failed to register webhook: {e}\nResponse: {response.text}")


def deregister_unified_webhook(webhook_id=None):
    """Deregister a unified webhook with Hostaway."""
    global REGISTERED_WEBHOOK_IDS
    poppedFromList = False

    if webhook_id is None:
        if len(REGISTERED_WEBHOOK_IDS) == 0:
            logger.log_error("No webhook ID found. Skipping deregistration.")
            return
        webhook_id = REGISTERED_WEBHOOK_IDS.pop()
        poppedFromList = True

    try:
        response = requests.delete(
            f"{HOSTAWAY_WEBHOOK_API_URL}/{webhook_id}",
            headers=get_headers(),
        )
        response.raise_for_status()
        logger.log_inform(f"Webhook with ID {webhook_id} deregistered successfully.")
        if not poppedFromList:
            REGISTERED_WEBHOOK_IDS.remove(webhook_id)

    except requests.exceptions.RequestException as e:
        notifier.error(f"Failed to deregister webhook with ID {webhook_id}: {e}")
        if poppedFromList:
            REGISTERED_WEBHOOK_IDS.append(
                webhook_id
            )  # Re-add webhook ID to list if deregistration failed


def load_registered_webhook_ids():
    """Load registered webhook IDs into the global variable."""
    global REGISTERED_WEBHOOK_IDS
    REGISTERED_WEBHOOK_IDS = [x["id"] for x in get_all_unified_webhooks()]


def deregister_all_unified_webhooks():
    """Delete all unified webhooks registered with Hostaway."""
    global REGISTERED_WEBHOOK_IDS
    for webhook_id in REGISTERED_WEBHOOK_IDS:
        try:
            response = requests.delete(
                f"{HOSTAWAY_WEBHOOK_API_URL}/{webhook_id}",
                headers=get_headers(),
            )
            response.raise_for_status()
            logger.log_inform(
                f"Webhook with ID {webhook_id} deregistered successfully."
            )

        except requests.exceptions.RequestException as e:
            notifier.error(f"Failed to deregister webhook with ID {webhook_id}: {e}")

    REGISTERED_WEBHOOK_IDS = load_registered_webhook_ids()  # Should be empty


def get_all_unified_webhooks():
    """Get all unified webhooks registered with Hostaway."""
    try:
        response = requests.get(
            HOSTAWAY_WEBHOOK_API_URL,
            headers=get_headers(),
        )
        response.raise_for_status()
        result = response.json()
        return result["result"]

    except requests.exceptions.RequestException as e:
        notifier.error(f"Failed to get all unified webhooks: {e}")
        return []


def read_unified_webhook(webhook_id):
    """Get a specific unified webhook object registered with Hostaway."""
    try:
        response = requests.get(
            f"{HOSTAWAY_WEBHOOK_API_URL}/{webhook_id}",
            headers=get_headers(),
        )
        response.raise_for_status()
        result = response.json()
        return result["result"]

    except requests.exceptions.RequestException as e:
        notifier.error(f"Failed to get webhook with ID {webhook_id}: {e}")
        return None


def update_unified_webhook(webhook_id, data):
    """Update a specific unified webhook object registered with Hostaway."""
    try:
        response = requests.put(
            f"{HOSTAWAY_WEBHOOK_API_URL}/{webhook_id}", headers=get_headers(), json=data
        )
        response.raise_for_status()
        result = response.json()
        return result["result"]

    except requests.exceptions.RequestException as e:
        notifier.error(f"Failed to update webhook with ID {webhook_id}: {e}")
        return None
