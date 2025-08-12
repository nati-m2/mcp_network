from datetime import datetime

def register_tools(mcp):
    @mcp.tool()
    def get_current_datetime() -> str:
        """
        Returns the current date and time formatted as 'DD.MM.YYYY HH:MM:SS'.
        """
        now = datetime.now()
        return now.strftime("%d.%m.%Y %H:%M:%S")

    @mcp.tool()
    def add(a: int, b: int) -> int:
        """
        Add two numbers and return the result.
        :param a: The first number.
        :param b: The second number.
        """
        return a + b

    # Add a dynamic greeting resource
    @mcp.resource("greeting://{name}")
    def get_greeting(name: str) -> str:
        """Get a personalized greeting"""
        return f"Hello, {name}!"

    # Add a prompt
    @mcp.prompt()
    def greet_user(name: str, style: str = "friendly") -> str:
        """Generate a greeting prompt"""
        styles = {
            "friendly": "Please write a warm, friendly greeting",
            "formal": "Please write a formal, professional greeting",
            "casual": "Please write a casual, relaxed greeting",
        }

        return f"{styles.get(style, styles['friendly'])} for someone named {name}."