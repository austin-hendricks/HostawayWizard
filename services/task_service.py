from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from datetime import date, datetime

from db import db_session
import models
from utils import notifier


def create_task(task_obj, notifySuccess=True):
    """Creates a new task in the database"""
    task_id = task_obj["id"]

    # Get a list of valid columns for the Task model
    valid_columns = {column.name for column in models.Task.__table__.columns}

    # Filter task data to include only valid fields
    filtered_task_data = {
        key: value for key, value in task_obj.items() if key in valid_columns
    }

    # Create a new task entry
    try:
        task = models.Task(**filtered_task_data)
        db_session.add(task)
        db_session.commit()
        if notifySuccess:
            notifier.inform(f"Task created with ID: {task_id}")

    except IntegrityError as ie:
        db_session.rollback()
        if isinstance(ie.orig, UniqueViolation):
            notifier.warn(f"Duplicate task creation for Task ID: {task_id}")
        else:
            raise  # Re-raise the exception if it's not a unique constraint violation


def update_task(task_obj, notifySuccess=True):
    """Updates an existing task in the database"""
    task_id = task_obj["id"]

    # Handle task updates and create a revision entry
    task = db_session.get(models.Task, task_id)
    if task:
        # Serialize only the relevant fields from the task instance
        task_revision_data = {
            column.name: (
                getattr(task, column.name).isoformat()
                if isinstance(getattr(task, column.name), (datetime, date))
                else getattr(task, column.name)
            )
            for column in task.__table__.columns
        }

        # Save a revision before updating
        task_revision = models.TaskRevision(
            task_id=task.id, revision_data=task_revision_data
        )
        db_session.add(task_revision)

        # Update task fields
        for key, value in task_obj.items():
            setattr(task, key, value)
        db_session.commit()
        if notifySuccess:
            notifier.inform(f"Task {task_id} updated")

    else:
        notifier.error(f"Task update received for non-existent task ID: {task_id}")
