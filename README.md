This software is used to make a raspberry pi pico (or easily any other microcontroller with access to gpio pins)
emit a pwm frequency to control fan speeds.

The pythonscript running as a backgroundtask provides a taskbar icon to access the Grapheditor UI (written in C# (WPF)).
Data is transmitted over a com port to the microcontroller.
Addiotionally it can read temperature data (in this case from a aquasuite high flow NEXT sensor) and apply the pwm speed in % based off this value.
