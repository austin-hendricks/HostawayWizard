from threading import Thread

from workers.jobs import slack_command_queue
from utils import notifier
from handlers import slack_command_handler


def worker(app):
    """
    Worker function to continuously process webhook payloads from the Slack command queue.
    Assumes the queue is populated with validated and sanitized Slack slashcommand payloads.
    """
    with app.app_context():
        while True:
            try:
                # Get a payload from the queue: tuple (command, request)
                payload = slack_command_queue.get()

                if payload is None:  # Exit the worker if a None payload is received
                    break

                # Extract the relevant fields from the webhook payload tuple
                command = payload[0]
                request_data = payload[1]

                # Send to Slack command handler
                slack_command_handler.handle_command(command, request_data)

            except Exception as e:
                notifier.error(
                    f"Failed to process Slack command payload: {e}. Data: {payload}"
                )

            finally:
                slack_command_queue.task_done()


def start_worker(app):
    """
    Start the worker function in a separate thread.
    Assumes the job queue is populated with validated Slack slashcommand payloads.
    """
    worker_thread = Thread(target=worker, args=(app,))
    worker_thread.daemon = True
    worker_thread.start()
    return worker_thread
