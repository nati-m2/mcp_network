from mcp.server.fastmcp import FastMCP
from modules import homeassistant_tools, docker_tools, generic

# Create an MCP server
mcp = FastMCP("mcp-network")

homeassistant_tools.register_tools(mcp)
docker_tools.register_tools(mcp)
generic.register_tools(mcp)

