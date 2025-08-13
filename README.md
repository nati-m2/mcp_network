
MCP Network is an AI-driven home automation and system management server. It allows you to control smart home devices, manage Docker containers, and automate system tasks.

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

System Optimization

Define system checks in checks.json to let the AI analyze your system and suggest actions like starting containers or restarting services.

Example checks.json:
   ```bash
[
  "Check containers and return inactive ones",
  "Verify disk space usage",
  "Check CPU and memory load",
  "Verify important services are running"
]


The system_optimizer tool reads this file and returns recommended actions in JSON format.


