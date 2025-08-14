import json
from pathlib import Path
from typing import Dict, Any
import paramiko

CONFIG_FILE = Path(__file__).parent / "env_config.json"

def load_env_config() -> Dict[str, Any]:
    """Loads the configuration file, creates an empty dict if it does not exist."""
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text("{}", encoding="utf-8")
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def run_ssh_command(connection_info: dict, command: str, working_dir: str = "") -> str:
    """Runs a command on a remote host via SSH and returns the output."""
    username = connection_info.get("username")
    password = connection_info.get("password")
    host = connection_info.get("host")

    if not all([username, password, host, command]):
        raise ValueError("Missing required connection information.")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if working_dir:
        command = f"cd {working_dir} && {command}"

    try:
        ssh.connect(hostname=host, username=username, password=password, timeout=10)
        stdin, stdout, stderr = ssh.exec_command(command)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        ssh.close()

        if error:
            return f"Error: {error}"
        return output

    except Exception as e:
        return f"SSH connection failed: {str(e)}"

def run_metric_ssh(env_data: dict, metric: str) -> str:
    """Runs a single metric command via SSH on the remote host."""
    metric_commands = {
        "disk_usage": "df -h",  # דיסק – שימושי
        "cpu_load": "uptime",  # עומס CPU
        "memory_usage": "free -h",  # זיכרון
        "wifi_status": "iwconfig",  # מצב Wi-Fi
        "processes": "ps aux --sort=-%cpu | head -n 10",  # 10 תהליכים הכי כבדים ב-CPU
        "network": "ip -s link",  # סטטיסטיקת רשת
        "temperature": "sensors",  # טמפרטורות אם lm-sensors מותקן
        "uptime": "uptime -p",  # זמן פעילות מערכת בפורמט קריא
        "docker_containers": "docker ps -a",  # רשימת קונטיינרים Docker
        "disk_inode": "df -i",  # Inode usage
        "network_speed": "cat /sys/class/net/eth0/speed"  # מהירות קו את'רנט (Mb/s)
    }

    if metric not in metric_commands:
        return f"❌ Unknown metric '{metric}'"

    return run_ssh_command(env_data, metric_commands[metric])

def register_tools(mcp):
    @mcp.tool()
    def get_remote_metrics(env_name: str, metric: str = "") -> Dict[str, str]:
        """
        Returns predefined metrics from a remote host.

        Args:
            env_name (str): environment name from config
            metric (str): single metric to fetch; fetches all allowed if empty

        Returns:
            Dict[str, str]: metric name -> output
        """
        config = load_env_config()
        if env_name not in config:
            return {"error": f"Environment '{env_name}' not found"}

        env_data = config[env_name]
        allowed_metrics = env_data.get("metrics", [])
        if not allowed_metrics:
            return {"error": f"No metrics defined for environment '{env_name}'"}

        # אם metrics ריקה, נריץ את כל ה־allowed metrics
        requested_metrics = [metric] if metric else allowed_metrics

        results = {}
        for m in requested_metrics:
            if m not in allowed_metrics:
                results[m] = f"❌ Metric '{m}' is not allowed for this environment"
            else:
                results[m] = run_metric_ssh(env_data, m)

        return results

