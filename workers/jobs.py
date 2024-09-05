from queue import Queue

# Create a global job queue for processing Hostaway webhook payloads
# Each queue item is a Hostaway webhook payload
hostaway_webhook_queue = Queue()

# Create a global job queue for processing Slack slash command payloads
# Each queue item is a tuple: (slack command, request)
slack_command_queue = Queue()
