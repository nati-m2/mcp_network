from fastmcp import FastMCP
from module_loader import load_modules

mcp = FastMCP("mcp-network")

# load modules and tools
load_modules(mcp)

if __name__ == "__main__":
    print("🚀 Starting MCP server... host=0.0.0.0, port=8080")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
