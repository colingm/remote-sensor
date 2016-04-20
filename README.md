# Spectral Point Sensor

## Overview
This repository contains all of the code needed for the spectral point sensor we designed. It is broken down into two 
main folders: the transmitter and the receiver. You will also find a 3D model used to print a container for the XBee
receiver module and the developer's board that it is connected to.

### Transmitter
The transmitter folder contains all of the files needed for the FRDM board and the Arduino. This includes the code 
to read from the GPS, the temperature sensor, and the spectrometer. It also has the necessary code to send this 
data to the receiver via the XBee PRO 900HP RF module. All of this code is in C/C++ and will be for either the FRDM
board or the Arduino. To use the FRDM code just import it into the MBED compiler on the web and compile it to your
device. For the Arduino code just install it to an Arduino like you would with any other project.

### Receiver
The receiver folder holds the Python code necessary to open a serial communication with the XBee receiver and to
read the packets of data being sent to it. There are only a few files that are needed for this to work. These files
use a few libraries that will need to be installed using PIP prior to running the code. This includes "matplotlib",
"numpy", and "pyserial". To run this code simply call `python xbee_main.py <Serial Port>`

