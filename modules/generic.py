import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKS_FILE = os.path.join(BASE_DIR, 'checks.json')

def register_tools(mcp):

    @mcp.tool()
    def get_current_datetime() -> str:
        """Returns the current date and time formatted as 'DD.MM.YYYY HH:MM:SS'."""
        now = datetime.now()
        return now.strftime("%d.%m.%Y %H:%M:%S")

    @mcp.tool()
    def add(a: int, b: int) -> int:
        """Add two numbers and return the result."""
        return a + b

    @mcp.resource("greeting://{name}")
    def get_greeting(name: str) -> str:
        """Get a personalized greeting"""
        return f"Hello, {name}!"

   # --- Helper to load or create checks.json ---
    def get_system_checks(config_file: str = CHECKS_FILE):
        if not os.path.exists(config_file):
            with open(config_file, "w") as f:
                json.dump([
                    "Check all containers and return inactive ones",
                    "Check disk space and report if below threshold",
                    "Check important services and restart if not running"
                ], f, indent=2)
        with open(config_file, "r") as f:
            checks = json.load(f)
        return checks

    @mcp.tool()
    def system_optimizer() -> dict:
        """
        Analyze system checks and return recommended actions.
        Returns a JSON object with 'checks to do'.
        """
        checks = get_system_checks()
        checks_text = "\n".join(checks)
        
        return {
            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "checks": checks,
        }

