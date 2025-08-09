from fastmcp import FastMCP
from modules import homeassistant_tools, docker_tools, generic

mcp = FastMCP("mcp-network")

homeassistant_tools.register_tools(mcp)
docker_tools.register_tools(mcp)
generic.register_tools(mcp)

if __name__ == "__main__":
    print("Starting MCP server... host=0.0.0.0, port=8080")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)