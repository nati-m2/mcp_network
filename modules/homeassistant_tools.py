import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()
from typing import Optional, Dict, Any, List

# הגדרת פרמטרים גלובליים
HOMEASSISTANT_URL = os.getenv('HOMEASSISTANT_URL')
HOMEASSISTANT_TOKEN = os.getenv('HOMEASSISTANT_TOKEN')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENTITIES_MAP_FILE = os.path.join(BASE_DIR, 'entities_map.json')

HEADERS = {
    "Authorization": f"Bearer {HOMEASSISTANT_TOKEN}",
    "Content-Type": "application/json"
}

if not HOMEASSISTANT_URL or not HOMEASSISTANT_TOKEN:
    print("Error: Missing HOMEASSISTANT_URL or HOMEASSISTANT_TOKEN environment variables.")
    exit(1)

def register_tools(mcp):

    @mcp.tool()
    def get_home_assistant_entity_state(entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the current state of a specific Home Assistant entity.
        This can be used to get the status of a light, the temperature of a sensor, etc.

        :param entity_id: The full entity ID (e.g., "light.living_room", "sensor.kitchen_temperature").
        :returns: A dictionary containing the entity's state data, or None if an error occurred.
        """
        try:
            url = f"{HOMEASSISTANT_URL}/api/states/{entity_id}"
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting state: {e}")
            return None


    @mcp.tool()
    def getDeviceClass(entity_id: str) -> Optional[str]:
        """
        Retrieves the Home Assistant domain from a given entity ID.

        This tool is essential for identifying the type of device
        (e.g., 'light', 'switch') before performing a service call.
        For example, for 'light.bedroom_lamp', it returns 'light'.

        :param entity_id: The ID of the entity (e.g., 'light.living_room').
        :returns: The domain of the entity as a string, or None if the ID is invalid.
        """
        if not isinstance(entity_id, str):
            return None
        parts = entity_id.split('.')
        if len(parts) > 1:
            return parts[0]
        return None


    @mcp.tool()
    def getAllEntities() -> List[Dict[str, Any]]:
        """
        Retrieves a complete list of all configured Home Assistant entities.

        This is the primary tool for the AI to get a full overview of all
        available devices, including their names, aliases, rooms, and types.
        The AI should use this to find the correct entity ID before performing
        an action.

        :returns: A list of dictionaries, where each dictionary represents an entity.
        """
        print(f"ENTITIES_MAP_FILE: {ENTITIES_MAP_FILE}")
        try:
            with open(ENTITIES_MAP_FILE, encoding='utf-8') as f:
                entities = json.load(f)
            return entities
        except (FileNotFoundError, json.JSONDecodeError):
            # במקרה של שגיאה, תחזיר רשימה ריקה
            print(f"Error: Could not find or read the file at {ENTITIES_MAP_FILE}")
            return []


    @mcp.tool()
    def send_home_assistant_service_call(domain: str, service: str, service_data: Dict[str, Any]) -> str:
        """
        Calls a Home Assistant service to control a device.

        This tool is used to turn on/off devices, set temperatures, play media, etc.
        The 'service_data' parameter must be a dictionary containing the 'entity_id'
        and any other service-specific data.

        :param domain: The service domain (e.g., "light", "climate").
        :param service: The service name (e.g., "turn_on", "set_temperature").
        :param service_data: A dictionary with service-specific data (e.g., {"entity_id": "light.living_room"}).
        :returns: A string indicating the status of the service call.
        """
        url = f"{HOMEASSISTANT_URL}/api/services/{domain}/{service}"

        try:
            response = requests.post(
                url,
                headers=HEADERS,
                data=json.dumps(service_data)
            )
            response.raise_for_status()
            return f"Service call {domain}.{service} sent successfully. Response: {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Error sending service call: {e}"