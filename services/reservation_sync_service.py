from sqlalchemy import inspect

from db import db_session
import models
from utils import logger, notifier, slackbot, hostaway_client, validator
from services import reservation_service


def sync_reservations_with_hostaway():
    """Fetches reservations from Hostaway and ensures they match the local database."""

    notifier.inform("Syncing reservations with Hostaway...")

    # Fetch all reservations from the Hostaway API
    reservations = hostaway_client.get_reservations()
    if not reservations:
        notifier.error("Failed to retrieve all reservations from Hostaway API.")
        return

    outdatedReservationCount = 0
    missingReservationCount = 0

    # Iterate through each reservation from Hostaway
    for hostaway_reservation in reservations:
        reservation_id = hostaway_reservation["id"]
        local_reservation = db_session.get(models.Reservation, reservation_id)

        if not local_reservation:
            logger.log_inform(
                f"Reservation {reservation_id} not found locally. Creating it...",
                logger="hostaway_data_sync",
            )
            missingReservationCount += 1

            # Reservation not found locally, ingest it into the database if valid
            isValid, msg = validator.validate_hostaway_payload_against_model(
                hostaway_reservation, "reservation"
            )
            if not isValid:
                logger.log_error(
                    f"Invalid reservation fetched from Hostaway API (id {reservation_id}): {msg}",
                    logger="hostaway_data_sync",
                )
                continue
            ingest_reservation(hostaway_reservation)
        else:
            # Check for discrepancies and update if necessary
            discrepancies = check_for_discrepancies(
                local_reservation, hostaway_reservation
            )
            if discrepancies:
                logger.log_warning(
                    f"Reservation {reservation_id} data is out of sync with Hostaway. Resolving discrepancies...",
                    logger="hostaway_data_sync",
                )
                outdatedReservationCount += 1
                notify_discrepancy(reservation_id, discrepancies)
                update_local_reservation(hostaway_reservation)

    # Log the summary of the sync process
    summary_msg = f"Synced {len(reservations)} reservations with Hostaway."
    if missingReservationCount > 0:
        summary_msg += f" Ingested {missingReservationCount} missing reservations."
    if outdatedReservationCount > 0:
        summary_msg += f" Updated {outdatedReservationCount} outdated reservations."
    notifier.inform(summary_msg)


def ingest_reservation(reservation_data):
    """Ingests a new reservation into the local database."""
    try:
        reservation_service.create_reservation(reservation_data, notifySuccess=False)
    except Exception as e:
        notifier.error(
            f"Failed to ingest missing reservation with ID {reservation_data['id']}: {str(e)}"
        )


def check_for_discrepancies(local_reservation, hostaway_reservation):
    """Compares a local reservation with a Hostaway reservation and returns a list of discrepancies."""
    discrepancies = []
    inspector = inspect(models.Reservation)
    columns = {
        column.name
        for column in inspector.columns
        if (column.name != "created_at" and column.name != "updated_at")
    }

    for column in columns:
        local_value = getattr(local_reservation, column)
        hostaway_value = hostaway_reservation.get(column)

        if str(local_value) != str(hostaway_value):
            discrepancies.append(
                f"{column}: Local({local_value}) vs Hostaway({hostaway_value})"
            )

    return discrepancies


def update_local_reservation(hostaway_reservation):
    """Updates the local reservation to match the Hostaway reservation."""
    try:
        reservation_service.update_reservation(
            hostaway_reservation, notifySuccess=False
        )
    except Exception as e:
        notifier.error(
            f"Failed to update outdated reservation data with ID {hostaway_reservation['id']}: {str(e)}"
        )


def notify_discrepancy(reservation_id, discrepancies):
    """Sends a message to Slack with the list of discrepancies."""
    message = f"Discrepancies found for reservation ID {reservation_id}:\n" + "\n".join(
        discrepancies
    )
    slackbot.message_channel(message)
