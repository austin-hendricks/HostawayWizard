from queue import Queue

# Create a global job queue for processing Hostaway webhook payloads
hostaway_webhook_queue = Queue()
