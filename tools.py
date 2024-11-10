import serial
import subprocess
import re
import json
import os
import numpy as np
from config_loader import CfgLoader
from aquasuite_plugin import get_sensors_data_aquasuite

config = CfgLoader("config.json")
temps = CfgLoader("temps.json")

if os.name == "posix":
    SERIAL_PORT = config.get_data()["serial_port_linux"]
elif os.name == "nt":
    SERIAL_PORT = config.get_data()["serial_port_windows"]
else:
    SERIAL_PORT = config.get_data()["serial_port_linux"] # default to posix path

# SERIAL_PORT = "/dev/ttyACM0"
pattern = re.compile(r'^(.*?):\s+([^\s]+)')

def get_temp_dict():
    curve_dict = {int(key): value for key, value in temps.get_data().items()}
    curve_dict[0] = 0
    curve_dict[100] = 100
    return curve_dict

def parse_sensors_data(sensors_data):
    # Define a regex pattern to capture the key and value

    # Create an empty dictionary to store the key-value pairs
    data_dict = {}

    # Iterate through each line in the sensors_data
    for line in sensors_data.splitlines():
        # Apply the regex pattern to each line
        match = pattern.match(line.strip())
        if match:
            # Extract key and value from the regex groups
            key = match.group(1).strip()
            value = match.group(2).strip()
            # Store the key-value pair in the dictionary
            data_dict[key] = value

    return data_dict

def get_sensors_data():
    try:
        # Run the sensors command and capture the output
        if os.name == "posix":
            result = subprocess.run(['sensors'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)["Coolant temp"][1:-2]
        elif os.name == "nt":
            result = get_sensors_data_aquasuite()
            # print("Windows sensor data not implemented")
            return result
        # Return the output of the command

        return parse_sensors_data(result.stdout)
    except subprocess.CalledProcessError as e:
        # Handle the error if the command fails
        print(f"An error occurred: {e}")
        return None

def set_fan_speed(speed:int):
    try:
        pico_serial = serial.Serial(SERIAL_PORT, baudrate=115200, timeout=1)
    except serial.serialutil.SerialException:
        print("Controller not detected")
    else:
        if 0 <= speed <= 100:
            pico_serial.write(f"{speed}\n".encode('utf-8'))
            # print(f"Sent speed: {speed}%")
        else:
            print("Please enter a value between 0 and 100.")
        pico_serial.close()

def calculate_fan_speed(temperature):
    # Get the temperature-to-fan-speed dictionary
    temp_dict = get_temp_dict()
    if temp_dict is not None:
        x_values = np.array(sorted(temp_dict.keys()))
        y_values = np.array([temp_dict[x] for x in x_values])
        if temperature < x_values.min() or temperature > x_values.max():
            raise ValueError("x is out of bounds of the given data points.")

        # Perform linear interpolation
        y = np.interp(temperature, x_values, y_values)
        return int(y)

    return None