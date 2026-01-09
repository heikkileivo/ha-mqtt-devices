# Home Assistant MQTT Devices
This project provides a declarative Python framework for defining MQTT devices and Home Assistant discovery entities.
Specific device implementations (such as Vallox ventilation units) are provided as examples.

The original intent of this project was to create a Home Assistant device for 
[Vallox 150 SE](https://www.vallox.com/en/product/vallox-150-effect-se/) home ventilator. The actual interface for the ventilator
is direct Python port from [ValloxEsp serial interface](https://github.com/kotope/valloxesp/tree/master) by [@kotope](https://github.com/kotope).

While developing the implementation it was evident that the project needs clean separation between concerns such as startup/shutdown,
MQTT connection, device discovery and actual device communication. As a result, I ended up implementing basic, declarative syntax for generic Home Assistant devices.
The main module loads and instantiates devices defined in an environment variable, so it should be easy to implement new devices using this approach.

The goal of the project is to implement property declarations for commonly used Home Assistant entities, and the work is in progress.
