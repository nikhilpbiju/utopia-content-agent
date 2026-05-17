# slack_sender.py
# Sends a formatted Slack message using an Incoming Webhook.
# Slack webhooks are the simplest possible Slack integration —
# no auth flow, just a URL that accepts POST requests.

import requests
import json
# requests is a Python library for making HTTP requests.
# We use it to send data to the Slack webhook URL.

def send_to_slack(
    webhook_url: str,
    post_text: str,
    launch_stage: str,
    attendee: str,
    topic: str
) -> bool:
    """
    Sends the LinkedIn post draft to a Slack channel.
    Returns True if successful, False if not.
    """
    
    # Slack messages can be formatted using "blocks" —
    # a structured layout system. But for simplicity,
    # we'll use a plain text message with some formatting.
    # This is a deliberate scope decision: blocks are more
    # complex and can break. Plain text always works.
    
    message = {
        "text": (
            f"*New content from Content Agent*\n"
            f"Meeting with: *{attendee}* · Topic: {topic}\n"
            f"LAUNCH stage: *{launch_stage}*\n\n"
            f"*LinkedIn Post Draft:*\n{post_text}"
        )
    }
    # The * * syntax makes text bold in Slack.
    # \n is a newline character.
    
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(message),
            headers={"Content-Type": "application/json"}
            # We tell Slack we're sending JSON via the Content-Type header.
        )
        # Slack returns "ok" as plain text if the message was received.
        return response.status_code == 200
        # status_code 200 means "success" in HTTP.
        # Any other code means something went wrong.
    
    except Exception as e:
        print(f"Slack error: {e}")
        return False