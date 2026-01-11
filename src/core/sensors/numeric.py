from typing import Optional
from core import DeviceProperty

class Numeric(DeviceProperty):
    """
    Represents a numeric property of a Home Assistant device.
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)
        self.type: type = float
        self.unit: str = ""
        self.device_class: str = None

    def _copy_metadata_to(self, other: "Numeric") -> "Numeric":
        super()._copy_metadata_to(other)
        other.type = self.type
        other.unit = self.unit
        return other
    
    def discovery_payload(self, device) -> dict:
        """
        Return metadata for numeric entity.
        """
        payload = {
            "name": self.display_name or self._name,
            "p": "sensor",
            "unit_of_measurement": self.unit,
            "state_topic": f"{device.root_topic}/{device.device_id}/{self._name.lower()}/state",
            "unique_id": f"{device.device_id}_{self._name.lower()}",
        }

        if self.device_class:
            payload["device_class"] = self.device_class

        return payload

def numeric(unit: str = "", display_name: str = "", device_class: str = None):
    """
    Decorator to define a numeric property.
    """
    def decorator(func):
        prop = Numeric(func)
        prop.unit = unit
        prop.display_name = display_name
        prop.device_class = device_class
        return prop
    return decorator