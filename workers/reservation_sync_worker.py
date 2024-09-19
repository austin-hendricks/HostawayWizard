import time
from threading import Thread

from services import reservation_sync_service
from utils import notifier


def worker(app):
    """Worker that runs the reservation sync process daily at midnight."""
    with app.app_context():
        # Sync reservations once at application startup
        try:
            reservation_sync_service.sync_reservations_with_hostaway()
        except Exception as e:
            notifier.error(f"Failed to sync reservations: {str(e)}")

        # Sync reservations daily at midnight
        while True:
            current_time = time.strftime("%H:%M")
            if current_time == "00:00":
                try:
                    reservation_sync_service.sync_reservations_with_hostaway()
                except Exception as e:
                    notifier.error(f"Failed to sync reservations: {str(e)}")
            time.sleep(60)  # Wait for 1 minute before checking again


def start_worker(app):
    """
    Start the worker function in a separate thread.
    Worker runs the reservation sync process daily at midnight.
    """
    worker_thread = Thread(target=worker, args=(app,))
    worker_thread.daemon = True
    worker_thread.start()
    return worker_thread
