import requests
import logging
import json
from src.settings import IMAGE, FALLBACK_LOGO

def read_settings():
    with open("db/settings.json") as f:
        return json.load(f)
    
def SendDiscordWebhook(alert, islogo, airline):
    try:
        if islogo[1] is True:
            print(f"Sending notification with image for {airline}")

            payload = {
                "content": f"✈️ **Flight Detected**",
                "embeds": [
                    {
                        "description": alert,
                        "image": {
                            "url": f"attachment://{IMAGE}"
                        }
                    }
                ]
            }

            with open(IMAGE, "rb") as f:
                files = {
                    "file": (IMAGE, f, "image/jpeg")
                }

                r = requests.post(
                    read_settings()["discord_webhook"],
                    data={"payload_json": json.dumps(payload)},
                    files=files
                )

        else:
            payload = {
                "content": f"✈️ **Flight Detected**",
                "embeds": [
                    {
                        "description": alert,
                        "image": {
                            "url": f"attachment://{FALLBACK_LOGO}"
                        }
                    }
                ]
            }

            with open(FALLBACK_LOGO, "rb") as f:
                files = {
                    "file": (FALLBACK_LOGO, f, "image/jpeg")
                }

                r = requests.post(
                    read_settings()["discord_webhook"],
                    data={"payload_json": json.dumps(payload)},
                    files=files
                )

        if r.status_code in (200, 204):
            print(f"Discord notification sent successfully for {airline}")
        else:
            logging.error(f"Discord webhook failed: {r.status_code} - {r.text}")

    except Exception as e:
        logging.error(f"Error in send_notification(): {e}")
