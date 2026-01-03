"""
MQTT discovery configuration for Home Assistant integration.
"""
import json
from typing import Tuple, Optional
import os
from os import environ as env


class DeviceId:
    """
    Generate and persist unique IDs for devices.
    """
    _index : int = 0
    _is_initialized : bool = False
    _ids : list[str] = []

    """ Class initializer to load existing IDs from file. """
    @classmethod
    def _initialize(cls):
        if not cls._is_initialized:
            try:
                with open("deviceids.txt", "r", encoding="utf-8") as f:
                    cls._ids = [line.strip() for line in f.readlines()]
            except FileNotFoundError:
                cls._ids = []
            cls._is_initialized = True


    @classmethod
    def get_next(cls) -> str:
        """ Get the next unique device ID. """
        if not cls._is_initialized:
           cls._initialize()
        if cls._index < len(cls._ids):
            device_id = cls._ids[cls._index]
            cls._index += 1
            return device_id
        else:
            # Generate new, random 16-digit hex ID
            new_id = f"0x{ hex(int.from_bytes(os.urandom(8), 'big'))[2:].rjust(16, '0')}"
            cls._ids.append(new_id)
            cls._index += 1
            with open("deviceids.txt", "a", encoding="utf-8") as f:
                f.write(new_id + "\n")
            return new_id
        

class DeviceProperty(property):
    """
    Represents a property of a Home Assistant device.
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)

    
    def meta(self, name: str, device) -> dict:
        """Return metadata for temperature property."""
        return {}


class Temperature(DeviceProperty):
    """
    Represents a temperature property of a Home Assistant device.
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)
        self.unit: str = "°C"

    def meta(self, name: str, device) -> dict:
        """
        Return metadata for temperature entity.
        """
        return {
            "name": name,
            "p": "sensor",
            "unit_of_measurement": self.unit,
            "device_class": "temperature",
            "value_template": f"{{{{ value_json.{name} }}}}",
            "unique_id": f"{device.device_id}_{name.lower().replace(' ', '_')}",
        }


def temperature(unit: str = "°C"):
    """
    Decorator to define a temperature property.
    """
    def decorator(func):
        prop = Temperature(func)
        prop.unit = unit
        return prop
    return decorator

class DeviceMetaclass(type):
    """
    Metaclass for Home Assistant MQTT discovery devices.
    """

    def __new__(mcs, name, bases, attrs):
        if "components" not in attrs:
            attrs["components"] = {}
        
        # Copy all DeviceProperty attributes to components
        for key, value in attrs.items():
            if isinstance(value, DeviceProperty):
                attrs["components"][key] = value

        return super().__new__(mcs, name, bases, attrs)
    


class Device(metaclass=DeviceMetaclass):
    """
    Base class for Home Assistant MQTT discovery devices.
    """
    components = {}
    def __init__(self, **kwargs):
        args = {**kwargs, **env}
        self.root_topic : str = args.get("root_topic", self.__class__.__name__.lower())
        self.discovery_prefix : str = args.get("discovery_prefix", "homeassistant")
        self.device_id : str = args.get("device_id", DeviceId.get_next())
        self.device_name : str = args.get("device_name", self.__class__.__name__)
        self.manufacturer : str = args.get("manufacturer", "Unknown")
        self.model : str = args.get("model", "Unknown")
        self.software_version : str = args.get("software_version", "1.0")
        self.serial_number : Optional[str] = args.get("serial_number", None)
        self.hardware_version : str = args.get("hardware_version", "1.0")
        self.origin: str = args.get("origin", "Unknown")
        self.support_url: str = args.get("support_url", "https://example.com/support")
        
        

    @property
    def discovery_topic(self) -> str:
        """Generate MQTT topic for Home Assistant discovery."""
        return f"{self.discovery_prefix}/device/{self.device_id}/config"

    @property
    def value_topic(self) -> str:
        """Generate MQTT topic for device state."""
        return f"{self.root_topic}/{self.device_id}/state"

    @property
    def payload(self):
        """Publish the values to mqtt server."""
        components = self.__class__.__dict__.get("components", {})
        payload =  {k: v.fget(self) for k, v in components.items()}
        return payload   

    @property
    def dict(self) -> dict:
        """Generate MQTT discovery configuration for Home Assistant."""
        dev = {"ids": f"{self.device_id}", "name": f"{self.device_name}", "mf": f"{self.manufacturer}", "mdl": f"{self.model}", "sw": f"{self.software_version}", "sn": self.serial_number, "hw": f"{self.hardware_version}"}
        o = {"name": f"{self.origin}", "sw": f"{self.software_version}", "url": f"{self.support_url}"}
        cmps = [c.meta(n, self) for n, c in self.components.items()]
        return {"dev": dev, "o": o, "cmps": cmps, "state_topic": f"{self.device_id}/state", "qos": 0 }



class TestDevice(Device):
    """
    Sample device for testing purposes.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name = "bar"
        self._temperature = 25.0

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set the name of the device."""
        self._name = value

    @temperature(unit="°C")
    def temperature(self) -> float:
        """Return the temperature value."""
        return self._temperature
    
    @temperature.setter
    def temperature(self, value: float):
        """Set the temperature value."""
        self._temperature = value
    


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    td = TestDevice(root_topic="test_devices", 
                    device_id="test_device_1")
    print(f"Temperature: {td.temperature} °C")
    print("Discovery topic:")
    print(td.discovery_topic)
    print("Discovery Config:")
    print(json.dumps(td.dict, indent=4))
    print("Value Topic:")
    print(td.value_topic)
    print("Value Payload:")
    print(json.dumps(td.payload, indent=4))

