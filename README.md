# Python Framework for Roboy's LightSkin
### Analysis, Simulation and Reconstruction for a pressure sensitive silicone skin based on optical 2D-Waveguides

This project is for simulating and testing reconstruction algorithms etc...  
It provides different libraries for reconstruction, visualization in tkinter etc...

Most of these functions access the sensor and LED arrangements defined in `sensors.csv` and `leds.csv`.
Some of them also use the sample translucency map provided in `translucency.csv`

The functions of these libraries are used in different scripts as listed below

## Dependencies
 * python3
 * numpy
 * scipy
 * pyserial (for Arduino connection)
 * matplotlib (currently only for color maps)

## Available scripts

### `simulator.py`
This script tests different reconstruction algorithms on the current set of LEDs and Sensors.
It uses the provided translucency values as ground truth for simulation.

### `visualizer.py`
This script connects to an Arduino running the Arduino connector script and
displays the collected and reconstructed data.
With every frame, it will update live.
The first frame received is used as calibration data.

### `analyzer.py`
This script displays useful maps for the current sensor placements:
 * Sensitivity map  
   The summed influences of the cells on all rays; allows to see which cells cannot be measured