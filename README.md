SpaceDrive
==========

A space game engine built on top of Panda3D and the Sandbox entity component system library.

# Installation

SpaceDrive can be installed via pip. Sandbox (currently) has to be manually installed as well:

```
pip2 install git+https://github.com/croxis/sandbox.git
pip2 install git+https://github.com/croxis/SpaceDrive.git
```

# Quick Start

To begin using SpaceDrive, import it and initialize with your desired log level.
init() must be called before any other systems can be initiated.

```python
import spacedrive

if __name__ == '__main__':
    # Configure any panda prc settings here
    spacedrive.init(log_level='info', window_title='SpaceDrive Demo')
    # Initiate the game loop.
    spacedrive.run()
```
    
# Use

SpaceDrive is designed with a client-server model in mind. init() accepts run_client and run_server variables.
If run_client is set to false SpaceDrive will run in windowless mode.

# Features

SpaceDrive comes with a number of built in systems to serve a spaceship game. Features are enabled by calling their respective init functions. Custom systems and the component class they listen for can be passed in the init functions to override default behaviors.

```python
import spacedrive

if __name__ == '__main__':
    # Configure any panda prc settings here
    spacedrive.init(log_level='info', window_title='SpaceDrive Demo')
    
    # Multipass physical based rendering based on Tobias work.
    # To use an alternative render system use spacedrive.init_graphics(system=CustomEntitySystem, CustomComponent) instead
    spacedrive.init_graphics()
    
    # Client netcode system. No default system or component provided (yet)
    spacedrive.init_client(system, component, address, port)
    
    # Server netcode system. No default system or component provided (yet)
    spacedrive.init_server(system, component, address, port)
    
    # Uses cefpython for html/css/javascript gui. This feature is not complete.
    spacedrive.init_gui()
     
    # Implements planet and moon orbit engine. Default provides realistic celestial movement using the 6 kepler variables
    spacedrive.init_orbits()
    
    # Implements ridged body physics using bullet that utilizes a cube grid system. A floating grid similar to CCP EVE Online is also planned.
    spacedrive.init_physics()
    
    # Add a custom SandBox EntitySystem
    spacedrive.init_system(system, component)
    
    # Initiate the game loop.
    spacedrive.run()
```
