import os
import json
import threading
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(BASE_DIR, 'tasks.json')

TRIGGER_INTERVAL = float(os.getenv('TRIGGER_INTERVAL', 30))
TRIGGER_WEBHOOK_URL = os.getenv('TRIGGER_WEBHOOK_URL')

DATE_FORMAT = "%d.%m.%Y %H:%M:%S"  # פורמט תאריך מלא עם שניות

# ---------------- File Handling ----------------

def load_tasks():
    """Load tasks from file, create an empty one if missing or invalid."""
    if not os.path.exists(TASKS_FILE):
        save_tasks([])
        return []

    with open(TASKS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            save_tasks([])
            return []

def save_tasks(tasks):
    """Save tasks list to file."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# ---------------- Task Management ----------------

def add_task(prompt, run_time):
    """
    Add a new scheduled task.
    :param prompt: The action to perform
    :param run_time: The datetime string in format '%d.%m.%Y %H:%M:%S'
    """
    tasks = load_tasks()
    tasks.append({"prompt": prompt, "time": run_time})
    save_tasks(tasks)

def send_webhook_trigger(prompt):
    """Send the prompt to the webhook URL as a POST request."""
    try:
        resp = requests.post(TRIGGER_WEBHOOK_URL, json={"prompt": prompt}, timeout=10)
        resp.raise_for_status()
        print(f"Webhook triggered successfully for prompt: {prompt}")
    except Exception as e:
        print(f"Error triggering webhook for prompt '{prompt}': {e}")

def scheduler_loop(mcp):
    """Background loop to check and run tasks when their time arrives."""
    while True:
        now = datetime.now()
        tasks = load_tasks()
        updated_tasks = []

        #print(f"Checking tasks at {now.strftime(DATE_FORMAT)}")

        for task in tasks:
            try:
                task_time = datetime.strptime(task["time"], DATE_FORMAT)
            except ValueError:
                print(f"Invalid time format for task: {task}")
                continue

            if now >= task_time:
                print(f"Executing scheduled task: {task['prompt']}")
                try:
                    send_webhook_trigger(task["prompt"])  # שולח את הפרומפט דרך ה-webhook
                except Exception as e:
                    print(f"Error executing task: {e}")
            else:
                updated_tasks.append(task)

        save_tasks(updated_tasks)
        time.sleep(TRIGGER_INTERVAL)

def start_scheduler(mcp):
    threading.Thread(target=scheduler_loop, args=(mcp,), daemon=True).start()

def register_tools(mcp):
    @mcp.tool()
    def add_scheduled_task(prompt: str, run_time: str) -> str:
        try:
            datetime.strptime(run_time, DATE_FORMAT)
        except ValueError:
            return f"❌ Invalid datetime format. Use '{DATE_FORMAT}'"

        add_task(prompt, run_time)
        return f"✅ Task added: '{prompt}' at {run_time}"

    @mcp.tool()
    def list_scheduled_tasks() -> str:
        tasks = load_tasks()
        if not tasks:
            return "No scheduled tasks."
        lines = [f"{i+1}. {task['prompt']} at {task['time']}" for i, task in enumerate(tasks)]
        return "\n".join(lines)

    @mcp.tool()
    def delete_scheduled_task(task_number: int) -> str:
        tasks = load_tasks()
        if task_number < 1 or task_number > len(tasks):
            return "❌ Invalid task number."
        removed = tasks.pop(task_number - 1)
        save_tasks(tasks)
        return f"✅ Removed task: '{removed['prompt']}' scheduled at {removed['time']}"
