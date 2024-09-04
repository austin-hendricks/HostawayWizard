from threading import Thread

from workers.jobs import hostaway_webhook_queue
from utils import logger, notifier
from handlers import hostaway_event_handler


def worker(app):
    """
    Worker function to continuously process webhook payloads from the Hostaway payload queue.
    Assumes the queue is populated with validated Hostaway webhook payloads.
    """
    with app.app_context():
        while True:
            try:
                # Get a payload from the queue
                payload = hostaway_webhook_queue.get()

                if payload is None:  # Exit the worker if a None payload is received
                    break

                # Extract the relevant fields from the webhook payload
                object_type = payload["object"]
                event_type = payload["event"]

                # Log payload to specific logger
                logger.log_inform(payload, logger=object_type)

                # Send to Hostaway event handler
                hostaway_event_handler.handle_event(object_type, event_type, payload)

            except Exception as e:
                notifier.error(
                    f"Failed to process Hostaway webhook payload: {e}. Data: {payload}"
                )

            finally:
                hostaway_webhook_queue.task_done()


def start_worker(app):
    """
    Start the worker function in a separate thread.
    Assumes the job queue is populated with validated Hostaway webhook payloads.
    """
    worker_thread = Thread(target=worker, args=(app,))
    worker_thread.daemon = True
    worker_thread.start()
    return worker_thread
