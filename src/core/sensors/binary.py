"""Binary sensor implementation for Home Assistant devices."""

from core import DeviceProperty
class Binary(DeviceProperty):
    """
    Represents a binary (on/off) property of a Home Assistant device.
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)
        self.type: type = bool
        self.device_class: str = None

    def _copy_metadata_to(self, other: "Binary") -> "Binary":
        super()._copy_metadata_to(other)
        other.type = self.type
        return other
    
    def serialize(self, value):
        return "ON" if value else "OFF"
    
    def parse(self, value: str):
        return value.upper() == "ON"

    def discovery_payload(self, device) -> dict:
        """
        Return metadata for binary sensor entity.
        """
        payload = {
            "name": self.display_name or self._name,
            "p": "binary_sensor",
            "state_topic": f"{device.root_topic}/{device.device_id}/{self._name.lower()}/state",
            "unique_id": f"{device.device_id}_{self._name.lower()}",
        }
        if self.device_class:
            payload["device_class"] = self.device_class
        return payload

def binary(display_name: str = "", device_class: str = None):
    """
    Decorator to define a binary property.
    """
    def decorator(func):
        prop = Binary(func)
        prop.display_name = display_name
        prop.device_class = device_class
        return prop
    return decorator