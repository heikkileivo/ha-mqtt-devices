"""Number sensor property for Home Assistant devices."""


from typing import Optional
from core import DeviceProperty

class Number(DeviceProperty):
    """
    Represents a numeric property of a Home Assistant device.
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)
        self.type: type = int
        self.unit: str = ""
        self.min: Optional[float] = None
        self.max: Optional[float] = None
        self.step: Optional[float] = None

    def _copy_metadata_to(self, other: "Number") -> "Number":
        super()._copy_metadata_to(other)
        other.type = self.type
        other.unit = self.unit
        other.min = self.min
        other.max = self.max
        other.step = self.step
        return other

    def discovery_payload(self, device) -> dict:
        """
        Return metadata for number entity.
        """
        payload = {
            "name": self.display_name or self._name,
            "p": "number",
            "unit_of_measurement": self.unit,
            "state_topic": f"{device.root_topic}/{device.device_id}/{self._name.lower()}/state",
            "unique_id": f"{device.device_id}_{self._name.lower()}",
        }
        if self.is_read_only is False:
            payload["command_topic"] = f"{device.root_topic}/{device.device_id}/{self._name.lower()}/set"
        if self.min is not None:
            payload["min"] = self.min
        if self.max is not None:
            payload["max"] = self.max
        if self.step is not None:
            payload["step"] = self.step
        return payload

def number(value_type: type = int,
           display_name: str = "",
           unit: str = "",
           min_value: Optional[float] = None, 
           max_value: Optional[float] = None, 
           step: Optional[float] = None):
    """
    Decorator to define a numeric property.
    """
    def decorator(func):
        prop = Number(func)
        prop.display_name = display_name
        prop.type = value_type
        prop.unit = unit
        prop.min = min_value
        prop.max = max_value
        prop.step = step
        return prop
    return decorator