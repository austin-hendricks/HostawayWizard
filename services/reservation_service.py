from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from datetime import date, datetime

from db import db_session
import models
from utils import notifier


def create_reservation(reservation_obj, notifySuccess=True):
    """Creates a new reservation in the database"""
    reservation_id = reservation_obj["id"]

    # Get a list of valid columns for the Reservation model
    valid_columns = {column.name for column in models.Reservation.__table__.columns}

    # Filter reservation data to include only valid fields
    filtered_reservation_data = {
        key: value for key, value in reservation_obj.items() if key in valid_columns
    }

    try:
        reservation = models.Reservation(**filtered_reservation_data)
        db_session.add(reservation)
        db_session.commit()
        if notifySuccess:
            notifier.inform(f"Reservation created with ID: {reservation_id}")

    except IntegrityError as ie:
        db_session.rollback()
        if isinstance(ie.orig, UniqueViolation):
            notifier.warn(
                f"Duplicate reservation creation for Reservation ID: {reservation_id}"
            )
        else:
            raise  # Re-raise the exception if it's not a unique constraint violation


def update_reservation(reservation_obj, notifySuccess=True):
    """Updates an existing reservation in the database"""
    reservation_id = reservation_obj["id"]
    reservation = db_session.get(models.Reservation, reservation_id)
    if reservation:
        # Serialize only the relevant fields from the reservation instance
        reservation_revision_data = {
            column.name: (
                getattr(reservation, column.name).isoformat()
                if isinstance(getattr(reservation, column.name), (datetime, date))
                else getattr(reservation, column.name)
            )
            for column in reservation.__table__.columns
        }

        # Save a revision before updating
        reservation_revision = models.ReservationRevision(
            reservation_id=reservation.id, revision_data=reservation_revision_data
        )
        db_session.add(reservation_revision)

        # Update reservation fields
        for key, value in reservation_obj.items():
            setattr(reservation, key, value)
        db_session.commit()

        if notifySuccess:
            notifier.inform(f"Reservation {reservation_id} updated")

    else:
        notifier.error(
            f"Reservation update received for non-existent reservation ID: {reservation_id}"
        )
