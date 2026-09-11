"""Device Manager for handling multiple devices."""
import asyncio
import json
from typing import Dict
from .device import Device

class DeviceManager:
    """
    Manages multiple devices.
    """
    # Delay between re-sending discovery and states after Home Assistant comes online,
    # so that the entities have been set up and subscribed before their states arrive.
    STATE_REPUBLISH_DELAY = 5.0

    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.subscriptions = {}
        self.mqtt_client = None

    def add_device(self, device: Device):
        """Add a device to the manager."""
        device.manager = self
        self.devices[device.device_id] = device

    def get_device(self, device_id: str) -> Device:
        """Retrieve a device by its ID."""
        return self.devices.get(device_id)

    def remove_device(self, device_id: str):
        """Remove a device from the manager."""
        if device_id in self.devices:
            device = self.devices[device_id]
            device.manager = None
            del self.devices[device_id]


    def subscribe_all(self):
        """Subscribe to all device topics."""
        if self.mqtt_client is None:
            return
        for device in self.devices.values():
            # Subscribe to device topics
            for topic, setter in device.subscriptions:
                self.subscriptions[topic] = setter
                self.mqtt_client.subscribe(topic)

        # Home Assistant publishes its birth message to <discovery_prefix>/status when it (re)starts
        for prefix in {device.discovery_prefix for device in self.devices.values()}:
            topic = f"{prefix}/status"
            self.subscriptions[topic] = self.handle_home_assistant_status
            self.mqtt_client.subscribe(topic)

    def handle_home_assistant_status(self, payload: str):
        """Re-send discovery and states when Home Assistant comes online, as states are not retained."""
        if payload != "online":
            return
        print("Home Assistant is online, re-publishing discovery topics and states.")
        self.publish_discovery_topics()
        asyncio.get_running_loop().call_later(self.STATE_REPUBLISH_DELAY, self.publish_all)

    def publish_discovery_topics(self):
        """Publish all discovery topics."""
        if self.mqtt_client is None:
            return
        for device in self.devices.values():
            # Publish discovery payloads
            topic = device.discovery_topic
            payload = json.dumps(device.discovery_payload)
            self.mqtt_client.publish(topic, payload, qos=0, retain=True)

    def handle_message(self, msg):
        """Handle incoming MQTT messages."""
        setter = self.subscriptions.get(msg.topic, None)
        if setter:
            setter(msg.payload.decode())

    def publish_all(self):
        """Publish all device payloads."""
        if self.mqtt_client is None:
            return
        try:
            for device in self.devices.values():
                for topic, payload in device.payloads:
                    self.mqtt_client.publish(topic, str(payload), qos=0, retain=False)
        except Exception as e:
            print(f"Error publishing payloads: {e}")