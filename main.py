from view import FanCurveApp
from tools import *
import threading
from time import sleep
from tk_signal import Signal

sensor_signal = Signal(str, str)

def apply_fan_speed():
    while True:
        sensor_values = get_sensors_data()
        if sensor_values is not None:
            water_temp = int(float(sensor_values))
            # water_flow = int(sensor_values["Flow [dL/h]"])
            # print(water_temp, water_flow, print())
            fan_speed = calculate_fan_speed(water_temp)
            print("settings fan speed to:" + str(fan_speed))
            sensor_signal.emit("Fan Speed", f"{fan_speed}")
            sensor_signal.emit("Water Temperature", f"{water_temp}")
            set_fan_speed(fan_speed)
        sleep(3)

if __name__ == "__main__":
    fan_speed_worker = threading.Thread(target=apply_fan_speed, daemon=True)
    fan_speed_worker.start()
    app = FanCurveApp(sensor_signal, [("Water Temperature", (115, 222, 80)), ("Fan Speed", (219, 125, 42))])
    while app.running:
        sleep(1)
    # app.mainloop()
