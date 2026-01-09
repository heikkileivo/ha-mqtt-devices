from typing import Optional
from core import DeviceProperty

class Temperature(DeviceProperty):
    """
    Represents a temperature property of a Home Assistant device.
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)
        self.type: type = float
        self.unit: str = "°C"

    def _copy_metadata_to(self, other):
        super()._copy_metadata_to(other)
        other.type = self.type
        other.unit = self.unit
        return other

    def discovery_payload(self, device) -> dict:
        """
        Return discovery payload for temperature entity.
        """
        return {
            "name": self.display_name or self._name,
            "p": "sensor",
            "unit_of_measurement": self.unit,
            "device_class": "temperature",
            "state_topic": f"{device.root_topic}/{device.device_id}/{self._name.lower()}/state",
            "unique_id": f"{device.device_id}_{self._name.lower()}",
        }

def temperature(unit: str = "°C", display_name: Optional[str] = None):
    """
    Decorator to define a temperature property.
    """
    def decorator(func):
        prop = Temperature(func)
        prop.unit = unit
        prop.display_name = display_name
        return prop
    return decorator