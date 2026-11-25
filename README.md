# Circuit Temp Trigger

DC circuit analysis (nodal analysis) with a temperature trigger.

## Files
- circuit_analysis.py: solves a DC circuit, checks KCL and power balance, draws a node graph
- temp_trigger.py: runs circuit_analysis.py when temperature reaches 35 C

## Install
pip install numpy networkx matplotlib pyserial

## Usage
python temp_trigger.py

Modes: 1) Manual input, 2) Simulated auto, 3) Serial sensor (Arduino)
