import requests
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

# הגדרות Portainer עם Access Token
PORTAINER_CONFIG = {
    "url": os.getenv('PORTAINER_URL'),
    "access_token": os.getenv('PORTAINER_TOKEN'),  # החלף בטוקן שיצרת ב-Portainer
    "endpoint_id": 2
}

class PortainerAPI:
    def __init__(self):
        self.base_url = PORTAINER_CONFIG["url"]
        self.access_token = PORTAINER_CONFIG["access_token"]
        self.endpoint_id = PORTAINER_CONFIG["endpoint_id"]

    def get_headers(self) -> Dict[str, str]:
        """החזרת headers עם Access Token"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def test_connection(self) -> Dict[str, Any]:
        """בדיקת חיבור וטוקן"""
        url = f"{self.base_url}/api/endpoints"

        try:
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                return {"success": True, "endpoints": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}", "message": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_containers(self, all_containers: bool = False) -> Dict[str, Any]:
        """קבלת רשימת קונטיינרים"""
        url = f"{self.base_url}/api/endpoints/{self.endpoint_id}/docker/containers/json"
        params = {"all": "true"} if all_containers else {}

        try:
            response = requests.get(url, headers=self.get_headers(), params=params, timeout=10)
            if response.status_code == 200:
                return {"success": True, "containers": response.json()}
            elif response.status_code == 401:
                return {"success": False, "error": "Unauthorized - Check your access token"}
            elif response.status_code == 404:
                return {"success": False, "error": f"Endpoint {self.endpoint_id} not found"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def start_container(self, container_id: str) -> Dict[str, Any]:
        """הפעלת קונטיינר"""
        url = f"{self.base_url}/api/endpoints/{self.endpoint_id}/docker/containers/{container_id}/start"

        try:
            response = requests.post(url, headers=self.get_headers(), timeout=10)
            if response.status_code == 204:
                return {"success": True}
            elif response.status_code == 304:
                return {"success": True, "message": "Container already running"}
            elif response.status_code == 404:
                return {"success": False, "error": "Container not found"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_container(self, container_id: str) -> Dict[str, Any]:
        """עצירת קונטיינר"""
        url = f"{self.base_url}/api/endpoints/{self.endpoint_id}/docker/containers/{container_id}/stop"

        try:
            response = requests.post(url, headers=self.get_headers(), timeout=10)
            if response.status_code == 204:
                return {"success": True}
            elif response.status_code == 304:
                return {"success": True, "message": "Container already stopped"}
            elif response.status_code == 404:
                return {"success": False, "error": "Container not found"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def restart_container(self, container_id: str) -> Dict[str, Any]:
        """הפעלה מחדש של קונטיינר"""
        url = f"{self.base_url}/api/endpoints/{self.endpoint_id}/docker/containers/{container_id}/restart"

        try:
            response = requests.post(url, headers=self.get_headers(), timeout=15)
            if response.status_code == 204:
                return {"success": True}
            elif response.status_code == 404:
                return {"success": False, "error": "Container not found"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_container_by_name(self, container_name: str) -> Optional[Dict[str, Any]]:
        """חיפוש קונטיינר לפי שם"""
        result = self.list_containers(all_containers=True)
        if not result["success"]:
            return None

        for container in result["containers"]:
            names = container.get("Names", [])
            # בדיקה עם שם נקי (בלי סלש) ושם מלא
            clean_names = [name.lstrip('/') for name in names]
            if container_name in clean_names or any(container_name in name for name in names):
                return container
        return None

    def get_container_logs(self, container_id: str, lines: int = 100) -> Dict[str, Any]:
        """קבלת לוגים של קונטיינר"""
        url = f"{self.base_url}/api/endpoints/{self.endpoint_id}/docker/containers/{container_id}/logs"
        params = {
            "stdout": "true",
            "stderr": "true",
            "tail": str(lines),
            "timestamps": "true"
        }

        try:
            response = requests.get(url, headers=self.get_headers(), params=params, timeout=15)
            if response.status_code == 200:
                return {"success": True, "logs": response.text}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """קבלת סטטיסטיקות של קונטיינר"""
        url = f"{self.base_url}/api/endpoints/{self.endpoint_id}/docker/containers/{container_id}/stats"
        params = {"stream": "false"}

        try:
            response = requests.get(url, headers=self.get_headers(), params=params, timeout=15)
            if response.status_code == 200:
                return {"success": True, "stats": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


    # יצירת instance גלובלי
portainer = PortainerAPI()

def register_tools(mcp):
    @mcp.tool()
    def start_container(container_name: str) -> str:
        """Starts a Docker container using Portainer API."""
        try:
            container = portainer.get_container_by_name(container_name)
            if not container:
                return f"❌ Container '{container_name}' not found."

            container_id = container["Id"]
            result = portainer.start_container(container_id)

            if result["success"]:
                message = result.get("message", "")
                if message:
                    return f"✅ Container '{container_name}': {message}"
                else:
                    return f"✅ Container '{container_name}' started successfully."
            else:
                return f"❌ Error starting '{container_name}': {result['error']}"

        except Exception as e:
            return f"❌ Error: {str(e)}"


    @mcp.tool()
    def stop_container(container_name: str) -> str:
        """Stops a Docker container using Portainer API."""
        try:
            container = portainer.get_container_by_name(container_name)
            if not container:
                return f"❌ Container '{container_name}' not found."

            container_id = container["Id"]
            result = portainer.stop_container(container_id)

            if result["success"]:
                message = result.get("message", "")
                if message:
                    return f"✅ Container '{container_name}': {message}"
                else:
                    return f"✅ Container '{container_name}' stopped successfully."
            else:
                return f"❌ Error stopping '{container_name}': {result['error']}"

        except Exception as e:
            return f"❌ Error: {str(e)}"


    @mcp.tool()
    def restart_container(container_name: str) -> str:
        """Restarts a Docker container using Portainer API."""
        try:
            container = portainer.get_container_by_name(container_name)
            if not container:
                return f"❌ Container '{container_name}' not found."

            container_id = container["Id"]
            result = portainer.restart_container(container_id)

            if result["success"]:
                return f"✅ Container '{container_name}' restarted successfully."
            else:
                return f"❌ Error restarting '{container_name}': {result['error']}"

        except Exception as e:
            return f"❌ Error: {str(e)}"


    @mcp.tool()
    def list_containers(all_containers: bool = False) -> str:
        """Lists Docker containers using Portainer API."""
        try:
            result = portainer.list_containers(all_containers)
            if not result["success"]:
                return f"❌ Error listing containers: {result['error']}"

            containers = result["containers"]
            if not containers:
                return "📦 No containers found."

            output = "📦 **Containers:**\n"

            running_containers = []
            stopped_containers = []

            for container in containers:
                name = container["Names"][0].lstrip('/') if container["Names"] else "unnamed"
                state = container["State"]
                status = container["Status"]
                image = container["Image"]

                container_info = f"   • **{name}** ({image})\n     Status: {status}"

                if state == "running":
                    running_containers.append(container_info)
                else:
                    stopped_containers.append(container_info)

            if running_containers:
                output += f"\n🟢 **Running ({len(running_containers)}):**\n"
                output += "\n".join(running_containers)

            if stopped_containers and all_containers:
                output += f"\n\n🔴 **Stopped ({len(stopped_containers)}):**\n"
                output += "\n".join(stopped_containers)

            return output

        except Exception as e:
            return f"❌ Error: {str(e)}"


    @mcp.tool()
    def get_container_status(container_name: str) -> str:
        """Gets detailed status of a Docker container using Portainer API."""
        try:
            container = portainer.get_container_by_name(container_name)
            if not container:
                return f"❌ Container '{container_name}' not found."

            name = container["Names"][0].lstrip('/') if container["Names"] else "unnamed"
            state = container["State"]
            status = container["Status"]
            image = container["Image"]
            ports = container.get("Ports", [])

            output = f"📊 **Container Status: {name}**\n"
            output += f"   • **State:** {state}\n"
            output += f"   • **Status:** {status}\n"
            output += f"   • **Image:** {image}\n"

            if ports:
                port_info = []
                for port in ports:
                    if "PublicPort" in port and "PrivatePort" in port:
                        port_info.append(f"{port['PublicPort']}→{port['PrivatePort']}")
                    elif "PrivatePort" in port:
                        port_info.append(f"{port['PrivatePort']}")
                if port_info:
                    output += f"   • **Ports:** {', '.join(port_info)}\n"

            # ניסיון לקבל סטטיסטיקות אם רץ
            if state == "running":
                stats_result = portainer.get_container_stats(container["Id"])
                if stats_result["success"]:
                    stats = stats_result["stats"]
                    if "memory" in stats and "usage" in stats["memory"]:
                        memory_usage = stats["memory"]["usage"]
                        memory_limit = stats["memory"].get("limit", 0)

                        if memory_limit > 0:
                            memory_mb = round(memory_usage / 1024 / 1024, 1)
                            memory_percent = round((memory_usage / memory_limit) * 100, 1)
                            output += f"   • **Memory:** {memory_mb} MB ({memory_percent}%)\n"

            return output

        except Exception as e:
            return f"❌ Error: {str(e)}"


    @mcp.tool()
    def get_container_logs(container_name: str, lines: int = 50) -> str:
        """Gets the last N lines of logs from a Docker container."""
        try:
            container = portainer.get_container_by_name(container_name)
            if not container:
                return f"❌ Container '{container_name}' not found."

            container_id = container["Id"]
            result = portainer.get_container_logs(container_id, lines)

            if result["success"]:
                logs = result["logs"]
                if not logs.strip():
                    return f"📝 No logs found for '{container_name}'"

                # ניקוי תווי בקרה מיותרים מהלוגים
                clean_logs = logs.replace('\x01\x00\x00\x00', '').replace('\x02\x00\x00\x00', '')

                return f"📝 **Last {lines} lines of logs for '{container_name}':**\n```\n{clean_logs}\n```"
            else:
                return f"❌ Error getting logs for '{container_name}': {result['error']}"

        except Exception as e:
            return f"❌ Error: {str(e)}"


    @mcp.tool()
    def test_portainer_connection() -> str:
        """Tests the connection to Portainer API and validates access token."""
        try:
            # בדיקת חיבור בסיסי
            connection_test = portainer.test_connection()
            if not connection_test["success"]:
                return f"❌ Connection failed: {connection_test['error']}"

            # בדיקת רשימת קונטיינרים
            containers_test = portainer.list_containers(all_containers=False)
            if containers_test["success"]:
                container_count = len(containers_test["containers"])
                endpoint_count = len(connection_test["endpoints"])
                return f"✅ Successfully connected to Portainer!\n📦 Found {container_count} running containers on {endpoint_count} endpoint(s)."
            else:
                return f"⚠️ Connected to Portainer but failed to list containers: {containers_test['error']}"

        except Exception as e:
            return f"❌ Connection test failed: {str(e)}"