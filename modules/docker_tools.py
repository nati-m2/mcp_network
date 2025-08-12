import requests
import os
import threading
from dotenv import load_dotenv
load_dotenv()

PORTAINER_URL = os.getenv('PORTAINER_URL').rstrip("/")
USERNAME = os.getenv('PORTAINER_USERNAME').strip()
PASSWORD = os.getenv('PORTAINER_PASSWORD').strip()

class PortainerAPI:
    def __init__(self, url, username, password):
        self.url = url.rstrip("/")
        self.base_url = f"{self.url}/api"
        self.username = username
        self.password = password
        self.token = None
        self.endpoint_id = None
        self.headers = None
        self.connect()

    def connect(self):
        auth_payload = {"Username": self.username, "Password": self.password}
        r = requests.post(f"{self.base_url}/authenticate", json=auth_payload)
        if r.status_code == 404:
            r = requests.post(f"{self.base_url}/auth", json=auth_payload)
        r.raise_for_status()
        self.token = r.json().get("jwt")
        if not self.token:
            raise ValueError(f"Failed to get JWT token: {r.text}")
        self.headers = {"Authorization": f"Bearer {self.token}"}

        endpoints = self._get("/endpoints")
        if not endpoints:
            raise ValueError("No endpoints found in Portainer")
        self.endpoint_id = endpoints[0]["Id"]

    def _get(self, path, **kwargs):
        kwargs.setdefault("timeout", 30)  # Default timeout for GET requests
        r = requests.get(f"{self.base_url}{path}", headers=self.headers, **kwargs)
        r.raise_for_status()
        return r.json()

    def _post(self, path, **kwargs):
        kwargs.setdefault("timeout", 30)  # Default timeout for POST requests
        r = requests.post(f"{self.base_url}{path}", headers=self.headers, **kwargs)
        r.raise_for_status()
        return r.json() if r.text else {}

    def _post_nojson(self, path, **kwargs):
        kwargs.setdefault("timeout", 30)  # Default timeout for POST requests
        r = requests.post(f"{self.base_url}{path}", headers=self.headers, **kwargs)
        r.raise_for_status()
        return r.text

    def _post_action(self, container_id, action):
        return self._post_nojson(f"/endpoints/{self.endpoint_id}/docker/containers/{container_id}/{action}")

    def get_container_id(self, name):
        containers = self.list_containers(all_containers=True)
        for c in containers:
            if any(name.strip("/") == n.strip("/") for n in c["Names"]):
                return c["Id"]
        raise ValueError(f"Container '{name}' not found")

    def list_containers(self, all_containers=False):
        all_flag = "1" if all_containers else "0"
        return self._get(f"/endpoints/{self.endpoint_id}/docker/containers/json?all={all_flag}")

    def get_container_status(self, name):
        container_id = self.get_container_id(name)
        details = self._get(f"/endpoints/{self.endpoint_id}/docker/containers/{container_id}/json")
        return details["State"]

    def get_container_logs(self, name, lines=50):
        container_id = self.get_container_id(name)
        logs = self._get(f"/endpoints/{self.endpoint_id}/docker/containers/{container_id}/logs?stdout=1&stderr=1&tail={lines}")
        if isinstance(logs, list):
            logs = "".join(logs)
        return logs

    def start_container(self, name):
        container_id = self.get_container_id(name)
        return self._post_action(container_id, "start")

    def stop_container(self, name):
        container_id = self.get_container_id(name)
        return self._post_action(container_id, "stop")

    def restart_container(self, name):
        container_id = self.get_container_id(name)
        return self._post_action(container_id, "restart")

    def deploy_latest_image(self, name):
        container_id = self.get_container_id(name)
        details = self._get(f"/endpoints/{self.endpoint_id}/docker/containers/{container_id}/json")
        image_name = details["Config"]["Image"]

        # Pull new image with extended timeout (5 minutes)
        self._post_nojson(
            f"/endpoints/{self.endpoint_id}/docker/images/create?fromImage={image_name}",
            timeout=300
        )

        # Stop and remove container
        self.stop_container(name)
        r = requests.delete(
            f"{self.base_url}/endpoints/{self.endpoint_id}/docker/containers/{container_id}?force=1",
            headers=self.headers,
            timeout=30
        )
        r.raise_for_status()

        config = details["Config"]
        host_config = details.get("HostConfig", {})

        # Preserve volume binds and other HostConfig settings to keep container config intact
        create_payload = {
            "Image": image_name,
            "Cmd": config.get("Cmd"),
            "Env": config.get("Env"),
            "ExposedPorts": config.get("ExposedPorts"),
            "HostConfig": {
                "Binds": host_config.get("Binds", []),
                "PortBindings": host_config.get("PortBindings", {}),
                "RestartPolicy": host_config.get("RestartPolicy", {}),
                "NetworkMode": host_config.get("NetworkMode", ""),
            },
            "Labels": config.get("Labels"),
            "WorkingDir": config.get("WorkingDir"),
            "Entrypoint": config.get("Entrypoint"),
        }

        self._post(f"/endpoints/{self.endpoint_id}/docker/containers/create?name={name}", json=create_payload, timeout=30)
        self.start_container(name)

        return f"✅ Container '{name}' updated with latest image"


portainer = PortainerAPI(PORTAINER_URL, USERNAME, PASSWORD)


def register_tools(mcp):
    @mcp.tool()
    def test_portainer_connection() -> str:
        """Test connection to Portainer and return the endpoint ID."""
        return f"Connected to Portainer. Endpoint ID: {portainer.endpoint_id}"

    @mcp.tool()
    def list_containers(all_containers: bool = False) -> str:
        """List containers, optionally including stopped ones."""
        containers = portainer.list_containers(all_containers)
        return "\n".join([f"{', '.join(c['Names'])} | {c['Status']}" for c in containers])

    @mcp.tool()
    def get_container_status(container_name: str) -> str:
        """Get the state/status of a specific container."""
        state = portainer.get_container_status(container_name)
        return str(state)

    @mcp.tool()
    def get_container_logs(container_name: str, lines: int = 50) -> str:
        """Fetch last N lines of logs from a container."""
        return portainer.get_container_logs(container_name, lines)

    @mcp.tool()
    def restart_container(container_name: str) -> str:
        """Restart the specified container."""
        portainer.restart_container(container_name)
        return f"🔄 Container '{container_name}' restarted"

    @mcp.tool()
    def stop_container(container_name: str) -> str:
        """Stop the specified container."""
        portainer.stop_container(container_name)
        return f"🛑 Container '{container_name}' stopped"

    @mcp.tool()
    def start_container(container_name: str) -> str:
        """Start the specified container."""
        portainer.start_container(container_name)
        return f"▶ Container '{container_name}' started"

    def deploy_latest_background(container_name):
        try:
            portainer.deploy_latest_image(container_name)
            print(f"✅ Update of container '{container_name}' completed successfully")
            # Optional: update status or send notification here
        except Exception as e:
            print(f"❌ Error updating container '{container_name}': {e}")

    @mcp.tool()
    def deploy_latest(container_name: str) -> str:
        """Start updating the container with the latest image asynchronously."""
        thread = threading.Thread(target=deploy_latest_background, args=(container_name,))
        thread.start()
        return f"🚀 Update of container '{container_name}' started in background"
