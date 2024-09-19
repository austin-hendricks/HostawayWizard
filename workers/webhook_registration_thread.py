from threading import Thread
import time
from utils import hostaway_webhook_manager


def start(app):
    worker_thread = Thread(target=register_webhook, args=(app,))
    worker_thread.daemon = True
    worker_thread.start()
    return worker_thread


def register_webhook(app):
    with app.app_context():
        hostaway_webhook_manager.load_registered_webhook_ids()
        time.sleep(5)
        hostaway_webhook_manager.register_unified_webhook()
