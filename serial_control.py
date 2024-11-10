import serial

# Replace 'COM3' with the correct port where your ESP8266 is connected
serial_port = 'COM5'
baud_rate = 115200

try:
    # Initialize serial connection
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
except serial.SerialException as e:
    print(f"Could not open port {serial_port}: {e}")
    exit()

def set_fan_speed(speed):
    if 0 <= speed <= 1023:
        ser.write(f"{speed}\n".encode())
        response = ser.readline().decode('utf-8').strip()
        print("@@@", response)
    else:
        print("Speed must be between 0 and 1023.")

try:
    while True:
        user_input = input("Enter fan speed (0-1023): ")
        if user_input.isdigit():
            set_fan_speed(int(user_input))
        else:
            print("Please enter a valid number.")

except KeyboardInterrupt:
    print("Exiting program.")

finally:
    ser.close()
