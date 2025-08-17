import os
import json
from datetime import datetime
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(BASE_DIR, 'tasks.json')
TRIGGER_WEBHOOK_URL = os.getenv('TRIGGER_WEBHOOK_URL')
DATE_FORMAT = "%d.%m.%Y %H:%M:%S"

# ---------------- Scheduler ----------------

def schedule_task(task):
    """Schedule a task using APScheduler (date or cron) with misfire handling and automatic removal for 'once' tasks."""
    task_type = task.get("type", "once")
    prompt = task["prompt"]

    if task_type == "once":
        run_time = datetime.strptime(task["time"], DATE_FORMAT)
        trigger = DateTrigger(run_date=run_time)

        def job_wrapper():
            try:
                send_webhook_trigger(prompt)
            finally:
                tasks = load_tasks()
                tasks = [t for t in tasks if not (t.get("type") == "once" and t.get("prompt") == prompt and t.get("time") == task["time"])]
                save_tasks(tasks)

        scheduler.add_job(job_wrapper, trigger, misfire_grace_time=300)  # 5 דקות
    elif task_type == "cron":
        cron_expr = task["cron"]
        trigger = CronTrigger.from_crontab(cron_expr)
        scheduler.add_job(lambda: send_webhook_trigger(prompt), trigger, misfire_grace_time=300)

# ---------------- File Handling ----------------

def load_tasks():
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
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# ---------------- Webhook ----------------

def send_webhook_trigger(prompt):
    try:
        resp = requests.post(TRIGGER_WEBHOOK_URL, json={"prompt": prompt}, timeout=10)
        resp.raise_for_status()
        print(f"[{datetime.now()}] ✅ Webhook triggered: {prompt}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error triggering webhook for '{prompt}': {e}")

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.print_jobs()

def load_and_schedule_all():
    tasks = load_tasks()
    for task in tasks:
        schedule_task(task)

# ---------------- MCP Tools ----------------

def register_tools(mcp):

    @mcp.tool()
    def add_scheduled_task(prompt: str, run_time: str) -> str:
        """
        MCP Tool: Schedule a new task to be executed at a specific date and time.

        Args:
            prompt (str): The action or instruction to execute.
            run_time (str): The date and time for execution in the format 'DD.MM.YYYY HH:MM:SS'.

        Returns:
            str: Success message if the task was added, or error message if the date format is invalid.
        """
        try:
            datetime.strptime(run_time, DATE_FORMAT)
        except ValueError:
            return f"❌ Invalid datetime format. Use '{DATE_FORMAT}'"

        tasks = load_tasks()
        task = {"prompt": prompt, "type": "once", "time": run_time}
        tasks.append(task)
        save_tasks(tasks)
        schedule_task(task)
        return f"✅ One-time task added: '{prompt}' at {run_time}"

    @mcp.tool()
    def add_cron_task(prompt: str, cron_expr: str) -> str:
        """
        MCP Tool: Schedule a recurring task using a CRON expression.

        Args:
            prompt (str): The action or instruction to execute.
            cron_expr (str): CRON expression defining the schedule (e.g., "0 7 * * *" for every day at 07:00).

        Returns:
            str: Success message with the CRON expression or error if the expression is invalid.

        Example:
            add_cron_task("Turn on lights", "0 18 * * *")
            # Schedules the task to run every day at 18:00
        """
        try:
            CronTrigger.from_crontab(cron_expr)
        except Exception:
            return "❌ Invalid CRON expression."

        tasks = load_tasks()
        task = {"prompt": prompt, "type": "cron", "cron": cron_expr}
        tasks.append(task)
        save_tasks(tasks)
        schedule_task(task)
        return f"✅ CRON task added: '{prompt}' ({cron_expr})"

    @mcp.tool()
    def list_scheduled_tasks() -> str:
        """
        MCP Tool: List all currently scheduled tasks.

        Returns:
            str: Numbered list of tasks with their type (One-time, CRON, Interval) and schedule details.
                 Returns a message if no tasks are scheduled.

        Example:
            list_scheduled_tasks()
        """
        tasks = load_tasks()
        if not tasks:
            return "No scheduled tasks."
        lines = []
        for i, task in enumerate(tasks, 1):
            if task["type"] == "once":
                lines.append(f"{i}. [One-time] {task['prompt']} at {task['time']}")
            elif task["type"] == "cron":
                lines.append(f"{i}. [CRON] {task['prompt']} ({task['cron']})")
            elif task["type"] == "interval":
                lines.append(
                    f"{i}. [Interval] {task['prompt']} every {task.get('days', 0)}d {task.get('hours', 0)}h {task.get('minutes', 0)}m {task.get('seconds', 0)}s")
        return "\n".join(lines)

    @mcp.tool()
    def delete_scheduled_task(task_number: int) -> str:
        """
        MCP Tool: Delete a scheduled task by its list number.

        Args:
            task_number (int): The 1-based index of the task in the list of scheduled tasks.

        Returns:
            str: Success message with details of the removed task or error if the number is invalid.

        Example:
            delete_scheduled_task(2)
            # Removes the second task in the scheduled list
        """
        tasks = load_tasks()
        if task_number < 1 or task_number > len(tasks):
            return "❌ Invalid task number."
        removed = tasks.pop(task_number - 1)
        save_tasks(tasks)
        return f"✅ Removed task: '{removed['prompt']}'"

# ---------------- Initialize ----------------

# Load existing tasks from file and schedule them
load_and_schedule_all()
print(f"✅ [Scheduler] All tasks loaded and scheduled.")