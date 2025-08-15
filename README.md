Here’s an updated `README.md` including a **Metrics & Container Management Examples** section with practical usage instructions:

---

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
   PORTAINER_USERNAME=admin
   PORTAINER_PASSWORD=dRuP@ssw0rd.....
   PORTAINER_URL=http://192.168.0.101:9000

   # Scheduler Settings
   TRIGGER_INTERVAL=10
   TRIGGER_WEBHOOK_URL=https://example.com/webhook
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run MCP Network:**

   ```bash
   python main.py
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

The `system_optimizer` tool analyzes these checks and returns results in JSON format for automated or manual execution.

---

## Metrics & Container Management Examples

### Fetch System Metrics

Use the `get_remote_metrics` tool to fetch metrics from a remote environment:

```python
# Fetch all allowed metrics
metrics = get_remote_metrics("omv")

# Fetch a single metric
disk_usage = get_remote_metrics("omv", metrics="disk_usage")
```

**Allowed metrics examples:**

* `disk_usage` → Disk space usage (`df -h`)
* `cpu_load` → CPU load (`uptime`)
* `memory_usage` → Memory usage (`free -h`)
* `wifi_status` → Wireless network info (`iwconfig`)

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

## Contributing

Contributions are welcome! Please open issues or pull requests for improvements, bug fixes, or new features.

---

## License

MIT License – see [LICENSE](LICENSE) for details.

---

Do you want me to add that diagram?
