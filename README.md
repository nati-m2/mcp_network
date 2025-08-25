
# MCP Network

**MCP Network** is an AI-driven home automation and system management server.
It allows you to control smart home devices, manage Docker containers, monitor system metrics, and automate tasks efficiently.

---

## Key Features

* **Smart Home Control:** Manage lights, AC, fans, doors, and more.
* **Container & Service Management:** Monitor Docker containers, start/stop/restart them as needed.
* **Task Scheduling:** Schedule recurring or one-time automation tasks.
* **AI-Powered System Optimizer:** Automatically detects system issues and recommends corrective actions.
* **Secure Remote Commands:** Execute predefined SSH commands safely on remote machines.
* **Metrics Monitoring:** Track CPU, memory, disk usage, network speed, and other system metrics.

---

## Quick Start

1. **Clone the repository:**

```bash
   git clone https://github.com/yourusername/mcp-network.git
   cd mcp-network
```

2. **Create a `.env` file in the project root:**

```env
   # Home Assistant Configuration
   HOMEASSISTANT_URL=http://192.168.0.100:8123
   HOMEASSISTANT_TOKEN=eyJhbGciOiJIUzI1NiIsInR...

   # Portainer Configuration
   PORTAINER_URL=http://192.168.0.101:9000
   PORTAINER_ACCESS_TOKEN=ptr_5AmW.....

   # Scheduler Settings
   TRIGGER_WEBHOOK_URL=https://example.com/webhook
```

3. **Install **

 ```docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build:
      context: .
    environment:
      - TZ=Asia/Jerusalem
    ports:
      - "8086:8080"
    restart: unless-stopped
    volumes:
      #map app
      - ./mcp-network:/app  
   ```
---

## System Optimization

MCP Network includes an AI-powered system optimizer. It reads system checks from a JSON file and suggests recommended actions, such as starting stopped containers, restarting services, or alerting for resource issues.

### Example `checks.json`

```json
[
  "Check containers and return inactive ones",
  "Verify disk space usage",
  "Check CPU and memory load",
  "Verify important services are running"
]
```
### Example env_config.json
```

{
  "server1": {
    "username": "user",
    "password": "5.....",
    "host": "192.168.0.50",
    "working_dir": "/tmp",
    "metrics": [
      "disk_usage",
      "cpu_load",
      "memory_usage",
      "wifi_status",
      "processes",
      "network",
      "temperature",
      "uptime",
      "docker_containers",
      "disk_inode",
      "network_speed"
    ]
  }
}

```
| Metric             | Command                             | Description                               |
| ------------------ | ----------------------------------- | ----------------------------------------- |
| disk\_usage        | `df -h`                             | Disk space usage                          |
| cpu\_load          | `uptime`                            | CPU load                                  |
| memory\_usage      | `free -h`                           | Memory usage                              |
| wifi\_status       | `iwconfig`                          | Wireless network info                     |
| processes          | `ps aux --sort=-%cpu \| head -n 10` | Top 10 CPU-consuming processes            |
| network            | `ip -s link`                        | Network interface statistics              |
| temperature        | `sensors`                           | System temperatures (requires lm-sensors) |
| uptime             | `uptime -p`                         | System uptime in human-readable format    |
| docker\_containers | `docker ps -a`                      | List all Docker containers                |
| disk\_inode        | `df -i`                             | Inode usage                               |
| network\_speed     | `cat /sys/class/net/eth0/speed`     | Ethernet interface speed in Mb/s          |


The `system_optimizer` tool analyzes these checks and returns results in JSON format for automated or manual execution.

---

## Metrics & Container Management Examples

### Fetch System Metrics

Use the `get_remote_metrics` tool to fetch metrics from a remote environment:

```python
# Fetch all allowed metrics
metrics = get_remote_metrics("server1")

# Fetch a single metric
disk_usage = get_remote_metrics("server1", metrics="disk_usage")
```

**Allowed metrics examples:**
  
If you request a metric not allowed for the environment, you will receive an error message.

---

### Manage Docker Containers

Use the container management tools:

```python
# List all running containers
running_containers = list_containers()

# Start a stopped container
start_container("plex")

# Stop a running container
stop_container("plex")
```

**AI Behavior Example:**

* If a system check finds stopped containers, the AI can ask you:

  `"Container 'plex' is stopped. Do you want to start it?"`

* You can approve, and the AI will execute the action automatically.

---

## Security & Best Practices

* Only allowed SSH commands can be executed on remote machines.
* Keep `.env` files and API tokens private.
* Limit AI actions to predefined system checks to avoid unintended changes.

---

## Creating New Tools

You can easily add custom tools to MCP Network. Follow these steps:

1. **Write your tool script**

   * Create a new Python file in the `modules/` directory, e.g., `modules/my_tool.py`.
   * Define your tool functions using the `@mcp.tool()` decorator. Example:

   ```python
   from datetime import datetime

   def register_tools(mcp):

       @mcp.tool()
       def get_current_datetime() -> str:
           """Returns the current date and time formatted as 'DD.MM.YYYY HH:MM:SS'."""
           now = datetime.now()
           return now.strftime("%d.%m.%Y %H:%M:%S")
   ```

2. **Add dependencies**

   * If your tool requires additional Python packages, add them to the `[project] dependencies` list in `pyproject.toml`:

   ```toml
   dependencies = [
       "mcp[cli]>=1.12.4",
       "requests",
       "colorlog",
       "paramiko",
       "your_new_dependency"
   ]
   ```

3. **Register the tool**

   * Ensure your function is included inside `register_tools(mcp)` so it is loaded when the MCP server starts.

4. **Verify tool loading**

   * Start the MCP server. You should see logs like:

   ```
   🔍 Starting tool loading process...
   ✅ Loaded module: modules.my_tool
   🛠 MCP tools were registered by modules:
       - modules.my_tool
   ```

5. **Inspect before connecting to the AI agent**

   * Run the inspector to verify your tool is correctly loaded and workng:

   ```bash
   npx @modelcontextprotocol/inspector
   ```

---
## License

MIT License – see [LICENSE](LICENSE) for details.

---










