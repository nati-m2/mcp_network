הטקסט שלך קצת נשבר במבנה ה־Markdown, אז סידרתי לך אותו עם פורמט נכון:

````markdown
# MCP Network

MCP Network is an AI-driven home automation and system management server.  
It allows you to control smart home devices, manage Docker containers, and automate system tasks.

## Key Features
- Control lights, AC, fans, doors, and more.
- Monitor and manage Docker containers and services.
- Schedule tasks for automation.
- AI-powered system optimizer that detects issues and recommends fixes.
- Secure execution of allowed SSH commands on remote machines.

## Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-network.git
````

2. Create a `.env` file in the project root with the following structure:

   ```env
   # Home Assistant Configuration
   HOMEASSISTANT_URL=http://192.168.0.100:8123
   HOMEASSISTANT_TOKEN=eyJhbGciOiJIUzI1NiIsInR...

   # Portainer Configuration
   PORTAINER_USERNAME=admin
   PORTAINER_PASSWORD=dRuP@ssw0rd
   PORTAINER_URL=http://192.168.0.101:9000

   # Scheduler
   TRIGGER_INTERVAL=10
   TRIGGER_WEBHOOK_URL=https://example.com/webhook
   ```

## System Optimization

Define system checks in `checks.json` to let the AI analyze your system and suggest actions like starting containers or restarting services.

Example `checks.json`:

```json
[
  "Check containers and return inactive ones",
  "Verify disk space usage",
  "Check CPU and memory load",
  "Verify important services are running"
]
```

The `system_optimizer` tool reads this file and returns recommended actions in JSON format.


