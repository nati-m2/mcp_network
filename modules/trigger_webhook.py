import requests

def register_tools(mcp):
    @mcp.tool()
    def trigger_webhook(url: str, prompt: str) -> str:
        """
        Trigger a webhook by sending a POST request with JSON body containing the prompt.
        :param url: The webhook URL to send to
        :param prompt: The prompt/message to send in JSON
        """
        try:
            payload = {"chatInput": prompt}
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return f"✅ Webhook triggered successfully, status code: {response.status_code}"
        except Exception as e:
            return f"❌ Failed to trigger webhook: {e}"

