import json
import urllib.request
import os
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

PROJECTS = [
    {
        "name": "Cogosmart",
        "url": "https://cogosmart.com/health"
    },

    {
        "name": "Onstru",
        "url": "https://onstru.com/health"
    }
]

def send_telegram(message):
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(api, data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=10)

def lambda_handler(event, context):
    for project in PROJECTS:
        try:
            start = time.time()
            resp = urllib.request.urlopen(project["url"], timeout=10)
            status = resp.getcode()
            latency = round((time.time() - start) * 1000)

            if status != 200:
                send_telegram(
                    f"🚨 WEBSITE DOWN\n"
                    f"Project: {project['name']}\n"
                    f"Status: {status}"
                )

        except Exception as e:
            send_telegram(
                f"🚨 WEBSITE DOWN\n"
                f"Project: {project['name']}\n"
                f"Error: {str(e)}"
            )

    return {"status": "done"}
