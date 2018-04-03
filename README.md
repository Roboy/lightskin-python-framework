# Some Python Code for my Bachelor Thesis

This project is for simulating and testing reconstruction algorithms etc...  
It provides different libraries for reconstruction, visualization in tkinter etc...

Most of these functions access the sensor and LED arrangements defined in `sensors.csv` and `leds.csv`.
Some of them also use the sample translucency map provided in `translucency.csv`

The functions of these libraries are used in different scripts as listed below

## Dependencies
 * python3
 * numpy
 * scipy
 * matplotlib (currently only for color maps)

## Available scripts

### `simulator.py`
This script tests different reconstruction algorithms on the current set of LEDs and Sensors using the provided translucency values.

### `visualizer.py`
This script connects to an Arduino running the Arduino connector module and displays the collected and reconstructed data updating live.

### `analyzer.py`
This script displays various useful maps for the current sensor placements:
 * A sensitivity map
 * A locality resolution map