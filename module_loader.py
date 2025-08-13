import importlib
import pkgutil
import modules
from fastmcp import FastMCP
from logger import get_logger

logger = get_logger()

def load_modules(mcp: FastMCP):
    logger.info("🔍 Starting tool loading process...")
    loaded_modules = []
    registered_tools = []

    for loader, module_name, is_pkg in pkgutil.iter_modules(modules.__path__):
        full_name = f"modules.{module_name}"
        try:
            module = importlib.import_module(full_name)
            loaded_modules.append(full_name)
            logger.info(f"✅ Loaded module: {full_name}")

            # Register tools if function exists
            if hasattr(module, "register_tools"):
                module.register_tools(mcp)
                registered_tools.append(full_name)

            # Start scheduler if function exists
            if hasattr(module, "start_scheduler"):
                module.start_scheduler(mcp)

        except Exception as e:
            logger.error(f"❌ Failed to load module {full_name}: {e}")

    if loaded_modules:
        logger.info("📦 Modules loaded successfully:")
        for mod in loaded_modules:
            logger.info(f"    - {mod}")
    else:
        logger.warning("⚠ No modules were loaded from tools directory.")

    if registered_tools:
        logger.info("🛠 MCP tools were registered by modules:")
        for mod in registered_tools:
            logger.info(f"    - {mod}")
    else:
        logger.warning("⚠ No MCP tools were registered.")

    return loaded_modules, registered_tools
