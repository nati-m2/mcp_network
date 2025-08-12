from fastmcp import FastMCP
import threading
from modules import homeassistant_tools, docker_tools, generic,taskScheduler, trigger_webhook

mcp = FastMCP("mcp-network")

homeassistant_tools.register_tools(mcp)
docker_tools.register_tools(mcp)
generic.register_tools(mcp)
trigger_webhook.register_tools(mcp)
taskScheduler.register_tools(mcp)
taskScheduler.start_scheduler(mcp)


if __name__ == "__main__":
    print("Starting MCP server... host=0.0.0.0, port=8080")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)