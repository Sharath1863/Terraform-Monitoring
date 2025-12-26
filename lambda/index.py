import json
import urllib.request
import os
import time
import boto3
from datetime import datetime

# ===== AWS CLIENTS =====
ssm = boto3.client("ssm")
dynamodb = boto3.client("dynamodb")

# ===== CONFIG =====
TABLE_NAME = "website-monitor-state"

BOT_TOKEN_PARAM = "/central-monitor/telegram/bot_token"
CHAT_ID_PARAM  = "/central-monitor/telegram/chat_id"

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

# ===== SSM HELPERS =====
def get_secret(param_name):
    response = ssm.get_parameter(
        Name=param_name,
        WithDecryption=True
    )
    return response["Parameter"]["Value"]

BOT_TOKEN = get_secret(BOT_TOKEN_PARAM)
CHAT_ID  = get_secret(CHAT_ID_PARAM)

# ===== TELEGRAM =====
def send_telegram(message):
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        api,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req, timeout=10)

# ===== DYNAMODB HELPERS =====
def get_last_state(project_name):
    resp = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={"monitor_id": {"S": project_name}}
    )
    return resp.get("Item", {}).get("status", {}).get("S")

def save_state(project_name, state):
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            "monitor_id": {"S": project_name},
            "status": {"S": state},
            "updated_at": {"S": datetime.utcnow().isoformat()}
        }
    )

# ===== HEALTH CHECK =====
def check_website(url):
    try:
        start = time.time()
        resp = urllib.request.urlopen(url, timeout=10)
        latency = round((time.time() - start) * 1000)
        return "UP", resp.getcode(), latency
    except Exception as e:
        return "DOWN", str(e), None

# ===== LAMBDA HANDLER =====
def lambda_handler(event, context):
    for project in PROJECTS:
        name = project["name"]
        url = project["url"]

        current_state, info, latency = check_website(url)
        last_state = get_last_state(name)

        # First run
        if last_state is None:
            save_state(name, current_state)
            continue

        # State change
        if current_state != last_state:
            if current_state == "DOWN":
                send_telegram(
                    f"🔴 WEBSITE DOWN\n"
                    f"Project: {name}\n"
                    f"Error: {info}"
                )
            else:
                send_telegram(
                    f"🟢 WEBSITE UP\n"
                    f"Project: {name}\n"
                    f"Latency: {latency} ms"
                )

            save_state(name, current_state)

    return {"status": "done"}
