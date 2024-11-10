# import tkinter as tk
# from tkinter import ttk
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import pystray
from pystray import MenuItem as item
import threading
from config_loader import CfgLoader
import subprocess

class DraggablePoint:
    def __init__(self, point, update_callback, get_prev_and_next_callback):
        self.point = point
        self.press = None
        self.update_callback = update_callback
        self.get_prev_and_next_callback = get_prev_and_next_callback

        self.cid_press = point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.point.axes:
            return
        contains, _ = self.point.contains(event)
        if not contains:
            return
        self.press = (self.point.center[0], self.point.center[1], event.xdata, event.ydata)

    def on_motion(self, event):
        # print(self.get_prev_and_next_callback())
        if self.press is None:
            return
        if event.inaxes != self.point.axes:
            return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.point.center = (x0 + dx, y0 + dy)
        self.update_callback()  # Update the curve in real-time
        self.point.figure.canvas.draw()

    def on_release(self, event):
        self.press = None
        self.update_callback()
        self.point.figure.canvas.draw()

    def disconnect(self):
        self.point.figure.canvas.mpl_disconnect(self.cid_press)
        self.point.figure.canvas.mpl_disconnect(self.cid_release)
        self.point.figure.canvas.mpl_disconnect(self.cid_motion)

class FanCurveApp():
    def __init__(self, sensor_signal, tray_sensors=[]):
        # super().__init__()
        # self.withdraw()
        # self.title("Fan Curve Creator")
        # self.geometry("660x550")
        # self.iconbitmap("fan.ico")
        self.temps = CfgLoader("temps.json")
        self.tray_sensors = tray_sensors
        self.running = True
        self.sensor_signal_cb = sensor_signal
        self.sensor_signal_cb.connect(self.set_sensor_value)

        # Data storage
        self.points = []
        # Create UI elements
        # self.create_widgets()
        # Load existing config if it exists
        # self.load_existing_config()
        # self.resizable(False, False)

        # Handle window close event
        # self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Tray icon setup
        # self.icon_image = self.create_image()
        for sensor_name, sensor_color in self.tray_sensors:
            sensor_image = self.create_sharp_tray_icon(text="", color=sensor_color, bg_color=(255, 255, 255, 0))
            sensor_icon = pystray.Icon("", sensor_image, sensor_name)
            setattr(self, f"{sensor_name}_color",  sensor_color)
            setattr(self, f"{sensor_name}_icon_thread", threading.Thread(target=sensor_icon.run, daemon=True))
            setattr(self, f"{sensor_name}_icon", sensor_icon)
            getattr(self, f"{sensor_name}_icon_thread").start()

        self.icon_image = Image.open("fan.ico")
        self.tray_icon = pystray.Icon("", self.icon_image, "Fan Curve Editor", self.create_menu())
        self.tray_icon_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_icon_thread.start()

        # self.mainloop()

    def set_sensor_value(self, sensor:str, value:str):
        if hasattr(self, f"{sensor}_icon"):
            if not isinstance(value, str):
                value = str(value)
            icon = getattr(self, f"{sensor}_icon")
            icon.icon = self.create_sharp_tray_icon(text=value, color=getattr(self, f"{sensor}_color"), bg_color=(255, 255, 255, 0))
            icon.update_menu()

    # def create_widgets(self):
    #     # Add Point button
    #     self.add_button = ttk.Button(self, text="Add Point", command=lambda: self.add_point(50, 50))
    #     self.add_button.grid(row=0, column=0, padx=10, pady=10)

    #     # Export button
    #     self.export_button = ttk.Button(self, text="Apply and Save Curve", command=self.export_curve)
    #     self.export_button.grid(row=0, column=1, padx=10, pady=10)

    #     # Figure for plotting
    #     self.fig, self.ax = plt.subplots()
    #     self.ax.set_xlim(0, 100)
    #     self.ax.set_ylim(0, 100)
    #     self.ax.set_xlabel("Temperature (°C)")
    #     self.ax.set_ylabel("Fan Speed (%)")
    #     self.ax.set_title("Fan Speed vs. Temperature Curve")
    #     self.ax.grid(True)

    #     self.canvas = FigureCanvasTkAgg(self.fig, master=self)
    #     self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=4, padx=10, pady=10)

    #     # Plot any loaded points
    #     self.update_curve()

    def add_point(self, x, y):
        # Add a point at the specified location
        point = plt.Circle((x, y), 2, color='blue', fill=True)
        self.ax.add_patch(point)
        self.points.append(DraggablePoint(point, self.update_curve, lambda: self.get_prev_and_next_point(point)))

        self.update_curve()

    def get_prev_and_next_point(self, point:DraggablePoint):
        index = self.points.index(point)
        prev = None
        next = None
        try:
            prev = self.points[index-1]
        except:
            pass

        try:
            next = self.points[index+1]
        except:
            pass

        return prev, next

    def update_curve(self):
        # Clear the current line but not the points or grid
        if hasattr(self, 'curve_line'):
            self.curve_line.remove()

        # Get all points and sort by x (temperature)
        points = [(p.point.center[0], p.point.center[1]) for p in self.points]
        points.sort()

        # Unpack the points
        if len(points) > 1:
            x, y = zip(*points)
            self.curve_line, = self.ax.plot(x, y, 'bo-', label="Fan Curve")

        self.canvas.draw()

    def export_curve(self):
        # Export the points to a dictionary
        curve_dict = {int(p.point.center[0]): int(p.point.center[1]) for p in self.points}

        # Save the dictionary to a config.json file
        self.temps.save(curve_dict)
        # with open('config.json', 'w') as f:
        #     json.dump(curve_dict, f)

    def get_curve_data(self):
        return self.temps.get_data()

    # def load_existing_config(self):
    #     # Load points from config.json if it exists
    #     if self.temps.get_data() is not None:
    #         for temp, speed in self.temps.data.items():
    #             self.add_point(int(temp), int(speed))

    def on_closing(self):
        # self.withdraw()  # Hide the window instead of closing it
        self.tray_icon.visible = True  # Show the tray icon

    def show_window(self, icon, item):
        # self.deiconify()  # Show the window
        def helper_func():
            self.tray_icon.visible = False  # Hide the tray icon
            command = ["pwm_control_wpf.exe"]
            for key, value in self.temps.data.items():
                command.append(str(key))
                command.append(str(value))
            process = subprocess.Popen(command)
            process.wait()
            self.tray_icon.visible = True  # Show the tray icon

        worker = threading.Thread(target=helper_func, daemon=True)
        worker.start()

    def quit_app(self, icon, item):
        self.tray_icon.stop()  # Stop the tray icon
        for sensor_name, sensor_color in self.tray_sensors: # stop sensor tray icons
            getattr(self, f"{sensor_name}_icon").stop()
        self.running = False

        # print("quitting")
        # self.destroy()  # Destroy the Tkinter window

    def set_tray_title(self, title):
        if hasattr(self, "tray_icon"):
            self.tray_icon.title = title

    def create_image(self, width=64, height=64, color1="black", color2="white"):
        # Generate an icon image for the tray
        image = Image.new("RGB", (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 2, 0, width, height // 2), fill=color2
        )
        dc.rectangle(
            (0, height // 2, width // 2, height), fill=color2
        )
        return image

    def create_menu(self):
        # Create a menu for the tray icon
        return pystray.Menu(
            item('Show', self.show_window),
            item('Quit', self.quit_app)
        )

    def create_sharp_tray_icon(self, text, color=(0, 0, 0), bg_color=(255, 255, 255, 0), icon_size=(16, 16), font_path=None):
        """
        Create a sharp image for use as a tray icon with the given text.

        :param text: The string to be displayed on the icon.
        :param color: The color of the text as an (R, G, B) tuple.
        :param bg_color: The background color of the icon as an (R, G, B, A) tuple.
        :param icon_size: The size of the final icon as a (width, height) tuple.
        :param font_path: Path to a .ttf or .otf font file. If None, the default font is used.
        :return: A Pillow Image object with the text.
        """
        # Create an image with the given background color
        image = Image.new('RGBA', icon_size, bg_color)

        # Set up the drawing context
        draw = ImageDraw.Draw(image)

        # Use a basic font and set the font size
        font_size = icon_size[1]  # Full height of the icon
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default(12)

        # Calculate the bounding box of the text
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate position to center the text
        position = (
            (icon_size[0] - text_width) // 2,  # Center horizontally
            (icon_size[1] - text_height) // 2 - 2  # Center vertically
        )

        # Draw the text
        draw.text(position, text, fill=color, font=font)

        return image