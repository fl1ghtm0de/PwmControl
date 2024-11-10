from machine import Pin, PWM
import sys

# Define the GPIO pin that will output the PWM signal
pwm_pin = Pin(15)  # Use GPIO 15, or another GPIO pin if needed
pwm = PWM(pwm_pin)
pwm.freq(25000)  # Set frequency to 25kHz

def set_fan_speed(duty_cycle):
    if 0 <= duty_cycle <= 100:
        pwm.duty_u16(int(duty_cycle * 65535 / 100))
    else:
        print("Duty cycle out of range")

# Main loop to listen for incoming serial commands
while True:
    try:
        line = sys.stdin.readline().strip()
        if line:
            duty_cycle = int(line)
            print(f"Setting fan speed to {duty_cycle}%")
            set_fan_speed(duty_cycle)
    except ValueError:
        print("Invalid input received")
    except Exception as e:
        print(f"Error: {e}")
