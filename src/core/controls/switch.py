"""Switch control implementation."""

from core import DeviceProperty

class Switch(DeviceProperty):
    """
    Represents a boolean property of a Home Assistant device.
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)
        self.type: type = bool

    def _copy_metadata_to(self, other: "Switch") -> "Switch":
        super()._copy_metadata_to(other)
        other.type = self.type
        return other
    
    def serialize(self, value):
        return "ON" if value else "OFF"
    
    def parse(self, value: str):
        return value.upper() == "ON"

    def discovery_payload(self, device) -> dict:
        """
        Return metadata for boolean entity.
        """
        payload = {
            "name": self.display_name or self._name,
            "p": "switch",
            "state_topic": f"{device.root_topic}/{device.device_id}/{self._name.lower()}/state",
            "unique_id": f"{device.device_id}_{self._name.lower()}",
        }
        if self.is_read_only is False:
            payload["command_topic"] = f"{device.root_topic}/{device.device_id}/{self._name.lower()}/set"
        return payload

def switch(display_name: str = ""):
    """
    Decorator to define a boolean property.
    """
    def decorator(func):
        prop = Switch(func)
        prop.display_name = display_name
        return prop
    return decorator